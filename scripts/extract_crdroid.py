# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 kyro
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import bz2, hashlib, lzma, shutil, struct, subprocess, zipfile
from pathlib import Path

ZIP_PATH = Path(r"C:\Users\kyro\Downloads\crDroidAndroid-16.0-20261010-judyln-v12.12.zip")
OUT_DIR = Path(r"C:\Users\kyro\Downloads\judyln-ios\crdroid")
TARGETS = {"boot", "dtbo", "vbmeta", "vendor_boot"}

def decompress_zstd(raw: bytes) -> bytes:
    try:
        from compression import zstd  # Python 3.14+
        return zstd.decompress(raw)
    except ImportError:
        pass
    try:
        import zstandard
        return zstandard.ZstdDecompressor().decompress(raw)
    except ImportError:
        pass
    try:
        import pyzstd
        return pyzstd.decompress(raw)
    except ImportError:
        pass
    for cmd in (["zstd", "-dc"], ["7z", "x", "-tzstd", "-so", "-si"]):
        if shutil.which(cmd[0]):
            res = subprocess.run(cmd, input=raw, capture_output=True, check=True)
            return res.stdout
    raise RuntimeError("ZSTD payload detected: run 'pip install zstandard' and re-run extract_crdroid.py")

def read_varint(buf, pos):
    val = shift = 0
    while True:
        b = buf[pos]; pos += 1
        val |= (b & 0x7f) << shift
        if not (b & 0x80):
            return val, pos
        shift += 7

def iter_fields(buf):
    pos, end = 0, len(buf)
    while pos < end:
        tag, pos = read_varint(buf, pos)
        fn, wt = tag >> 3, tag & 7
        if wt == 0: val, pos = read_varint(buf, pos)
        elif wt == 1: val, pos = buf[pos:pos+8], pos + 8
        elif wt == 2:
            ln, pos = read_varint(buf, pos)
            val, pos = buf[pos:pos+ln], pos + ln
        elif wt == 5: val, pos = buf[pos:pos+4], pos + 4
        else: raise ValueError(f"Unsupported wire type {wt}")
        yield fn, wt, val

def parse_extent(buf):
    sb = nb = 0
    for fn, wt, val in iter_fields(buf):
        if fn == 1: sb = val
        elif fn == 2: nb = val
    return sb, nb

def parse_op(buf):
    op_type = d_off = d_len = 0
    exts = []
    for fn, wt, val in iter_fields(buf):
        if fn == 1: op_type = val
        elif fn == 2: d_off = val
        elif fn == 3: d_len = val
        elif fn == 4: exts.append(parse_extent(val))
    return op_type, d_off, d_len, exts

def parse_part(buf):
    name, ops, new_sz = "", [], 0
    for fn, wt, val in iter_fields(buf):
        if fn == 1: name = val.decode()
        elif fn == 7:
            for sfn, _, sval in iter_fields(val):
                if sfn == 1: new_sz = sval
        elif fn == 8: ops.append(parse_op(val))
    return name, ops, new_sz

OUT_DIR.mkdir(parents=True, exist_ok=True)
for stale in OUT_DIR.glob("*.img"):
    if stale.stat().st_size == 0:
        stale.unlink()

with zipfile.ZipFile(ZIP_PATH) as zf, zf.open("payload.bin") as f:
    magic, ver, m_sz, sig_sz = struct.unpack(">4sQQI", f.read(24))
    assert magic == b"CrAU" and ver == 2, f"Unexpected payload header: {magic} v{ver}"
    manifest = f.read(m_sz)
    f.read(sig_sz)

    block_size = 4096
    parts = {}
    for fn, wt, val in iter_fields(manifest):
        if fn == 3: block_size = val
        elif fn == 13:
            pname, ops, new_sz = parse_part(val)
            if pname in TARGETS:
                parts[pname] = (ops, new_sz)

    jobs = sorted(
        (d_off, d_len, pname, idx)
        for pname, (ops, _) in parts.items()
        for idx, (op_type, d_off, d_len, exts) in enumerate(ops)
        if d_len > 0
    )
    cur, blobs = 0, {}
    for d_off, d_len, pname, idx in jobs:
        rem = d_off - cur
        while rem > 0:
            chunk = f.read(min(rem, 1024 * 1024))
            if not chunk: break
            rem -= len(chunk)
        cur = d_off
        blobs[(pname, idx)] = f.read(d_len)
        cur += d_len

    for pname, (ops, new_sz) in parts.items():
        assert ops, f"No install operations found for {pname}"
        out_path = OUT_DIR / f"{pname}.img"
        with out_path.open("wb") as out:
            for idx, (op_type, d_off, d_len, exts) in enumerate(ops):
                raw = blobs.get((pname, idx), b"")
                if op_type == 0: data = raw
                elif op_type == 1: data = bz2.decompress(raw)
                elif op_type in (6, 7): data = b"\x00" * sum(nb * block_size for _, nb in exts)
                elif op_type == 8: data = lzma.decompress(raw)
                elif op_type == 11: data = decompress_zstd(raw)
                else: raise ValueError(f"Unsupported op_type {op_type} in {pname}")
                pos = 0
                for sb, nb in exts:
                    sz = nb * block_size
                    out.seek(sb * block_size)
                    out.write(data[pos:pos+sz])
                    pos += sz
            if new_sz and out.tell() < new_sz:
                out.truncate(new_sz)
        sz = out_path.stat().st_size
        assert sz > 0, f"{out_path} ended up 0 bytes!"
        sha = hashlib.sha256(out_path.read_bytes()).hexdigest()[:16]
        print(f"OK: {out_path.name} -> {sz:,} bytes (sha256: {sha}...)")
