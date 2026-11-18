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
SEGS = [
    (0xfffffe0007004000, 0x0130408, 0x170000),
    (0xfffffe0007174000, 0x02a0410, 0x184000),
    (0xfffffe00072f8000, 0x0424410, 0x874000),
    (0xfffffe0007b6c000, 0x0c98410, 0x004000),
    (0xfffffe0007b70000, 0x0c9c410, 0x004000),
    (0xfffffe0007b74000, 0x0ca0410, 0x004000),
    (0xfffffe0007b78000, 0x0ca4410, 0x048000),
    (0xfffffe00080b0000, 0x0cec410, 0x04c000),
    (0xfffffe00080fc000, 0x0d38410, 0x04c000),
    (0xfffffe0008148000, 0x0d84410, 0x3be5c8),
]

def off_to_va(off):
    for va, base, sz in SEGS:
        if base <= off < base + sz:
            return va + (off - base)
    return None

def u32(off):
    return struct.unpack_from("<I", img, off)[0]

def sbits(val, bits):
    return val - (1 << bits) if (val & (1 << (bits - 1))) else val

def disasm_one(off):
    w = u32(off)
    va = off_to_va(off)
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
    if (w & 0xff000010) == 0x54000000:
        return f"b.{w&0xf:x} 0x{va + (sbits((w >> 5) & 0x7ffff, 19) << 2):x}"
    if (w & 0x3b000000) == 0x39000000:
        sz = (w >> 30) & 3
        opc = (w >> 22) & 3
        imm = ((w >> 10) & 0xfff) << sz
        op = {0: "str", 1: "ldr"}.get(opc, f"mem{opc}")
        r = "x" if sz == 3 else "w"
        return f"{op} {r}{w&31}, [x{(w>>5)&31}, #0x{imm:x}]"
    return f"0x{w:08x}"

def find_va_xrefs(target_va, label, after=6):
    t_page, t_lo = target_va & ~0xfff, target_va & 0xfff
    print(f"=== {label} (0x{target_va:x}) ===")
    for off in range(0x0424410, 0x0c98410, 4):
        w = u32(off)
        if (w & 0x9f000000) == 0x90000000:
            va = off_to_va(off)
            imm = sbits((((w >> 5) & 0x7ffff) << 2) | ((w >> 29) & 3), 21)
            if (va & ~0xfff) + (imm << 12) == t_page:
                rd = w & 31
                for k in range(1, 6):
                    w2 = u32(off + k*4)
                    # ADD imm12
                    if (w2 & 0xff000000) == 0x91000000 and ((w2 >> 5) & 31) == rd:
                        imm2 = ((w2 >> 10) & 0xfff) << (12 if ((w2 >> 22) & 1) else 0)
                        if imm2 == t_lo:
                            print(f"  xref 0x{off:x} (0x{va:x}):")
                            for j in range(0, after):
                                o = off + j*4
                                print(f"    0x{o:07x}: {u32(o):08x}  {disasm_one(o)}")
                    # LDR/STR unsigned imm
                    if (w2 & 0x3b000000) == 0x39000000 and ((w2 >> 5) & 31) == rd:
                        sz = (w2 >> 30) & 3
                        imm2 = ((w2 >> 10) & 0xfff) << sz
                        if imm2 == t_lo:
                            print(f"  xref 0x{off:x} (0x{va:x}):")
                            for j in range(0, after):
                                o = off + j*4
                                print(f"    0x{o:07x}: {u32(o):08x}  {disasm_one(o)}")

find_va_xrefs(0xfffffe00080895f0, "g_g7gpu", after=6)
find_va_xrefs(0xfffffe0007c5d2c0, "G7AdrenoAccelerator::metaClass", after=8)

for needle in [b"found\n\x00", b"found\x00"]:
    pos = 0x130408
    while True:
        s_off = img.find(needle, pos)
        if s_off < 0: break
        pos = s_off + 1
        start = img.rfind(b"\x00", 0x130408, s_off) + 1
        txt = img[start:s_off+len(needle)-1].decode("ascii", errors="replace")
        if "matching" in txt or "IOK" in txt:
            find_va_xrefs(off_to_va(start), f"str {txt!r}", after=6)
