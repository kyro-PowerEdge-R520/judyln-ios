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

SRC = r"C:\Users\kyro\Downloads\judyln-ios\work\next-gen\boot-g7em-20j-full.img"
GOLD = r"C:\Users\kyro\Downloads\judyln-ios\golden_boot\boot_a-cpu-ui-touch.img"
DST = r"C:\Users\kyro\Downloads\judyln-ios\work\next-gen\boot-g7em-gpu8-v3.img"
REPORT = r"C:\Users\kyro\Downloads\judyln-ios\work\next-gen\notes_v3.md"

GOLD_EXPECTED_SHA256 = "766a88577c208af62583d199fa5dbd8f46811342aa109db5c334a5d38607b3e7"
TEXT_EXEC_IMG_BASE = 0x424410
TEXT_EXEC_VA_BASE = 0xFFFFFE00072F8000


def sext(val, bits):
    sign = 1 << (bits - 1)
    return val - (1 << bits) if (val & sign) else val


def va_to_img(va):
    return TEXT_EXEC_IMG_BASE + (va - TEXT_EXEC_VA_BASE)


def img_to_va(io):
    return TEXT_EXEC_VA_BASE + (io - TEXT_EXEC_IMG_BASE)


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


def compare_with_golden(src, gold):
    kernel_identical = src[0x1000:0x130000] == gold[0x1000:0x130000]
    sw_src = 0x130000
    sw_gold = 0x130000
    cmd_src = src[sw_src + 0x48 : sw_src + 0x2A0].split(b"\x00", 1)[0].decode("ascii")
    cmd_gold = gold[sw_gold + 0x48 : sw_gold + 0x2A0].split(b"\x00", 1)[0].decode("ascii")

    seg_results = []
    for i in range(10):
        vm_s, vs_s, fo_s, fz_s = struct.unpack_from("<4Q", src, sw_src + 0x2A8 + i * 32)
        vm_g, vs_g, fo_g, fz_g = struct.unpack_from("<4Q", gold, sw_gold + 0x2A8 + i * 32)
        equal = src[sw_src + fo_s : sw_src + fo_s + fz_s] == gold[sw_gold + fo_g : sw_gold + fo_g + fz_g]
        seg_results.append((i, vm_s, sw_src + fo_s, sw_gold + fo_g, fz_s, equal))

    # Locate sweetfb_noconsole xrefs in __TEXT_EXEC
    noconsole_str_off = src.find(b"sweetfb_noconsole\x00")
    noconsole_global_xrefs = []
    for io in range(TEXT_EXEC_IMG_BASE, 0x0C98410, 4):
        va = img_to_va(io)
        w = struct.unpack_from("<I", src, io)[0]
        if (w & 0x9F000000) == 0x90000000:
            page = (va & ~0xFFF) + (sext((((w >> 5) & 0x7FFFF) << 2) | ((w >> 29) & 3), 21) << 12)
            if page == 0xFFFFFE0007C15000:
                for k in range(1, 5):
                    w2 = struct.unpack_from("<I", src, io + 4 * k)[0]
                    if (w2 & 0x3F800000) in (0x39000000, 0x39400000):
                        sz = (w2 >> 30) & 3
                        imm = ((w2 >> 10) & 0xFFF) << sz
                        if imm == 0x4C8:
                            noconsole_global_xrefs.append((io + 4 * k, img_to_va(io + 4 * k), (w2 >> 22) & 1))

    return {
        "kernel_identical": kernel_identical,
        "cmd_src": cmd_src,
        "cmd_gold": cmd_gold,
        "seg_results": seg_results,
        "noconsole_str_off": noconsole_str_off,
        "noconsole_global_xrefs": noconsole_global_xrefs,
    }


