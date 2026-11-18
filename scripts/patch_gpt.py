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

import struct, zlib
from pathlib import Path

LBA_SZ = 4096
bak = bytearray(Path(r"crdroid\sda_gpt_bak.bin").read_bytes())
assert len(bak) == 8 * LBA_SZ, f"Expected 32768 bytes, got {len(bak)}"

mbr = bak[:LBA_SZ]
hdr = bytearray(bak[LBA_SZ : 2 * LBA_SZ])
assert hdr[:8] == b"EFI PART", f"Missing EFI PART signature: {hdr[:8]!r}"

rev, hdr_sz, _, _, my_lba, alt_lba, first_usable, last_usable, disk_guid, part_lba, num_entries, entry_sz, _ = struct.unpack(
    "<IIIIQQQQ16sQIII", hdr[8:92]
)
entries_bytes = num_entries * entry_sz
entries = bytearray(bak[2 * LBA_SZ : 2 * LBA_SZ + entries_bytes])

p26_off = 25 * entry_sz
p27_off = 26 * entry_sz

p26_first, p26_last = struct.unpack("<QQ", entries[p26_off + 32 : p26_off + 48])
p26_name = entries[p26_off + 56 : p26_off + 128].decode("utf-16le").rstrip("\x00")
p27_first, p27_last = struct.unpack("<QQ", entries[p27_off + 32 : p27_off + 48])
p27_name = entries[p27_off + 56 : p27_off + 128].decode("utf-16le").rstrip("\x00")

assert p26_name == "userdata" and p26_first == 3092230 and p26_last == 15386617, f"Unexpected p26: {p26_name} {p26_first}..{p26_last}"
assert p27_name == "grow" and p27_first == 15386618 and p27_last == 15386618, f"Unexpected p27: {p27_name} {p27_first}..{p27_last}"

# Keep sda26 start at 4K LBA 3092230, shrink to 4325376 4K-blocks (16.50 GiB)
p26_new_last = 3092230 + 4325376 - 1   # 7417605
# Expand sda27 (grow) to 4K LBAs 7417606..15386618 (7969013 4K-blocks = 30.40 GiB)
p27_new_first = p26_new_last + 1       # 7417606

struct.pack_into("<QQ", entries, p26_off + 32, p26_first, p26_new_last)
struct.pack_into("<QQ", entries, p27_off + 32, p27_new_first, p27_last)

entries_crc = zlib.crc32(entries) & 0xFFFFFFFF

def build_header(cur_lba: int, bak_lba: int, ent_lba: int) -> bytearray:
    h = bytearray(hdr)
    struct.pack_into("<II", h, 16, 0, 0)                 # 16..20 HeaderCRC32=0, 20..24 Reserved=0
    struct.pack_into("<QQ", h, 24, cur_lba, bak_lba)     # 24..32 MyLBA, 32..40 AlternateLBA
    struct.pack_into("<Q", h, 72, ent_lba)               # 72..80 PartitionEntryLBA
    struct.pack_into("<I", h, 88, entries_crc)           # 88..92 PartitionEntryArrayCRC32
    hcrc = zlib.crc32(h[:hdr_sz]) & 0xFFFFFFFF
    struct.pack_into("<I", h, 16, hcrc)
    _, _, check_crc, check_res, check_my, check_alt = struct.unpack("<IIIIQQ", h[8:40])
    assert check_res == 0 and check_my == cur_lba and check_alt == bak_lba and check_crc == hcrc
    return h

entry_sectors = entries_bytes // LBA_SZ
bak_start_lba = alt_lba - entry_sectors
assert bak_start_lba == 15386622

pri_hdr = build_header(1, alt_lba, 2)
bak_hdr = build_header(alt_lba, 1, bak_start_lba)

Path(r"crdroid\sda_gpt_primary_new.bin").write_bytes(mbr + pri_hdr + entries)
Path(r"crdroid\sda_gpt_backup_new.bin").write_bytes(entries + bak_hdr)
print(f"OK: userdata (sda26) -> 4K LBAs {p26_first}..{p26_new_last} ({(p26_new_last - p26_first + 1)*LBA_SZ/1024**3:.2f} GiB)")
print(f"OK: grow     (sda27) -> 4K LBAs {p27_new_first}..{p27_last} ({(p27_last - p27_new_first + 1)*LBA_SZ/1024**3:.2f} GiB)")
