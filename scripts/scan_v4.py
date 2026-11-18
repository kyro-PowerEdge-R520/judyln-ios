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

def disasm_one(off):
    w = u32(off)
    va = off + VA_DELTA
    if (w & 0x9f000000) == 0x90000000:
        imm = (((w >> 5) & 0x7ffff) << 2) | ((w >> 29) & 3)
        if imm & 0x100000: imm -= 0x200000
        return f"adrp x{w&31}, 0x{(va & ~0xfff) + (imm << 12):x}"
    if (w & 0xff000000) == 0x91000000:
        imm = ((w >> 10) & 0xfff) << (12 if ((w >> 22) & 1) else 0)
        return f"add x{w&31}, x{(w>>5)&31}, #0x{imm:x}"
    if (w & 0xfc000000) == 0x94000000:
        imm = w & 0x3ffffff
        if imm & 0x2000000: imm -= 0x4000000
        return f"bl 0x{va + (imm << 2):x}"
    if (w & 0xfc000000) == 0x14000000:
        imm = w & 0x3ffffff
        if imm & 0x2000000: imm -= 0x4000000
        return f"b 0x{va + (imm << 2):x}"
    if (w & 0x3b000000) == 0x39000000:
        sz = (w >> 30) & 3
        opc = (w >> 22) & 3
        imm = ((w >> 10) & 0xfff) << sz
        op = {0: "str", 1: "ldr"}.get(opc, f"mem{opc}")
        reg = "x" if sz == 3 else "w"
        return f"{op} {reg}{w&31}, [x{(w>>5)&31}, #0x{imm:x}]"
    return f"0x{w:08x}"

def find_str_xrefs(needle):
    s_off = img.find(needle.encode() + b"\x00")
    if s_off < 0:
        print(f"[!] String not found: {needle}")
        return
    s_va = s_off + VA_DELTA
    s_page = s_va & ~0xfff
    s_lo = s_va & 0xfff
    print(f"\n=== {needle!r} (img=0x{s_off:x}, va=0x{s_va:x}) ===")
    for off in range(TEXT_START, TEXT_END, 4):
        w = u32(off)
        if (w & 0x9f000000) == 0x90000000:
            imm = (((w >> 5) & 0x7ffff) << 2) | ((w >> 29) & 3)
            if imm & 0x100000: imm -= 0x200000
            if ((off + VA_DELTA) & ~0xfff) + (imm << 12) == s_page:
                rd = w & 31
                for k in range(1, 8):
                    w2 = u32(off + k*4)
                    if (w2 & 0xff000000) == 0x91000000 and ((w2 >> 5) & 31) == rd:
                        imm2 = ((w2 >> 10) & 0xfff) << (12 if ((w2 >> 22) & 1) else 0)
                        if imm2 == s_lo:
                            print(f"-- xref at img=0x{off:x} (va=0x{off+VA_DELTA:x}) --")
                            for j in range(-4, 10):
                                o = off + j*4
                                print(f"  0x{o:07x} (0x{o+VA_DELTA:x}): {u32(o):08x}  {disasm_one(o)}")

find_str_xrefs("IOK %s: matching ")
find_str_xrefs("g7gpu")

print("\n=== _g7g_bringup_thread (0x0634b64..0x0634c30) ===")
for o in range(0x0634b64, 0x0634c30, 4):
    print(f"  0x{o:07x} (0x{o+VA_DELTA:x}): {u32(o):08x}  {disasm_one(o)}")

print("\n=== G7AdrenoAccelerator::attachCore (0x0bc0d10..0x0bc0da0) ===")
for o in range(0x0bc0d10, 0x0bc0da0, 4):
    print(f"  0x{o:07x} (0x{o+VA_DELTA:x}): {u32(o):08x}  {disasm_one(o)}")