def scan_stage8_and_smmu(src):
    needle = b"GPU SMMU context failed at step"
    str_off = src.find(needle)
    assert str_off != -1, "stage8 error string not found"
    str_va = 0xFFFFFE0007004000 + (str_off - 0x130408)
    str_page = str_va & ~0xFFF

    str_xrefs = []
    for io in range(TEXT_EXEC_IMG_BASE, 0x0C98410, 4):
        va = img_to_va(io)
        w = struct.unpack_from("<I", src, io)[0]
        if (w & 0x9F000000) == 0x90000000:
            page = (va & ~0xFFF) + (sext((((w >> 5) & 0x7FFFF) << 2) | ((w >> 29) & 3), 21) << 12)
            if page == str_page and io + 4 < 0x0C98410:
                w2 = struct.unpack_from("<I", src, io + 4)[0]
                if (w2 & 0x7F800000) == 0x11000000 and ((w2 >> 10) & 0xFFF) == (str_va & 0xFFF):
                    str_xrefs.append((io, va))

    attach_va = 0xFFFFFE0007A93CB8
    attach_callers = []
    for io in range(TEXT_EXEC_IMG_BASE, 0x0C98410, 4):
        w = struct.unpack_from("<I", src, io)[0]
        if (w & 0xFC000000) == 0x94000000:
            va = img_to_va(io)
            if va + sext(w & 0x3FFFFFF, 26) * 4 == attach_va:
                attach_callers.append((io, va))

    # Scan ArmSmmu4KAttachStreams and helpers for immediate 0x12 (18) and return MOVZ values
    funcs = [
        ("_ArmSmmu4KAttachStreams", 0xFFFFFE0007A93CB8, 0x374),
        ("_global", 0xFFFFFE0007A9354C, 0x14C),
        ("_ArmSmmu4KObserveOwnedContext", 0xFFFFFE0007A92CA4, 0x10C),
        ("_prepare", 0xFFFFFE0007A927B8, 0x228),
        ("_read_image", 0xFFFFFE0007A929E0, 0x11C),
        ("_ArmSmmu4KValidateContextReadback", 0xFFFFFE0007A8EF78, 0x154),
        ("_ArmSmmu4KEncodeContext", 0xFFFFFE0007A8EAC0, 0x4B8),
        ("_scan", 0xFFFFFE0007A93698, 0x2B4),
        ("_quarantine", 0xFFFFFE0007A9402C, 0x210),
        ("_observe", 0xFFFFFE0007A93A48, 0xB0),
        ("_ArmSmmu4KObserveStreams", 0xFFFFFE0007A9394C, 0xFC),
        ("NativeAdrenoSmmuContext::attach", 0xFFFFFE0007A9CCEC, 0x98),
        ("NativeAdrenoGpuContext::bringUp", 0xFFFFFE0007A97980, 0x5A4),
        ("_g7_adreno_bringup", 0xFFFFFE0007A95134, 0x9B8),
    ]
    imm18_hits = []
    smmu_movz_returns = {}
    for fname, va0, ln in funcs:
        io0 = va_to_img(va0)
        w0s = set()
        w26s = set()
        for off in range(0, ln, 4):
            w = struct.unpack_from("<I", src, io0 + off)[0]
            if (w & 0x7F800000) == 0x52800000:
                rd = w & 31
                imm = (w >> 5) & 0xFFFF
                if imm == 18:
                    imm18_hits.append((fname, io0 + off, va0 + off, rd))
                if rd == 0:
                    w0s.add(imm)
                if rd == 26:
                    w26s.add(imm)
            elif (w & 0x1F000000) == 0x11000000 and ((w >> 10) & 0xFFF) == 18:
                imm18_hits.append((fname, io0 + off, va0 + off, w & 31))
        if fname.startswith("_"):
            smmu_movz_returns[fname] = (sorted(w0s), sorted(w26s))

    return {
        "str_off": str_off,
        "str_va": str_va,
        "str_xrefs": str_xrefs,
        "attach_callers": attach_callers,
        "imm18_hits": imm18_hits,
        "smmu_movz_returns": smmu_movz_returns,
    }


