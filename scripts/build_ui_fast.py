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
import struct

GOLD = r"C:\Users\kyro\Downloads\judyln-ios\golden_boot\boot_a-cpu-ui-touch.img"
OUT_DIR = r"C:\Users\kyro\Downloads\judyln-ios\work\next-gen"
DST = os.path.join(OUT_DIR, "boot-g7em-ui-fast.img")
REPORT = os.path.join(OUT_DIR, "ui_fast_notes.md")
GOLD_EXPECTED_SHA256 = "766a88577c208af62583d199fa5dbd8f46811342aa109db5c334a5d38607b3e7"


def sext(val, bits):
    sign = 1 << (bits - 1)
    return val - (1 << bits) if (val & sign) else val


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def calc_bootimg_sha1(buf):
    ksz, _, rsz, _, ssz, _, _, pg, _, _ = struct.unpack_from("<10I", buf, 8)

    def align(n):
        return ((n + pg - 1) // pg) * pg

    k_off = pg
    r_off = k_off + align(ksz)
    s_off = r_off + align(rsz)

    h = hashlib.sha1()
    h.update(buf[k_off : k_off + ksz])
    h.update(struct.pack("<I", ksz))
    h.update(buf[r_off : r_off + rsz])
    h.update(struct.pack("<I", rsz))
    h.update(buf[s_off : s_off + ssz])
    h.update(struct.pack("<I", ssz))
    return h.digest()


def parse_layout(buf):
    sw = buf.find(b"SWEETXNU")
    nsegs = struct.unpack_from("<I", buf, sw + 12)[0]
    sw_segs = [struct.unpack_from("<4Q", buf, sw + 0x2A8 + i * 32) for i in range(nsegs)]
    t_vm, _, t_fo, t_fz = sw_segs[0]
    t_io = sw + t_fo
    e_vm, _, e_fo, e_fz = sw_segs[2]
    e_io = sw + e_fo
    l_vm, _, l_fo, l_fz = sw_segs[9]
    l_io = sw + l_fo

    ncmds = struct.unpack_from("<I", buf, t_io + 16)[0]
    off = t_io + 32
    symoff = nsyms = stroff = le_fo = 0
    for _ in range(ncmds):
        cmd, csz = struct.unpack_from("<II", buf, off)
        if cmd == 0x19 and buf[off + 8 : off + 24].split(b"\x00", 1)[0] == b"__LINKEDIT":
            le_fo = struct.unpack_from("<Q", buf, off + 40)[0]
        elif cmd == 2:
            symoff, nsyms, stroff, _ = struct.unpack_from("<4I", buf, off + 8)
        off += csz

    le_delta = l_io - le_fo
    sym_img = symoff + le_delta
    str_img = stroff + le_delta
    sym_by_va = {}
    syms_sorted = []
    for i in range(nsyms):
        n_strx, _, _, _, nv = struct.unpack_from("<IBBHQ", buf, sym_img + i * 16)
        if nv:
            end = buf.find(b"\x00", str_img + n_strx)
            nm = buf[str_img + n_strx : end].decode("ascii", errors="replace")
            sym_by_va[nv] = nm
            syms_sorted.append((nv, nm))
    syms_sorted.sort()

    def sym_name(va):
        if va in sym_by_va:
            return sym_by_va[va]
        best = max((sv for sv in sym_by_va if sv <= va), default=0)
        return f"{sym_by_va.get(best, '?')}+0x{va - best:x}"

    def io_to_va(io):
        return e_vm + (io - e_io)

    def va_to_io(va):
        return e_io + (va - e_vm)

    return {
        "sw": sw,
        "t_vm": t_vm,
        "t_io": t_io,
        "t_fz": t_fz,
        "e_vm": e_vm,
        "e_io": e_io,
        "e_fz": e_fz,
        "sym_name": sym_name,
        "io_to_va": io_to_va,
        "va_to_io": va_to_io,
        "syms_sorted": syms_sorted,
    }


def decode_arm64(va, w, sym_name):
    if w == 0xD503201F:
        return "nop"
    if w == 0xD65F03C0:
        return "ret"
    if (w & 0xFC000000) in (0x14000000, 0x94000000):
        op = "bl" if (w >> 31) else "b"
        tgt = va + sext(w & 0x3FFFFFF, 26) * 4
        return f"{op} 0x{tgt:x} <{sym_name(tgt)}>"
    if (w & 0xFF000010) == 0x54000000:
        conds = ["eq", "ne", "cs", "cc", "mi", "pl", "vs", "vc", "hi", "ls", "ge", "lt", "gt", "le", "al", "nv"]
        return f"b.{conds[w & 0xF]} 0x{va + sext((w >> 5) & 0x7FFFF, 19) * 4:x}"
    if (w & 0x7E000000) == 0x34000000:
        op = "cbnz" if (w & 0x01000000) else "cbz"
        rx = "x" if (w >> 31) else "w"
        return f"{op} {rx}{w & 31}, 0x{va + sext((w >> 5) & 0x7FFFF, 19) * 4:x}"
    if (w & 0x7E000000) == 0x36000000:
        op = "tbnz" if (w & 0x01000000) else "tbz"
        bit = ((w >> 31) << 5) | ((w >> 19) & 0x1F)
        return f"{op} w{w & 31}, #{bit}, 0x{va + sext((w >> 5) & 0x3FFF, 14) * 4:x}"
    if (w & 0x9F000000) == 0x90000000:
        page = (va & ~0xFFF) + (sext((((w >> 5) & 0x7FFFF) << 2) | ((w >> 29) & 3), 21) << 12)
        return f"adrp x{w & 31}, 0x{page:x}"
    if (w & 0x9F000000) == 0x10000000:
        return f"adr x{w & 31}, 0x{va + sext((((w >> 5) & 0x7FFFF) << 2) | ((w >> 29) & 3), 21):x}"
    if (w & 0x7F800000) == 0x11000000:
        sf = "x" if (w >> 31) else "w"
        sh = 12 if ((w >> 22) & 1) else 0
        rn = "sp" if ((w >> 5) & 31) == 31 else f"{sf}{(w >> 5) & 31}"
        rd = "sp" if (w & 31) == 31 else f"{sf}{w & 31}"
        return f"add {rd}, {rn}, #0x{((w >> 10) & 0xFFF) << sh:x}"
    if (w & 0x7F800000) == 0x51000000:
        sf = "x" if (w >> 31) else "w"
        rn = "sp" if ((w >> 5) & 31) == 31 else f"{sf}{(w >> 5) & 31}"
        rd = "sp" if (w & 31) == 31 else f"{sf}{w & 31}"
        return f"sub {rd}, {rn}, #0x{(w >> 10) & 0xFFF:x}"
    if (w & 0x7F800000) == 0x52800000:
        sf = "x" if (w >> 31) else "w"
        return f"movz {sf}{w & 31}, #0x{(w >> 5) & 0xFFFF:x}"
    if (w & 0xFFE0FFE0) == 0xAA0003E0:
        return f"mov x{w & 31}, x{(w >> 16) & 31}"
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
    return f".word 0x{w:08x}"


def find_xrefs(raw, info, pat):
    t_io, t_vm, t_fz = info["t_io"], info["t_vm"], info["t_fz"]
    e_io, e_vm, e_fz = info["e_io"], info["e_vm"], info["e_fz"]
    targets = {}
    pos = 0
    while True:
        idx = raw.find(pat, pos)
        if idx == -1:
            break
        if t_io <= idx < t_io + t_fz:
            s0 = raw.rfind(b"\x00", max(t_io, idx - 64), idx) + 1
            for cand in {s0, idx}:
                sva = t_vm + (cand - t_io)
                targets.setdefault(sva & ~0xFFF, []).append((sva, cand))
        pos = idx + 1

    res = []
    for io in range(e_io, e_io + e_fz, 4):
        w = struct.unpack_from("<I", raw, io)[0]
        va = e_vm + (io - e_io)
        if (w & 0x9F000000) == 0x90000000:
            page = (va & ~0xFFF) + (sext((((w >> 5) & 0x7FFFF) << 2) | ((w >> 29) & 3), 21) << 12)
            if page in targets:
                w2 = struct.unpack_from("<I", raw, io + 4)[0]
                if (w2 & 0x7F800000) == 0x11000000:
                    tva = page + ((w2 >> 10) & 0xFFF)
                    for sva, sio in targets[page]:
                        if tva == sva:
                            res.append((io, va, info["sym_name"](va), sio))
    return res


def main():
    raw = open(GOLD, "rb").read()
    assert len(raw) == 18112512
    gold_sha256 = sha256_bytes(raw)
    assert gold_sha256 == GOLD_EXPECTED_SHA256
    assert raw[0x240:0x254] == calc_bootimg_sha1(raw)

    info = parse_layout(raw)

    noconsole_xrefs = find_xrefs(raw, info, b"sweetfb_noconsole")
    sweetsurf_xrefs = find_xrefs(raw, info, b"SweetSurface")
    aks_xrefs = find_xrefs(raw, info, b"SWEET AKS:")
    iok_xrefs = find_xrefs(raw, info, b"IOK ")

    # Locate BL _IOLog immediately following each SWEET AKS: and IOK  xref
    iolog_va = None
    for va, nm in info["syms_sorted"]:
        if nm == "_IOLog":
            iolog_va = va
            break
    assert iolog_va is not None

    patch_sites = []
    for category, xlist in (("SWEET AKS", aks_xrefs), ("IOK", iok_xrefs)):
        for io, va, sn, sio in xlist:
            found_bl = None
            for k in range(1, 16):
                cur_io = io + 4 * k
                w = struct.unpack_from("<I", raw, cur_io)[0]
                if (w & 0xFC000000) == 0x94000000:
                    tgt = info["io_to_va"](cur_io) + sext(w & 0x3FFFFFF, 26) * 4
                    if tgt == iolog_va:
                        found_bl = (cur_io, info["io_to_va"](cur_io), w, sn, category)
                        break
            assert found_bl is not None, f"Expected BL _IOLog after {category} xref at 0x{io:x}"
            if found_bl[0] not in [p[0] for p in patch_sites]:
                patch_sites.append(found_bl)

    buf = bytearray(raw)
    for io, va, orig_w, sn, cat in patch_sites:
        assert struct.unpack_from("<I", buf, io)[0] == orig_w
        struct.pack_into("<I", buf, io, 0xD503201F)  # nop

    new_id = calc_bootimg_sha1(buf)
    buf[0x240:0x254] = new_id
    buf[0x254:0x260] = b"\x00" * 12

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(DST, "wb") as f:
        f.write(buf)

    out = open(DST, "rb").read()
    assert len(out) == 18112512
    assert out[0x240:0x254] == calc_bootimg_sha1(out) == new_id
    dst_sha256 = sha256_bytes(out)

    gold_after_sha256 = sha256_bytes(open(GOLD, "rb").read())
    assert gold_after_sha256 == GOLD_EXPECTED_SHA256

    # Build Markdown report
    lines = [
        "# UI Fast Boot Analysis & Patch Notes (`boot-g7em-ui-fast.img`)",
        "",
        "## 1. Image Summary & Integrity Verification",
        "",
        f"- **Source (`golden_boot\\boot_a-cpu-ui-touch.img`)**: `{len(raw)}` bytes, SHA-256: `{gold_after_sha256}` (verified read-only & untouched), header ID: `{raw[0x240:0x254].hex()}`",
        f"- **Output (`work\\next-gen\\boot-g7em-ui-fast.img`)**: `{len(out)}` bytes, SHA-256: `{dst_sha256}`, header ID: `{new_id.hex()}`",
        f"- **Total patched instructions**: `{len(patch_sites)}` `bl _IOLog` calls replaced with `nop` (`0xd503201f`).",
        "",
        "## 2. `sweetfb_noconsole` & `SweetSurface` / `AppleCLCD` First Frame Swap Findings",
        "",
        "### Framebuffer Console Hiding Condition",
        f"- `AppleCLCD::present` (`0x0bac804`, VA `0xfffffe0007a80414`) reads `[this + 0x104]` (`0x0bac838`). On the first frame swap, it calls `PE_parse_boot_argn(\"sweetfb_noconsole\", ...)` at `0x0bac84c`..`0x0bac85c` and stores `1` to `[0xfffffe0007c154c8]` (`0x0bac878`).",
        "- `_console_ring_try_empty` (`0x059be54..0x059be64`) and `__cnputs` (`0x059c1c4..0x059c1d4`) read `[0xfffffe0007c154c8]`. Once non-zero, both skip framebuffer console rendering unless `_panic_active()` returns non-zero.",
        "- Before `AppleCLCD::present()` runs for the first time, `[0xfffffe0007c154c8]` starts at `0`, so synchronous `SWEET AKS:` and `IOK ` `IOLog` prints still scroll on the CPU framebuffer during early boot and `backboardd` startup.",
        "",
        "### First Frame Swap Gate Check (`SweetSurface` & `AppleCLCD`)",
        "- `SweetSurface` (`0x0ba8f80..0x0bab9e0`) and `SweetSurfaceRef` (`0x0ba957c..0x0bab978`) only wrap `OSObject` memory-backed IOSurface state (`kernelAddress`, `IOSurfaceRootUserClient::addRef` at `0x0ba9e74`, `returnSurface` at `0x0baa1b8`); there are no hardware locks, GPU dependencies, or swap gates.",
        "- `AppleCLCD::start` (`0x0bac06c`) sets a `sweetfb_hz` (60 Hz) `IOTimerEventSource` vsync timer (`0x0bac2c4`), `AppleCLCD::vsyncFired` (`0x0bac484`) calls `AppleCLCD::present()` (`0x0bac6fc`), and `AppleCLCD::swap()` (`0x0bacf08`) immediately presents the swapped surface.",
        "- Thus, nothing in `SweetSurface` or `AppleCLCD` blocks the first frame swap; muting the repetitive `SWEET AKS:` and `IOK ` prints removes CPU framebuffer scrolling overhead before `AppleCLCD::present()` latches `sweetfb_noconsole=1`.",
        "",
        "## 3. `__TEXT_EXEC` Cross-References & Surrounding Disassembly",
        "",
    ]

    for label, xlist in (("`sweetfb_noconsole`", noconsole_xrefs), ("`SweetSurface`", sweetsurf_xrefs)):
        lines.append(f"### {label} ({len(xlist)} xrefs)")
        for io, va, sn, sio in xlist:
            lines.append(f"- img `0x{io:07x}` (`0x{va:x}`, `<{sn}>`) -> string `0x{sio:x}`")
            lines.append("```asm")
            for cur in range(max(info["e_io"], io - 16), min(info["e_io"] + info["e_fz"], io + 64), 4):
                cva = info["io_to_va"](cur)
                w = struct.unpack_from("<I", raw, cur)[0]
                mark = "  <-- xref" if cur == io else ""
                lines.append(f"0x{cur:07x} (0x{cva:x}): {w:08x}  {decode_arm64(cva, w, info['sym_name'])}{mark}")
            lines.append("```")
        lines.append("")

    # Also dump console gate + AppleCLCD::present head
    lines.extend([
        "### Framebuffer Console Flag Writers & Readers",
        "```asm",
    ])
    for cur in list(range(0x059be4c, 0x059be70, 4)) + list(range(0x059c1bc, 0x059c1e0, 4)) + list(range(0x0bac834, 0x0bac884, 4)):
        cva = info["io_to_va"](cur)
        w = struct.unpack_from("<I", raw, cur)[0]
        lines.append(f"0x{cur:07x} (0x{cva:x}): {w:08x}  {decode_arm64(cva, w, info['sym_name'])}  ; <{info['sym_name'](cva)}>")
    lines.extend([
        "```",
        "",
        "## 4. Muted `SWEET AKS:` and `IOK ` Log Sites (`boot-g7em-ui-fast.img`)",
        "",
        "| Category | File Offset | Virtual Address | Original `bl _IOLog` | Patched Word | Function |",
        "|---|---:|---|---:|---:|---|",
    ])
    for io, va, orig_w, sn, cat in patch_sites:
        lines.append(f"| `{cat}` | `0x{io:07x}` | `0x{va:016x}` | `0x{orig_w:08x}` | `0xd503201f` (`nop`) | `{sn}` |")
    lines.append(f"| Header SHA-1 | `0x0000240` | `(hdr+0x240)` | `{raw[0x240:0x254].hex()}` | `{new_id.hex()}` | Recomputed Android boot header ID |")

    with open(REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print("Done: boot-g7em-ui-fast.img created.")


if __name__ == "__main__":
    main()
