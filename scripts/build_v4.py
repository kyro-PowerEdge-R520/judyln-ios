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

SRC = Path(r"work\next-gen\boot-g7em-gpu8-v3-log.img")
DST = Path(r"work\next-gen\boot-g7em-gpu8-v4.img")
GOLD = Path(r"golden_boot\boot_a-cpu-ui-touch.img")
NOTES = Path(r"work\next-gen\notes_v4.md")

GOLD_SHA256 = "766a88577c208af62583d199fa5dbd8f46811342aa109db5c334a5d38607b3e7"
NOP = 0xD503201F

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

def va_to_off(addr):
    for va, base, sz in SEGS:
        if va <= addr < va + sz:
            return base + (addr - va)
    return None

def sbits(val, bits):
    return val - (1 << bits) if (val & (1 << (bits - 1))) else val

def u32(buf, off):
    return struct.unpack_from("<I", buf, off)[0]

def w32(buf, off, val):
    struct.pack_into("<I", buf, off, val)

def disasm_one(buf, off):
    w = u32(buf, off)
    va = off_to_va(off) or 0
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

def find_str_xrefs(buf, str_off):
    s_va = off_to_va(str_off)
    if not s_va:
        return []
    s_page, s_lo = s_va & ~0xfff, s_va & 0xfff
    hits = []
    for off in range(0x0424410, 0x0c98410, 4):
        w = u32(buf, off)
        if (w & 0x9f000000) == 0x90000000:
            va = off_to_va(off)
            imm = sbits((((w >> 5) & 0x7ffff) << 2) | ((w >> 29) & 3), 21)
            if (va & ~0xfff) + (imm << 12) == s_page:
                rd = w & 31
                for k in range(1, 8):
                    w2 = u32(buf, off + k*4)
                    if (w2 & 0xff000000) == 0x91000000 and ((w2 >> 5) & 31) == rd:
                        imm2 = ((w2 >> 10) & 0xfff) << (12 if ((w2 >> 22) & 1) else 0)
                        if imm2 == s_lo:
                            hits.append(off)
    return hits

def update_boot_v1_sha1(buf):
    # Android boot.img v1 layout: page_size at 0x24, sizes at 0x08, 0x10, 0x18, 0x20, 0x660, 0x670
    page_sz = struct.unpack_from("<I", buf, 0x24)[0]
    k_sz = struct.unpack_from("<I", buf, 0x08)[0]
    r_sz = struct.unpack_from("<I", buf, 0x10)[0]
    s_sz = struct.unpack_from("<I", buf, 0x18)[0]
    dt_sz = struct.unpack_from("<I", buf, 0x28)[0]
    rec_sz = struct.unpack_from("<I", buf, 0x660)[0]
    dtb_sz = struct.unpack_from("<I", buf, 0x670)[0]

    def align(n):
        return (n + page_sz - 1) & ~(page_sz - 1)

    h = hashlib.sha1()
    off = page_sz
    for sz in (k_sz, r_sz, s_sz, dt_sz, rec_sz, dtb_sz):
        h.update(buf[off:off + sz])
        h.update(struct.pack("<I", sz))
        off += align(sz)
    digest = h.digest()
    buf[0x240:0x254] = digest
    return digest.hex()

gold_hash = hashlib.sha256(GOLD.read_bytes()).hexdigest()
assert gold_hash == GOLD_SHA256, f"Golden hash mismatch: {gold_hash}"

buf = bytearray(SRC.read_bytes())
patches = []