def main():
    src = open(SRC, "rb").read()
    gold = open(GOLD, "rb").read()
    assert len(src) == 18128896, f"Unexpected source length {len(src)}"
    assert len(gold) == 18112512, f"Unexpected golden length {len(gold)}"

    src_sha256 = sha256_bytes(src)
    gold_sha256_before = sha256_bytes(gold)
    assert gold_sha256_before == GOLD_EXPECTED_SHA256, "Golden image SHA-256 mismatch!"

    cmp_info = compare_with_golden(src, gold)
    smmu_info = scan_stage8_and_smmu(src)

    patches = [
        (
            0x0059BE7C,
            0xFFFFFE000746FA6C,
            0x34000068,
            0xD503201F,
            "cbz w8, 0xfffffe000746fa78 -> nop",
            "_console_ring_try_empty: enforce sweetfb_noconsole from early boot (keeps _panic_active screen output)",
        ),
        (
            0x0059C1EC,
            0xFFFFFE000746FDDC,
            0x34000068,
            0xD503201F,
            "cbz w8, 0xfffffe000746fde8 -> nop",
            "__cnputs: enforce sweetfb_noconsole from early boot (keeps _panic_active screen output)",
        ),
        (
            0x00BBF1A4,
            0xFFFFFE0007A92D94,
            0x54000060,
            0x14000003,
            "b.eq 0xfffffe0007a92da0 -> b 0xfffffe0007a92da0",
            "_ArmSmmu4KObserveOwnedContext: ignore pre-existing latched CB0_FSR fault bits (11) in phase 1 & phase 3",
        ),
        (
            0x00BBFA44,
            0xFFFFFE0007A93634,
            0x36D80108,
            0xD503201F,
            "tbz w8, #27, 0xfffffe0007a93654 -> nop",
            "_global: bypass ID0.SMS==0 check on ID0=0x40016605 in phase 1 & phase 3",
        ),
        (
            0x00BBFA98,
            0xFFFFFE0007A93688,
            0x1A8903E0,
            0x52800000,
            "csel w0, wzr, w9, eq -> movz w0, #0x0",
            "_global: do not fail phase 1 & phase 3 on latched SMMU_sGFSR fault status",
        ),
    ]

    # Verify _scan S2CR mask (0xffffff00 ignoring cbndx 0xff in 0x200ff)
    assert struct.unpack_from("<4I", src, 0x0BBFCE0) == (0x121601AD, 0x52185DAD, 0x0A0B01AB, 0x7140817F)

    buf = bytearray(src)
    for off, va, orig_w, new_w, _, _ in patches:
        got = struct.unpack_from("<I", buf, off)[0]
        assert got == orig_w, f"Unexpected word at 0x{off:x}: 0x{got:08x} != 0x{orig_w:08x}"
        struct.pack_into("<I", buf, off, new_w)

    old_id = bytes(src[0x240:0x254])
    assert old_id == calc_bootimg_v1_sha1(src), "Source boot.img SHA-1 mismatch"
    new_id = calc_bootimg_v1_sha1(buf)
    buf[0x240:0x254] = new_id
    buf[0x254:0x260] = b"\x00" * 12

    with open(DST, "wb") as f:
        f.write(buf)

    out = open(DST, "rb").read()
    assert len(out) == 18128896
    assert out[0:8] == b"ANDROID!"
    assert out[0x240:0x254] == calc_bootimg_v1_sha1(out) == new_id
    dst_sha256 = sha256_bytes(out)

    # Verify preserved payload resources and cmdline
    sw = 0x130000
    assert out[sw : sw + 8] == b"SWEETXNU"
    cmdline_full = out[sw + 0x48 : sw + 0x2A0].split(b"\x00", 1)[0].decode("ascii")
    for token in ("g7gpu=8", "sweetfb_noconsole=1", "sweettouch=1", "g7touch_init=2", "-noprogress"):
        assert token in cmdline_full, f"Missing token {token}"

    seg10_vm, seg10_vs, seg10_fo, seg10_fz = struct.unpack_from("<4Q", out, sw + 0x2A8 + 10 * 32)
    elf_off = sw + seg10_fo
    e_type, e_machine = struct.unpack_from("<HH", out, elf_off + 16)
    e_entry, e_phoff = struct.unpack_from("<II", out, elf_off + 24)
    e_phnum = struct.unpack_from("<H", out, elf_off + 44)[0]
    assert out[elf_off : elf_off + 4] == b"\x7fELF"
    gzap_adt_off = out.find(b"G7Zap\x00")
    assert gzap_adt_off != -1

    gold_sha256_after = sha256_bytes(open(GOLD, "rb").read())
    assert gold_sha256_after == GOLD_EXPECTED_SHA256

    diff_count = sum(1 for a, b in zip(src, out) if a != b)

    # Generate Markdown report
    lines = [
        "# Boot Image v3 Analysis & Patch Report (`boot-g7em-gpu8-v3.img`)",
        "",
        "## 1. Image Summary & Integrity Verification",
        "",
        "| Artifact | Size (bytes) | SHA-256 | Android Boot v1 ID (`0x240..0x254`) |",
        "|---|---:|---|---|",
        f"| Source (`work\\next-gen\\boot-g7em-20j-full.img`) | {len(src)} | `{src_sha256}` | `{old_id.hex()}` |",
        f"| Output (`work\\next-gen\\boot-g7em-gpu8-v3.img`) | {len(out)} | `{dst_sha256}` | `{new_id.hex()}` |",
        f"| Golden (`golden_boot\\boot_a-cpu-ui-touch.img`) | {len(gold)} | `{gold_sha256_after}` | `{gold[0x240:0x254].hex()}` |",
        "",
        f"- Golden read-only guard: **verified unchanged** (`{gold_sha256_after}` == `{GOLD_EXPECTED_SHA256}`).",
        f"- Total differing bytes between `boot-g7em-20j-full.img` and `boot-g7em-gpu8-v3.img`: **{diff_count} bytes** (20 bytes boot header SHA-1 ID + 20 bytes ARM64 instruction patches).",
        "",
        "### Preserved Resources & Boot Arguments",
        f"- `SWEETXNU.cmdline` (`0x130048`): `{cmdline_full}`",
        f"- `seg[10]` (`G7Zap` ELF32): `va=0x{seg10_vm:x}`, `vs=0x{seg10_vs:x}`, `img_off=0x{elf_off:x}`, `fz=0x{seg10_fz:x}`, `e_type={e_type}`, `e_machine=0x{e_machine:x}`, `e_entry=0x{e_entry:x}`, `e_phoff={e_phoff}`, `e_phnum={e_phnum}`",
        f"- ADT `/chosen/memory-map/G7Zap` string offset: `0x{gzap_adt_off:x}`",
        "",
        "## 2. Comparison vs. `golden_boot\\boot_a-cpu-ui-touch.img` (Console Suppression)",
        "",
        f"- Linux kernel shim + appended DTB (`0x1000..0x130000`) identical: **{cmp_info['kernel_identical']}**",
        f"- Source `SWEETXNU.cmdline`: `{cmp_info['cmd_src']}`",
        f"- Golden `SWEETXNU.cmdline`: `{cmp_info['cmd_gold']}`",
        "",
        "| Segment | Virtual Address | Source Img Offset | Golden Img Offset | File Size | Byte-for-Byte Equal |",
        "|---:|---|---:|---:|---:|---|",
    ]
    for i, vm, off_s, off_g, fz, eq in cmp_info["seg_results"]:
        lines.append(f"| `seg[{i}]` | `0x{vm:016x}` | `0x{off_s:07x}` | `0x{off_g:07x}` | `0x{fz:06x}` | {eq} |")

    lines.extend([
        "",
        "### Why Console Text Still Rendered on Screen in `v2` (`g7gpu=8`)",
        f"- Both images contain identical kernel segments, DTB/ADT properties, `-noprogress`, and `sweetfb_noconsole=1`; the sole non-`seg[10]` difference in `golden_boot` is `g7gpu=0` vs `g7gpu=8`.",
        f"- `AppleCLCD::present` (`0x0bac86c`, VA `0xfffffe0007a8045c`) parses `sweetfb_noconsole` (`0x{cmp_info['noconsole_str_off']:x}`) and stores `1` to `[0xfffffe0007c154c8]` **only when the UI presents its first frame**.",
        "- Before `AppleCLCD::present` runs, `[0xfffffe0007c154c8]` is `0`, so `_console_ring_try_empty` (`0x059be7c`) and `__cnputs` (`0x059c1ec`) fall through `cbz w8` and render kernel logs onto the framebuffer whenever `g7gpu=8` delays or fails GPU/UI startup.",
        f"- All xrefs to `[0xfffffe0007c154c8]` in `__TEXT_EXEC`: " + ", ".join(
            f"`0x{io:07x}` (`0x{va:x}`, {'ldr' if ld else 'str'})" for io, va, ld in cmp_info["noconsole_global_xrefs"]
        ),
        "- Patching `0x059be7c` and `0x059c1ec` from `cbz w8` to `nop` makes non-panic framebuffer console suppression unconditional from early boot while preserving `bl _panic_active` (real panics still display on screen).",
        "",
        "## 3. `stage8` / `route 18 phase 1` Binary Trace",
        "",
        f"- Format string `\"GPU SMMU context failed at step...\"`: `img=0x{smmu_info['str_off']:x}`, `va=0x{smmu_info['str_va']:x}`",
        "- `_g7_adreno_bringup` xrefs to format string: " + ", ".join(
            f"`0x{io:07x}` (`0x{va:x}`)" for io, va in smmu_info["str_xrefs"]
        ),
        "- Printf struct mapping in `_g7_adreno_bringup` (`report` at `sp + 0xe0`):",
        "  - `step %u` <- `[sp, #0xe0]` (`report + 0x00`)",
        "  - `program %u` <- `[sp, #0x110]` (`report + 0x30`)",
        "  - `route %u` <- `[sp, #0x114]` (`report + 0x34`)",
        "  - `phase %u` <- `[sp, #0xf8]` (`report + 0x18`)",
        "- `NativeAdrenoGpuContext::bringUp` (`0x0bc4110..0x0bc411c`): copies `smmu_ + 0x284` (`[x19, #0x484]`) -> `report + 0x34` and `smmu_ + 0x1b0` (`[x19, #0x3b0]`) -> `report + 0x18`.",
        "- Single caller of `_ArmSmmu4KAttachStreams` (`0xfffffe0007a93cb8`): " + ", ".join(
            f"`0x{io:07x}` (`0x{va:x}`)" for io, va in smmu_info["attach_callers"]
        ) + " (`NativeAdrenoSmmuContext::attach+0x6c`, stores `w0` directly to `[x20, #0x284]` and adds `8` to `0xe00002c2` -> `0xe00002ca`).",
        f"- Immediate `18` (`0x12`) scan hits in SMMU / Adreno attach functions: **{len(smmu_info['imm18_hits'])}** (`{smmu_info['imm18_hits']}`).",
        "- All return values encoded across `ArmSmmu4K` attach helpers (strictly `ArmSmmu4KStatus` `0..11`):",
    ])
    for fn, (w0s, w26s) in smmu_info["smmu_movz_returns"].items():
        lines.append(f"  - `{fn}`: `w0` imm={w0s}, `w26` imm={w26s}")

    lines.extend([
        "",
        "### Phase 1 Validation Evaluation (`ID0=0x40016605`, `IDR1=0x20000805`, `sCR0=0x200626`, `S2CR=0x200ff`)",
        "- `_global` (`0x0bbf95c`):",
        "  - `0x0bbfa44`: `ID0.SMS == 0` -> returns `6` (`Unsupported`). **Patched -> `nop`**.",
        "  - `0x0bbfa4c..a60`: `NUMSMRG = 5 != 0`, `0xc14 <= 0x10000` -> passes.",
        "  - `0x0bbfa6c..a88`: `(0x200626 & 0x407) == 0x406` and `EXIDENABLE == ID0.EXIDS == 0` -> passes.",
        "  - `0x0bbfa98`: `SMMU_sGFSR != 0` -> returns `11` (`Fault`). **Patched -> `movz w0, #0x0`**.",
        "- `_ArmSmmu4KObserveOwnedContext` (`0x0bbf0b4`):",
        "  - `0x0bbf148`: `_ArmSmmu4KValidateContextReadback` verifies `CB0` config (`program 0`).",
        "  - `0x0bbf1a4`: `CB0_FSR & 0xc00001fe != 0` -> returns `11` (`Fault`), which was *not* checked by `NativeAdrenoSmmuContext::program()` and *not* patched in `v2`. **Patched (`0x0bbf1a4`) -> unconditional branch to success (`0xfffffe0007a92da0`)** so `phase 1` & `phase 3` proceed cleanly when pre-existing `CB0_FSR` bits are latched.",
        "- `_scan` (`0x0bbfaa8`):",
        "  - `0x0bbfcdc..cf0`: `0x0bbfce4` (`eor w13, w13, #0xffffff00`) already masks out `cbndx` `[7:0]` (`0x200ff & 0xffffff00 == 0x20000`); `SMR = 0` (`VALID = 0`) skips cleanly at `0x0bbfcf4`.",
        "",
        "## 4. Applied Patches (`boot-g7em-gpu8-v3.img`)",
        "",
        "| File Offset | Virtual Address | Original Word | Patched Word | Assembly Change | Purpose |",
        "|---:|---|---:|---:|---|---|",
    ])
    for off, va, orig_w, new_w, asm_desc, purpose in patches:
        lines.append(f"| `0x{off:07x}` | `0x{va:016x}` | `0x{orig_w:08x}` | `0x{new_w:08x}` | `{asm_desc}` | {purpose} |")
    lines.append(f"| `0x0000240` | `(boot_hdr+0x240)` | `{old_id.hex()}` | `{new_id.hex()}` | 20-byte SHA-1 ID | Recomputed Android boot.img v1 checksum |")

    with open(REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Done: boot-g7em-gpu8-v3.img created ({len(out)} bytes, SHA-256: {dst_sha256}). Report saved to work\\next-gen\\notes_v3.md.")


if __name__ == "__main__":
    main()
