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

import struct
from pathlib import Path

img = Path(r"work\next-gen\boot-g7em-gpu8-v3-log.img").read_bytes()
VA_DELTA = 0xfffffe0006ed3bf0
TEXT_START, TEXT_END = 0x0424410, 0x0c98410

def u32(off):
    return struct.unpack_from("<I", img, off)[0]

def sbits(val, bits):
    return val - (1 << bits) if (val & (1 << (bits - 1))) else val

def disasm_one(off):
    w = u32(off)
    va = off + VA_DELTA
    reg = "x" if (w >> 31) & 1 else "w"
    if (w & 0x9f000000) == 0x90000000:
        imm = sbits((((w >> 5) & 0x7ffff) << 2) | ((w >> 29) & 3), 21)
        return f"adrp x{w&31}, 0x{(va & ~0xfff) + (imm << 12):x}"
    if (w & 0xff000000) == 0x91000000:
        imm = ((w >> 10) & 0xfff) << (12 if ((w >> 22) & 1) else 0)
        return f"add x{w&31}, x{(w>>5)&31}, #0x{imm:x}"
    if (w & 0xfc000000) in (0x94000000, 0x14000000):
        op = "bl" if (w >> 31) & 1 else "b"
        return f"{op} 0x{va + (sbits(w & 0x3ffffff, 26) << 2):x}"
    if (w & 0x7e000000) == 0x34000000:
        op = "cbnz" if (w >> 24) & 1 else "cbz"
        return f"{op} {reg}{w&31}, 0x{va + (sbits((w >> 5) & 0x7ffff, 19) << 2):x}"
    if (w & 0x7e000000) == 0x36000000:
        op = "tbnz" if (w >> 24) & 1 else "tbz"
        bit = (((w >> 31) & 1) << 5) | ((w >> 19) & 0x1f)
        return f"{op} {reg}{w&31}, #{bit}, 0x{va + (sbits((w >> 5) & 0x3fff, 14) << 2):x}"
    if (w & 0xff000010) == 0x54000000:
        return f"b.{w&0xf:x} 0x{va + (sbits((w >> 5) & 0x7ffff, 19) << 2):x}"
    if (w & 0x1f800000) == 0x12800000:
        op = {0: "movn", 2: "movz", 3: "movk"}.get((w >> 29) & 3, "mov?")
        return f"{op} {reg}{w&31}, #0x{(w >> 5) & 0xffff:x}, lsl #{((w >> 21) & 3)*16}"
    if (w & 0x3b000000) == 0x39000000:
        sz = (w >> 30) & 3
        opc = (w >> 22) & 3
        imm = ((w >> 10) & 0xfff) << sz
        op = {0: "str", 1: "ldr"}.get(opc, f"mem{opc}")
        r = "x" if sz == 3 else "w"
        return f"{op} {r}{w&31}, [x{(w>>5)&31}, #0x{imm:x}]"
    return f"0x{w:08x}"

def find_all_xrefs(needle, exact=True, start_search=0x130000):
    pat = needle.encode() + (b"\x00" if exact else b"")
    pos = start_search
    while True:
        s_off = img.find(pat, pos)
        if s_off < 0:
            break
        pos = s_off + 1
        end = img.find(b"\x00", s_off)
        s_txt = img[s_off:end].decode("ascii", errors="replace")
        s_va = s_off + VA_DELTA
        s_page, s_lo = s_va & ~0xfff, s_va & 0xfff
        for off in range(TEXT_START, TEXT_END, 4):
            w = u32(off)
            if (w & 0x9f000000) == 0x90000000:
                imm = sbits((((w >> 5) & 0x7ffff) << 2) | ((w >> 29) & 3), 21)
                if ((off + VA_DELTA) & ~0xfff) + (imm << 12) == s_page:
                    rd = w & 31
                    for k in range(1, 8):
                        w2 = u32(off + k*4)
                        if (w2 & 0xff000000) == 0x91000000 and ((w2 >> 5) & 31) == rd:
                            imm2 = ((w2 >> 10) & 0xfff) << (12 if ((w2 >> 22) & 1) else 0)
                            if imm2 == s_lo:
                                print(f"\n=== {s_txt!r} (str=0x{s_off:x}) -> xref 0x{off:x} (0x{off+VA_DELTA:x}) ===")
                                for j in range(-3, 10):
                                    o = off + j*4
                                    print(f"  0x{o:07x} (0x{o+VA_DELTA:x}): {u32(o):08x}  {disasm_one(o)}")

find_all_xrefs("matching", exact=False, start_search=0x130400)
find_all_xrefs("g7gpu", exact=True, start_search=0x130400)
find_all_xrefs("G7 GPU: stage8", exact=False, start_search=0x130400)

print("\n=== _g7g_bringup_thread tail (0x0634c20..0x0634cf0) ===")
for o in range(0x0634c20, 0x0634cf0, 4):
    print(f"  0x{o:07x} (0x{o+VA_DELTA:x}): {u32(o):08x}  {disasm_one(o)}")
