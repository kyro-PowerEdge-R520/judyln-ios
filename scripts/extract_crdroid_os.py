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

import bz2, lzma, shutil, struct, subprocess, zipfile
from pathlib import Path

ZIP_PATH = Path(r"C:\Users\kyro\Downloads\crDroidAndroid-16.0-20261010-judyln-v12.12.zip")
OUT_DIR = Path(r"C:\Users\kyro\Downloads\judyln-ios\crdroid")
TARGETS = {"system", "vendor"}

def decompress_zstd(raw: bytes) -> bytes:
    try:
        from compression import zstd
        return zstd.decompress(raw)
    except ImportError:
        pass
    try:
        import zstandard
        return zstandard.ZstdDecompressor().decompress(raw)
    except ImportError:
        pass
    for cmd in (["zstd", "-dc"], ["7z", "x", "-tzstd", "-so", "-si"]):
        if shutil.which(cmd[0]):
            return subprocess.run(cmd, input=raw, capture_output=True, check=True).stdout
    raise RuntimeError("ZSTD support missing: run 'pip install zstandard' and re-run.")

def read_varint(buf, pos):
    val = shift = 0
    while True:
        b = buf[pos]; pos += 1
        val |= (b & 0x7f) << shift
        if not (b & 0x80): return val, pos
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
with zipfile.ZipFile(ZIP_PATH) as zf, zf.open("payload.bin") as f:
    magic, ver, m_sz, sig_sz = struct.unpack(">4sQQI", f.read(24))
    assert magic == b"CrAU" and ver == 2
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

    handles = {p: (OUT_DIR / f"{p}.img").open("wb") for p in parts}
    jobs = []
    for pname, (ops, _) in parts.items():
        for op_type, d_off, d_len, exts in ops:
            if d_len == 0 and op_type in (6, 7):
                for sb, nb in exts:
                    handles[pname].seek(sb * block_size)
                    handles[pname].write(b"\x00" * (nb * block_size))
            elif d_len > 0:
                jobs.append((d_off, d_len, pname, op_type, exts))

    jobs.sort(key=lambda x: x[0])
    cur = 0
    for d_off, d_len, pname, op_type, exts in jobs:
        rem = d_off - cur
        while rem > 0:
            chunk = f.read(min(rem, 4 * 1024 * 1024))
            if not chunk: break
            rem -= len(chunk)
        raw = f.read(d_len)
        cur = d_off + d_len

        if op_type == 0: data = raw
        elif op_type == 1: data = bz2.decompress(raw)
        elif op_type == 8: data = lzma.decompress(raw)
        elif op_type == 11: data = decompress_zstd(raw)
        else: raise ValueError(f"Unsupported op_type {op_type} in {pname}")

        pos = 0
        out = handles[pname]
        for sb, nb in exts:
            sz = nb * block_size
            out.seek(sb * block_size)
            out.write(data[pos:pos+sz])
            pos += sz

    for pname, (_, new_sz) in parts.items():
        out = handles[pname]
        if new_sz:
            out.seek(new_sz)
            out.truncate(new_sz)
        out.close()
        actual = (OUT_DIR / f"{pname}.img").stat().st_size
        assert actual == new_sz, f"{pname}.img size mismatch: {actual} != {new_sz}"
        print(f"OK: {pname}.img -> {actual:,} bytes")
