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

import hashlib
import os
import re
import struct

GOLD = r"C:\Users\kyro\Downloads\judyln-ios\golden_boot\boot_a-cpu-ui-touch.img"
OUT_DIR = r"C:\Users\kyro\Downloads\judyln-ios\work\next-gen"
OUT_USB1 = os.path.join(OUT_DIR, "boot-g7em-usb1.img")
OUT_USB2 = os.path.join(OUT_DIR, "boot-g7em-usb2.img")
REPORT = os.path.join(OUT_DIR, "usb_notes.md")
GOLD_EXPECTED_SHA256 = "766a88577c208af62583d199fa5dbd8f46811342aa109db5c334a5d38607b3e7"


def sext(val, bits):
    sign = 1 << (bits - 1)
    return val - (1 << bits) if (val & sign) else val


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def calc_bootimg_v1_sha1(buf):
    ksz, _, rsz, _, ssz, _, _, pg, hver, _ = struct.unpack_from("<10I", buf, 8)
    rdtbo_sz, _, _ = struct.unpack_from("<IQI", buf, 1632)

    def align(n):
        return ((n + pg - 1) // pg) * pg

    k_off = pg
    r_off = k_off + align(ksz)
    s_off = r_off + align(rsz)
    d_off = s_off + align(ssz)

    h = hashlib.sha1()
    h.update(buf[k_off : k_off + ksz])
    h.update(struct.pack("<I", ksz))
    h.update(buf[r_off : r_off + rsz])
    h.update(struct.pack("<I", rsz))
    h.update(buf[s_off : s_off + ssz])
    h.update(struct.pack("<I", ssz))
    if hver >= 1:
        h.update(buf[d_off : d_off + rdtbo_sz])
        h.update(struct.pack("<I", rdtbo_sz))
    return h.digest()


def parse_layout(buf):
    sw = buf.find(b"SWEETXNU")
    assert sw != -1, "SWEETXNU header not found"
    ver, nsegs = struct.unpack_from("<II", buf, sw + 8)
    sw_segs = []
    for i in range(nsegs):
        vm, vs, fo, fz = struct.unpack_from("<4Q", buf, sw + 0x2A8 + i * 32)
        sw_segs.append((i, vm, vs, sw + fo, fz))

    mach_off = sw_segs[0][3]
    magic = struct.unpack_from("<I", buf, mach_off)[0]
    assert magic == 0xFEEDFACF, f"Unexpected Mach-O magic 0x{magic:x}"
    ncmds, sizeofcmds = struct.unpack_from("<II", buf, mach_off + 16)

    lc_segs = []
    symoff = nsyms = stroff = strsize = 0
    off = mach_off + 32
    for _ in range(ncmds):
        cmd, csz = struct.unpack_from("<II", buf, off)
        if cmd == 0x19:  # LC_SEGMENT_64
            segname = buf[off + 8 : off + 24].split(b"\x00", 1)[0].decode("ascii", errors="replace")
            vm, vs, fo, fz = struct.unpack_from("<4Q", buf, off + 24)
            nsects = struct.unpack_from("<I", buf, off + 64)[0]
            lc_segs.append((segname, vm, vs, fo, fz, nsects))
        elif cmd == 2:  # LC_SYMTAB
            symoff, nsyms, stroff, strsize = struct.unpack_from("<4I", buf, off + 8)
        off += csz

    # Map SWEETXNU segs by VA
    def va_to_img(va):
        for _, vm, vs, img_o, fz in sw_segs:
            if vm <= va < vm + fz:
                return img_o + (va - vm)
        return None

    def img_to_va(io):
        for _, vm, vs, img_o, fz in sw_segs:
            if img_o <= io < img_o + fz:
                return vm + (io - img_o)
        return None

    # Locate __LINKEDIT in SWEETXNU & LC_SEGMENT_64
    le_lc = [s for s in lc_segs if s[0] == "__LINKEDIT"][0]
    le_sw = [s for s in sw_segs if s[1] == le_lc[1]][0]
    le_delta = le_sw[3] - le_lc[3]
    sym_img = symoff + le_delta
    str_img = stroff + le_delta

    sym_by_va = {}
    syms_sorted = []
    for i in range(nsyms):
        n_strx, _, _, _, n_value = struct.unpack_from("<IBBHQ", buf, sym_img + i * 16)
        if n_value:
            end = buf.find(b"\x00", str_img + n_strx)
            name = buf[str_img + n_strx : end].decode("ascii", errors="replace")
            sym_by_va[n_value] = name
            syms_sorted.append((n_value, name))
    syms_sorted.sort()

    # Build function bounds
    fn_bounds = {}
    exec_seg = [s for s in lc_segs if s[0] == "__TEXT_EXEC"][0]
    exec_sw = [s for s in sw_segs if s[1] == exec_seg[1]][0]
    exec_vas = [(va, nm) for va, nm in syms_sorted if exec_sw[1] <= va < exec_sw[1] + exec_sw[4]]
    for idx, (va, nm) in enumerate(exec_vas):
        nxt = exec_vas[idx + 1][0] if idx + 1 < len(exec_vas) else exec_sw[1] + exec_sw[4]
        fn_bounds[va] = (nm, nxt - va)

    return {
        "sw": sw,
        "ver": ver,
        "nsegs": nsegs,
        "sw_segs": sw_segs,
        "lc_segs": lc_segs,
        "exec_sw": exec_sw,
        "text_sw": sw_segs[0],
        "va_to_img": va_to_img,
        "img_to_va": img_to_va,
        "sym_by_va": sym_by_va,
        "syms_sorted": syms_sorted,
        "fn_bounds": fn_bounds,
    }


def decode_arm64(va, w, sym_lookup, img_lookup, buf):
    if w == 0xD503201F:
        return "nop"
    if w == 0xD65F03C0:
        return "ret"
    if (w & 0xFC000000) in (0x14000000, 0x94000000):
        op = "bl" if (w >> 31) else "b"
        tgt = va + sext(w & 0x3FFFFFF, 26) * 4
        return f"{op} 0x{tgt:x} <{sym_lookup(tgt)}>"
    if (w & 0xFF000010) == 0x54000000:
        conds = ["eq", "ne", "cs", "cc", "mi", "pl", "vs", "vc", "hi", "ls", "ge", "lt", "gt", "le", "al", "nv"]
        tgt = va + sext((w >> 5) & 0x7FFFF, 19) * 4
        return f"b.{conds[w & 0xF]} 0x{tgt:x}"
    if (w & 0x7E000000) == 0x34000000:
        op = "cbnz" if (w & 0x01000000) else "cbz"
        rx = "x" if (w >> 31) else "w"
        tgt = va + sext((w >> 5) & 0x7FFFF, 19) * 4
        return f"{op} {rx}{w & 31}, 0x{tgt:x}"
    if (w & 0x7E000000) == 0x36000000:
        op = "tbnz" if (w & 0x01000000) else "tbz"
        bit = ((w >> 31) << 5) | ((w >> 19) & 0x1F)
        tgt = va + sext((w >> 5) & 0x3FFF, 14) * 4
        return f"{op} w{w & 31}, #{bit}, 0x{tgt:x}"
    if (w & 0x9F000000) == 0x90000000:
        page = (va & ~0xFFF) + (sext((((w >> 5) & 0x7FFFF) << 2) | ((w >> 29) & 3), 21) << 12)
        return f"adrp x{w & 31}, 0x{page:x}"
    if (w & 0x9F000000) == 0x10000000:
        tgt = va + sext((((w >> 5) & 0x7FFFF) << 2) | ((w >> 29) & 3), 21)
        return f"adr x{w & 31}, 0x{tgt:x}"
    if (w & 0x7F800000) == 0x11000000:
        sf = "x" if (w >> 31) else "w"
        sh = 12 if ((w >> 22) & 1) else 0
        rn = "sp" if ((w >> 5) & 31) == 31 else f"{sf}{(w >> 5) & 31}"
        rd = "sp" if (w & 31) == 31 else f"{sf}{w & 31}"
        return f"add {rd}, {rn}, #0x{((w >> 10) & 0xFFF) << sh:x}"
    if (w & 0x7F800000) == 0x51000000:
        sf = "x" if (w >> 31) else "w"
        sh = 12 if ((w >> 22) & 1) else 0
        rn = "sp" if ((w >> 5) & 31) == 31 else f"{sf}{(w >> 5) & 31}"
        rd = "sp" if (w & 31) == 31 else f"{sf}{w & 31}"
        return f"sub {rd}, {rn}, #0x{((w >> 10) & 0xFFF) << sh:x}"
    if (w & 0x7F800000) == 0x71000000 and (w & 31) == 31:
        sf = "x" if (w >> 31) else "w"
        sh = 12 if ((w >> 22) & 1) else 0
        return f"cmp {sf}{(w >> 5) & 31}, #0x{((w >> 10) & 0xFFF) << sh:x}"
    if (w & 0x7F800000) == 0x71000000:
        sf = "x" if (w >> 31) else "w"
        sh = 12 if ((w >> 22) & 1) else 0
        return f"subs {sf}{w & 31}, {sf}{(w >> 5) & 31}, #0x{((w >> 10) & 0xFFF) << sh:x}"
    if (w & 0x7F800000) == 0x52800000:
        sf = "x" if (w >> 31) else "w"
        return f"movz {sf}{w & 31}, #0x{(w >> 5) & 0xFFFF:x}" + (f", lsl #{((w >> 21) & 3) * 16}" if ((w >> 21) & 3) else "")
    if (w & 0x7F800000) == 0x12800000:
        sf = "x" if (w >> 31) else "w"
        return f"movn {sf}{w & 31}, #0x{(w >> 5) & 0xFFFF:x}"
    if (w & 0x7F800000) == 0x72800000:
        sf = "x" if (w >> 31) else "w"
        return f"movk {sf}{w & 31}, #0x{(w >> 5) & 0xFFFF:x}, lsl #{((w >> 21) & 3) * 16}"
    if (w & 0xFFE0FFE0) == 0xAA0003E0:
        return f"mov x{w & 31}, x{(w >> 16) & 31}"
    if (w & 0xFFE0FFE0) == 0x2A0003E0:
        return f"mov w{w & 31}, w{(w >> 16) & 31}"
    if (w & 0x3F800000) in (0x39000000, 0x39400000):
        sz = (w >> 30) & 3
        ld = (w >> 22) & 1
        imm = ((w >> 10) & 0xFFF) << sz
        rn = "sp" if ((w >> 5) & 31) == 31 else f"x{(w >> 5) & 31}"
        rt = ("x" if sz == 3 else "w") + str(w & 31)
        op = {0: ("strb", "ldrb"), 1: ("strh", "ldrh"), 2: ("str", "ldr"), 3: ("str", "ldr")}[sz][ld]
        return f"{op} {rt}, [{rn}, #0x{imm:x}]"
    if (w & 0x3A000000) == 0x28000000:
        opc = (w >> 30) & 3
        ld = (w >> 22) & 1
        imm7 = sext((w >> 15) & 0x7F, 7)
        sz = 8 if (opc & 2) else 4
        rx = "x" if (opc & 2) else "w"
        rn = "sp" if ((w >> 5) & 31) == 31 else f"x{(w >> 5) & 31}"
        op = "ldp" if ld else "stp"
        return f"{op} {rx}{w & 31}, {rx}{(w >> 10) & 31}, [{rn}, #0x{imm7 * sz:x}]"
    if (w & 0x7FE0FC00) == 0x6B000000 and (w & 31) == 31:
        sf = "x" if (w >> 31) else "w"
        return f"cmp {sf}{(w >> 5) & 31}, {sf}{(w >> 16) & 31}"
    if (w & 0x7F800000) == 0x72000000:
        return f"tst/ands w{(w >> 5) & 31}, ..."
    return f".word 0x{w:08x}"


def main():
    raw = open(GOLD, "rb").read()
    assert len(raw) == 18112512, f"Unexpected golden size {len(raw)}"
    gold_sha256 = sha256_bytes(raw)
    assert gold_sha256 == GOLD_EXPECTED_SHA256, f"Golden SHA-256 mismatch: {gold_sha256}"

    info = parse_layout(raw)
    sw = info["sw"]
    cmdline_bytes = raw[sw + 0x48 : sw + 0x2A0]
    cmdline = cmdline_bytes.split(b"\x00", 1)[0].decode("ascii")

    exec_img0 = info["exec_sw"][3]
    exec_fz = info["exec_sw"][4]
    text_va0 = info["text_sw"][1]
    text_img0 = info["text_sw"][3]
    text_fz = info["text_sw"][4]

    def sym_lookup(va):
        if va in info["sym_by_va"]:
            return info["sym_by_va"][va]
        best = max((sv for sv in info["sym_by_va"] if sv <= va), default=0)
        return f"{info['sym_by_va'].get(best, '?')}+0x{va - best:x}"

    # Pre-index all ADRP+ADD string xrefs in __TEXT_EXEC
    keywords = [b"sweetusb", b"sweet_usb", b"sweetusblog", b"DWC3", b"usb-drd,t8027", b"sweetkeys"]
    kw_hits = {}
    page_map = {}

    for kw in keywords:
        pos = 0
        locs = []
        while True:
            idx = raw.find(kw, pos)
            if idx == -1:
                break
            # Find null-terminated or string context if inside Mach-O segments
            va = info["img_to_va"](idx)
            if va is not None and text_img0 <= idx < text_img0 + text_fz:
                # Expand back to string start if null-terminated ASCII
                s_start = raw.rfind(b"\x00", max(text_img0, idx - 80), idx)
                s_start = s_start + 1 if s_start != -1 else idx
                s_end = raw.find(b"\x00", idx, min(text_img0 + text_fz, idx + 120))
                if s_end == -1:
                    s_end = idx + len(kw)
                str_va = info["img_to_va"](s_start)
                text_str = raw[s_start:s_end].decode("ascii", errors="replace")
                # Also allow direct xref to exact kw offset OR cstring start
                locs.append((idx, va, s_start, str_va, text_str))
                page_map.setdefault(va & ~0xFFF, []).append((kw.decode(), idx, va, "exact"))
                if str_va != va:
                    page_map.setdefault(str_va & ~0xFFF, []).append((kw.decode(), s_start, str_va, "cstr"))
            else:
                locs.append((idx, va, idx, va, raw[max(0, idx - 8) : idx + 64].split(b"\x00", 1)[0].decode("ascii", errors="replace")))
            pos = idx + 1
        kw_hits[kw.decode()] = locs

    xrefs_by_kw = {kw.decode(): [] for kw in keywords}
    for io in range(exec_img0, exec_img0 + exec_fz, 4):
        w = struct.unpack_from("<I", raw, io)[0]
        va = info["img_to_va"](io)
        if (w & 0x9F000000) == 0x90000000:
            page = (va & ~0xFFF) + (sext((((w >> 5) & 0x7FFFF) << 2) | ((w >> 29) & 3), 21) << 12)
            if page in page_map:
                w2 = struct.unpack_from("<I", raw, io + 4)[0]
                if (w2 & 0x7F800000) == 0x11000000:
                    target_va = page + ((w2 >> 10) & 0xFFF)
                    for kw_name, _, sva, kind in page_map[page]:
                        if sva == target_va:
                            xrefs_by_kw[kw_name].append((io, va, target_va, sym_lookup(va)))

    # Analyze _sweet_usb_probe and _sweet_keys_init functions completely
    key_funcs = {}
    for va, name in info["syms_sorted"]:
        if name in ("_sweet_usb_probe", "_sweet_keys_init") or ("usb" in name.lower() and "sweet" in name.lower()):
            _, ln = info["fn_bounds"].get(va, (name, 0x200))
            key_funcs[name] = (va, min(ln, 0x1200))

    # Inspect _sweet_usb_probe around every sweetusb / sweet_usb / sweetusblog / DWC3 / usb-drd,t8027 xref
    # Detect if sweetusb expects mode != 1 (e.g. cmp w8, #2 -> gadget mode) or only checks nonzero or == 1 / == 2
    usb_probe_va = key_funcs.get("_sweet_usb_probe", (None, 0))[0]
    usb_mode_cmp_values = set()
    has_sweet_usb_bootarg = len(xrefs_by_kw["sweet_usb"]) > 0
    if usb_probe_va:
        p_io = info["va_to_img"](usb_probe_va)
        p_len = key_funcs["_sweet_usb_probe"][1]
        for off in range(0, p_len, 4):
            w = struct.unpack_from("<I", raw, p_io + off)[0]
            if (w & 0x7F800000) == 0x71000000 and (w & 31) == 31:
                imm = (w >> 10) & 0xFFF
                if imm <= 16:
                    usb_mode_cmp_values.add(imm)

    # Check exact patch target for sweetusb=0 -> sweetusb=1 in cmdline
    assert b"sweetusb=0" in cmdline_bytes, "sweetusb=0 not found in SWEETXNU.cmdline"
    buf1 = bytearray(raw)
    cmd_off1 = sw + 0x48 + cmdline_bytes.index(b"sweetusb=0")
    buf1[cmd_off1 : cmd_off1 + 10] = b"sweetusb=1"
    assert len(buf1) == len(raw)
    buf1[0x240:0x254] = calc_bootimg_v1_sha1(buf1)
    buf1[0x254:0x260] = b"\x00" * 12

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_USB1, "wb") as f:
        f.write(buf1)
    out1 = open(OUT_USB1, "rb").read()
    assert len(out1) == 18112512
    assert out1[0x240:0x254] == calc_bootimg_v1_sha1(out1)
    usb1_sha256 = sha256_bytes(out1)

    # Check if a second mode image (e.g. sweetusb=2) is indicated by _sweet_usb_probe
    # Wait: check what values _sweet_usb_probe actually compares against around PE_parse_boot_argn("sweetusb", ...)
    # Let's check exact instructions immediately following PE_parse_boot_argn for sweetusb!
    pe_va = None
    for va, nm in info["syms_sorted"]:
        if nm == "_PE_parse_boot_argn":
            pe_va = va
            break

    sweetusb_parsed_modes = []
    for io, va, sva, sn in xrefs_by_kw["sweetusb"]:
        # Look forward up to 24 instructions for cbz/cbnz/cmp/subs
        snippet = []
        for k in range(0, 28):
            ins_io = io + k * 4
            if ins_io >= exec_img0 + exec_fz:
                break
            w = struct.unpack_from("<I", raw, ins_io)[0]
            ins_va = img_to_va_val = info["img_to_va"](ins_io)
            snippet.append((ins_io, ins_va, w, decode_arm64(ins_va, w, sym_lookup, info["va_to_img"], raw)))
        sweetusb_parsed_modes.append((io, va, sn, snippet))

    # Determine if mode 2 is explicitly branched on right after PE_parse_boot_argn("sweetusb", ...) or inside _sweet_usb_probe
    needs_usb2 = False
    usb2_reason = "None"
    usb2_sha256 = None
    for _, _, _, snip in sweetusb_parsed_modes:
        for _, _, w, dec in snip:
            if dec.startswith(("cmp w", "subs w")) and "#0x2" in dec:
                needs_usb2 = True
                usb2_reason = f"Found `{dec}` in sweetusb check"
    if 2 in usb_mode_cmp_values and not needs_usb2:
        # Check if mode 2 appears anywhere in _sweet_usb_probe
        needs_usb2 = True
        usb2_reason = f"`_sweet_usb_probe` checks cmp value(s) {sorted(usb_mode_cmp_values)}"

    if needs_usb2:
        buf2 = bytearray(raw)
        buf2[cmd_off1 : cmd_off1 + 10] = b"sweetusb=2"
        buf2[0x240:0x254] = calc_bootimg_v1_sha1(buf2)
        buf2[0x254:0x260] = b"\x00" * 12
        with open(OUT_USB2, "wb") as f:
            f.write(buf2)
        out2 = open(OUT_USB2, "rb").read()
        assert len(out2) == 18112512
        assert out2[0x240:0x254] == calc_bootimg_v1_sha1(out2)
        usb2_sha256 = sha256_bytes(out2)

    gold_sha256_after = sha256_bytes(open(GOLD, "rb").read())
    assert gold_sha256_after == GOLD_EXPECTED_SHA256

    # Build Markdown report
    lines = [
        "# USB & Boot-Args Analysis Report (`golden_boot\\boot_a-cpu-ui-touch.img`)",
        "",
        "## 1. Source & Output Images",
        "",
        f"- **Baseline (`golden_boot\\boot_a-cpu-ui-touch.img`)**: `{len(raw)}` bytes, SHA-256: `{gold_sha256_after}` (verified read-only & untouched)",
        f"- **`SWEETXNU` Header**: offset `0x{sw:x}`, version `{info['ver']}`, `nsegs={info['nsegs']}`",
        f"- **Current `CMDLINE` (`0x{sw + 0x48:x}`)**: `{cmdline}`",
        f"- **Output 1 (`work\\next-gen\\boot-g7em-usb1.img`)**: `{len(out1)}` bytes, `sweetusb=1` (replaced `sweetusb=0` in-place at `0x{cmd_off1:x}`, same byte length), SHA-256: `{usb1_sha256}`, boot header SHA-1 ID (`0x240`): `{out1[0x240:0x254].hex()}`",
    ]
    if needs_usb2:
        lines.append(
            f"- **Output 2 (`work\\next-gen\\boot-g7em-usb2.img`)**: `{len(out2)}` bytes, `sweetusb=2` (at `0x{cmd_off1:x}`; reason: {usb2_reason}), SHA-256: `{usb2_sha256}`, boot header SHA-1 ID (`0x240`): `{out2[0x240:0x254].hex()}`"
        )
    else:
        lines.append(f"- **Output 2**: Not needed (`_sweet_usb_probe` mode check values: `{sorted(usb_mode_cmp_values)}`; `{usb2_reason}`).")

    lines.extend([
        "",
        "## 2. Mach-O `LC_SEGMENT_64` & `SWEETXNU` Segment Layout",
        "",
        "| Mach-O Segment | VM Start | VM Size | File Offset | File Size | `nsects` |",
        "|---|---|---:|---:|---:|---:|",
    ])
    for name, vm, vs, fo, fz, nsects in info["lc_segs"]:
        lines.append(f"| `{name}` | `0x{vm:016x}` | `0x{vs:x}` | `0x{fo:x}` | `0x{fz:x}` | {nsects} |")

    lines.extend([
        "",
        "| `SWEETXNU` Index | VM Start | VM Size | Image Offset | File Size |",
        "|---:|---|---:|---:|---:|",
    ])
    for idx, vm, vs, img_o, fz in info["sw_segs"]:
        lines.append(f"| `seg[{idx}]` | `0x{vm:016x}` | `0x{vs:x}` | `0x{img_o:07x}` | `0x{fz:x}` |")

    lines.extend([
        "",
        "## 2b. Mode & Value Expectations (`sweetusb`, `sweet_usb`, `sweetusblog`, `sweetkeys`)",
        "",
        "- **`sweetusb`** (parsed in `_sweet_usb_probe` at `0x062e6c8` via `PE_parse_boot_argn`; defaults to `1` at `0x062e6c0` if omitted from boot-args):",
        "  - `0` (current `golden_boot` setting): `0x062e6e0` (`cbz w8`) disables USB probing and skips DWC3 register/gadget bringup.",
        "  - `1`: DWC3 clock/register probe & **report only** (`0x062e9e0`: `report only (sweetusb=1)`); reads/logs DWC3 registers (`GSNPSID`, `GCTL`, `GSTS`, `GUSB2PHYCFG`, `DCFG`, `DCTL`, `DEVTEN`, `DSTS`, `DALEPENA`, `GEVNT*`, `GHWPARAMS0`), then stops at `0x062eaf8` (`cmp w8, #0x2; b.lt`).",
        "  - `2` (or `>= 2`): Passes `0x062eaf8` (`cmp w8, #0x2; b.lt`), allocates USB buffers/locks (`sweet_usb` lock group at `0x062ec58`), and starts full DWC3 device/gadget mode.",
        "- **`sweet_usb`**: Lock group name string at `0x062ec58` (not a separate boot-arg).",
        "- **`sweetusblog`** (`0x062f214`, defaults to `1` at `0x062f20c`): Non-zero starts the `sweetusblog` kernel worker thread (`0x062f24c`) when active.",
        "- **`DWC3` / `usb-drd,t8027`**: `DWC3` strings at `0x01c40c7..0x01c420c` are used in `_sweet_usb_probe` (`0x062ea40..0x062ebdc`) for Qualcomm SDM845 DWC3 diagnostics; `usb-drd,t8027` has `0` occurrences in this image.",
        "- **`sweetkeys`** (parsed in `_sweet_keys_init` at `0x062a380` via `PE_parse_boot_argn`):",
        "  - `0`: `0x062a398` (`cbz w8`) logs `SWEET KEYS: disabled (sweetkeys=0)` and disables key polling.",
        "  - `!= 0` (e.g. `1`, or omitted default non-zero): Enables GPIO/PMIC hardware key polling and parses `sweetkeys_ai`, `sweetkeys_ai_page`, and `sweetkeys_ai_usage` (`0x062aa1c..0x062aa64`).",
        "",
        "## 3. Keyword Strings & `__TEXT_EXEC` Cross-References",
        "",
    ])
    for kw in [k.decode() for k in keywords]:
        lines.append(f"### `{kw}`")
        hits = kw_hits[kw]
        xrefs = xrefs_by_kw[kw]
        lines.append(f"- String/symbol occurrences ({len(hits)}):")
        for idx, va, s_start, str_va, txt in hits[:20]:
            va_s = f"`0x{va:x}`" if va is not None else "n/a"
            lines.append(f"  - img `0x{idx:07x}` (VA {va_s}): `{txt}`")
        lines.append(f"- `__TEXT_EXEC` `ADRP+ADD` xrefs ({len(xrefs)}):")
        for io, va, sva, sn in xrefs:
            lines.append(f"  - img `0x{io:07x}` (VA `0x{va:x}`, `<{sn}>`) -> `0x{sva:x}`")
        lines.append("")

    # Disassembly around every xref
    lines.extend([
        "## 4. Surrounding Disassembly for Each Cross-Reference",
        "",
    ])
    seen_ranges = []
    for kw in [k.decode() for k in keywords]:
        for io, va, sva, sn in xrefs_by_kw[kw]:
            s_io = max(exec_img0, io - 4 * 4)
            e_io = min(exec_img0 + exec_fz, io + 28 * 4)
            lines.append(f"### Xref `{kw}` at `0x{io:07x}` (`0x{va:x}` `<{sn}>`)")
            lines.append("```asm")
            for cur in range(s_io, e_io, 4):
                cva = info["img_to_va"](cur)
                w = struct.unpack_from("<I", raw, cur)[0]
                mark = "  <-- xref" if cur == io else ""
                lines.append(f"0x{cur:07x} (0x{cva:x}): {w:08x}  {decode_arm64(cva, w, sym_lookup, info['va_to_img'], raw)}{mark}")
            lines.append("```")
            lines.append("")

    # Full key functions disassembly (_sweet_usb_probe, _sweet_keys_init, and any sweet*usb* functions)
    lines.extend([
        "## 5. Relevant USB & Keys Functions Disassembly",
        "",
    ])
    for fname, (fva, flen) in sorted(key_funcs.items(), key=lambda x: x[1][0]):
        fio = info["va_to_img"](fva)
        if fio is None:
            continue
        lines.append(f"### `{fname}` (`0x{fio:07x}`, VA `0x{fva:x}`, size `0x{flen:x}`)")
        lines.append("```asm")
        for cur in range(fio, min(fio + flen, exec_img0 + exec_fz), 4):
            cva = info["img_to_va"](cur)
            w = struct.unpack_from("<I", raw, cur)[0]
            lines.append(f"0x{cur:07x} (0x{cva:x}): {w:08x}  {decode_arm64(cva, w, sym_lookup, info['va_to_img'], raw)}")
        lines.append("```")
        lines.append("")

    with open(REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print("Done: USB report saved to work\\next-gen\\usb_notes.md.")


if __name__ == "__main__":
    main()
