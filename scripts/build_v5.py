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
import struct
from pathlib import Path

SRC = Path(r"work\next-gen\boot-g7em-gpu8-v4.img")
DST = Path(r"work\next-gen\boot-g7em-gpu8-v5.img")
GOLD = Path(r"golden_boot\boot_a-cpu-ui-touch.img")
GOLD_SHA256 = "766a88577c208af62583d199fa5dbd8f46811342aa109db5c334a5d38607b3e7"
NOP = 0xD503201F
VA_DELTA = 0xfffffe0006ed3bf0

def u32(buf, off):
    return struct.unpack_from("<I", buf, off)[0]

def w32(buf, off, val):
    struct.pack_into("<I", buf, off, val)

def sbits(val, bits):
    return val - (1 << bits) if (val & (1 << (bits - 1))) else val

def disasm_one(buf, off):
    w = u32(buf, off)
    va = off + VA_DELTA
    reg = "x" if (w >> 31) & 1 else "w"
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

def update_boot_v1_sha1(buf):
    page_sz = struct.unpack_from("<I", buf, 0x24)[0]
    k_sz = struct.unpack_from("<I", buf, 0x08)[0]
    r_sz = struct.unpack_from("<I", buf, 0x10)[0]
    s_sz = struct.unpack_from("<I", buf, 0x18)[0]
    dt_sz = struct.unpack_from("<I", buf, 0x28)[0]
    rec_sz = struct.unpack_from("<I", buf, 0x660)[0]
    dtb_sz = struct.unpack_from("<I", buf, 0x670)[0]
    align = lambda n: (n + page_sz - 1) & ~(page_sz - 1)
    h = hashlib.sha1()
    off = page_sz
    for sz in (k_sz, r_sz, s_sz, dt_sz, rec_sz, dtb_sz):
        h.update(buf[off:off + sz])
        h.update(struct.pack("<I", sz))
        off += align(sz)
    buf[0x240:0x254] = h.digest()
    return h.hexdigest()

assert hashlib.sha256(GOLD.read_bytes()).hexdigest() == GOLD_SHA256
buf = bytearray(SRC.read_bytes())

print("=== _ArmSmmu4KAttachStreams phase 1 (0x0bc00c8..0x0bc0250) ===")
route10_hits = []
for o in range(0x0bc00c8, 0x0bc0250, 4):
    w = u32(buf, o)
    # Match movz w26, #10 (0x5280015a) or any write of immediate 10 to w26
    if w == 0x5280015a or ((w & 0x7f80001f) == 0x5280001a and ((w >> 5) & 0xffff) == 10):
        route10_hits.append(o)
    if (w & 0x1f) == 26 or (w & 0x7e000000) in (0x34000000, 0x36000000) or (w & 0xff000010) == 0x54000000 or (w & 0xfc000000) in (0x94000000, 0x14000000):
        print(f"  0x{o:07x} (0x{o+VA_DELTA:x}): {w:08x}  {disasm_one(buf, o)}")

print(f"\nFound mov w26, #10 at: {[hex(x) for x in route10_hits]}")
for hit in route10_hits:
    # Show surrounding 6 instructions and look for the conditional branch jumping to hit
    target_va = hit + VA_DELTA
    print(f"Context around 0x{hit:x} (va=0x{target_va:x}):")
    for o in range(hit - 24, hit + 16, 4):
        print(f"  0x{o:07x} (0x{o+VA_DELTA:x}): {u32(buf, o):08x}  {disasm_one(buf, o)}")
    # Find any branch in 0x0bc00c8..0x0bc0250 whose target is target_va
    for o in range(0x0bc00c8, 0x0bc0250, 4):
        w = u32(buf, o)
        va = o + VA_DELTA
        t = None
        if (w & 0x7e000000) == 0x34000000:
            t = va + (sbits((w >> 5) & 0x7ffff, 19) << 2)
        elif (w & 0x7e000000) == 0x36000000:
            t = va + (sbits((w >> 5) & 0x3fff, 14) << 2)
        elif (w & 0xff000010) == 0x54000000:
            t = va + (sbits((w >> 5) & 0x7ffff, 19) << 2)
        if t == target_va:
            print(f"  -> NOPing branch at 0x{o:07x} ({disasm_one(buf, o)}) -> route 10")
            w32(buf, o, NOP)

new_id = update_boot_v1_sha1(buf)
DST.write_bytes(buf)
assert hashlib.sha256(GOLD.read_bytes()).hexdigest() == GOLD_SHA256
print(f"\nBuilt {DST} (SHA-256: {hashlib.sha256(DST.read_bytes()).hexdigest()}, boot_id: {new_id})")