# 1. Locate and mute only the repetitive IOK matching log call ("matching " / "found")
matching_bl_patched = []
pos = 0x130408
while pos < 0x424410:
    s_off = buf.find(b"matching", pos)
    if s_off < 0:
        break
    pos = s_off + 1
    start = buf.rfind(b"\x00", 0x130408, s_off) + 1
    end = buf.find(b"\x00", s_off)
    txt = buf[start:end].decode("ascii", errors="replace")
    if "found" in txt or "IOK" in txt or txt.startswith("matching"):
        for xref in find_str_xrefs(buf, start):
            for k in range(1, 10):
                cand = xref + k*4
                w = u32(buf, cand)
                if (w & 0xfc000000) == 0x94000000:  # bl log_fn
                    orig = u32(buf, cand)
                    w32(buf, cand, NOP)
                    patches.append((cand, orig, NOP, f"Mute repetitive matching log ({txt!r})"))
                    matching_bl_patched.append(cand)
                    break

# 2. Inspect g7gpu init block (0x0633ab4..0x0633b50) & _g7g_bringup_thread post-bringup (0x0634cf0..0x0634d90)
g7gpu_init_lines = [f"  0x{o:07x} (0x{off_to_va(o):x}): {u32(buf, o):08x}  {disasm_one(buf, o)}" for o in range(0x0633ab4, 0x0633b50, 4)]
bringup_tail_lines = [f"  0x{o:07x} (0x{off_to_va(o):x}): {u32(buf, o):08x}  {disasm_one(buf, o)}" for o in range(0x0634cf0, 0x0634d90, 4)]

# Also check if g7gpu init block stores a Metal/GPU capability flag to a global that we can clear on bringup failure
# Look for stores to 0xfffffe0008089xxx in 0x0633ab4..0x0633b50
gpu_cap_globals = []
last_page = {}
for o in range(0x0633ab4, 0x0633b50, 4):
    w = u32(buf, o)
    va = off_to_va(o)
    if (w & 0x9f000000) == 0x90000000:
        imm = sbits((((w >> 5) & 0x7ffff) << 2) | ((w >> 29) & 3), 21)
        last_page[w & 31] = (va & ~0xfff) + (imm << 12)
    elif (w & 0x3b000000) == 0x39000000 and ((w >> 22) & 3) == 0:  # str
        rn = (w >> 5) & 31
        if rn in last_page:
            sz = (w >> 30) & 3
            imm = ((w >> 10) & 0xfff) << sz
            gpu_cap_globals.append((o, last_page[rn] + imm, disasm_one(buf, o)))

# 3. Recompute boot.img v1 SHA-1
new_id = update_boot_v1_sha1(buf)
DST.write_bytes(buf)

assert hashlib.sha256(GOLD.read_bytes()).hexdigest() == GOLD_SHA256
out_sha256 = hashlib.sha256(DST.read_bytes()).hexdigest()

report = [
    "# Boot Image v4 Build & Inspection Report (`boot-g7em-gpu8-v4.img`)",
    "",
    f"- Output: `{DST}` ({len(buf)} bytes, SHA-256: `{out_sha256}`)",
    f"- Boot header SHA-1 ID (`0x240..0x254`): `{new_id}`",
    f"- Golden image verified untouched: `{GOLD_SHA256}`",
    "",
    "## Applied Patches",
]
for off, orig, new, desc in patches:
    report.append(f"- `0x{off:07x}` (`0x{off_to_va(off):x}`): `0x{orig:08x}` -> `0x{new:08x}` ({desc})")
report += [
    "",
    "## g7gpu Init Block (`0x0633ab4..0x0633b50`)",
    "```",
    *g7gpu_init_lines,
    "```",
    "",
    "## `_g7g_bringup_thread` Post-Bringup (`0x0634cf0..0x0634d90`)",
    "```",
    *bringup_tail_lines,
    "```",
]
NOTES.write_text("\n".join(report) + "\n", encoding="utf-8")

print(f"Built {DST} (SHA-256: {out_sha256})")
print(f"Patched matching log calls: {[hex(x) for x in matching_bl_patched]}")
print("GPU cap globals written in 0x0633ab4..0x0633b50:", [(hex(o), hex(va), ins) for o, va, ins in gpu_cap_globals])
print("\n--- _g7g_bringup_thread (0x0634cf0..0x0634d90) ---")
print("\n".join(bringup_tail_lines[:24]))
