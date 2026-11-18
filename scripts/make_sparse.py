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

BLK_SZ = 4096
MAX_RAW_BLKS = 16384  # 64 MiB max per RAW chunk for clean fastboot splitting
ZERO_BLK = b"\x00" * BLK_SZ

def raw_to_sparse(src: Path, dst: Path):
    sz = src.stat().st_size
    assert sz % BLK_SZ == 0, f"{src} size {sz} not aligned to {BLK_SZ}"
    total_blks = sz // BLK_SZ

    chunks = []
    with src.open("rb") as f:
        blk_idx = 0
        cur_type = None
        cur_blks = 0
        cur_off = 0
        while blk_idx < total_blks:
            data = f.read(BLK_SZ)
            if len(data) != BLK_SZ:
                raise EOFError(f"Unexpected EOF at block {blk_idx}")
            btype = 0xCAC2 if data == ZERO_BLK else 0xCAC1
            if btype == cur_type and (btype == 0xCAC2 or cur_blks < MAX_RAW_BLKS):
                cur_blks += 1
            else:
                if cur_type is not None:
                    chunks.append((cur_type, cur_blks, cur_off))
                cur_type = btype
                cur_blks = 1
                cur_off = blk_idx * BLK_SZ
            blk_idx += 1
        if cur_type is not None:
            chunks.append((cur_type, cur_blks, cur_off))

    with src.open("rb") as f, dst.open("wb") as out:
        out.write(struct.pack("<IHHHHIIII", 0xED26FF3A, 1, 0, 28, 12, BLK_SZ, total_blks, len(chunks), 0))
        for ctype, cblks, coff in chunks:
            if ctype == 0xCAC2:
                out.write(struct.pack("<HHII", 0xCAC2, 0, cblks, 16))
                out.write(b"\x00\x00\x00\x00")
            else:
                nbytes = cblks * BLK_SZ
                out.write(struct.pack("<HHII", 0xCAC1, 0, cblks, 12 + nbytes))
                f.seek(coff)
                rem = nbytes
                while rem > 0:
                    buf = f.read(min(rem, 4 * 1024 * 1024))
                    out.write(buf)
                    rem -= len(buf)

    print(f"OK: {dst.name} -> {dst.stat().st_size:,} bytes ({len(chunks)} chunks, {total_blks} blocks)")

for name in ("system", "vendor"):
    raw_to_sparse(Path(rf"crdroid\{name}.img"), Path(rf"crdroid\{name}_sparse.img"))
