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

import hashlib, struct
from pathlib import Path

SRC = Path(r"work\next-gen\boot-g7em-ui-fast.img")
DST = Path(r"work\next-gen\boot-g7em-ui-fast-8c.img")
GOLD = Path(r"golden_boot\boot_a-cpu-ui-touch.img")
GOLD_SHA256 = "766a88577c208af62583d199fa5dbd8f46811342aa109db5c334a5d38607b3e7"

assert hashlib.sha256(GOLD.read_bytes()).hexdigest() == GOLD_SHA256
buf = bytearray(SRC.read_bytes())

assert b"cpus=8" in buf[0x130040:0x130300], "cpus=8 missing"
idx = buf.find(b"g7perf=100", 0x130040, 0x130300)
assert idx != -1, "g7perf=100 not found in CMDLINE"
buf[idx:idx + 10] = b"g7perf=75 "

pg, k, r, s, dt, rec, dtb = [struct.unpack_from("<I", buf, o)[0] for o in (0x24, 0x08, 0x10, 0x18, 0x28, 0x660, 0x670)]
h = hashlib.sha1()
off = pg
for sz in (k, r, s, dt, rec, dtb):
    h.update(buf[off:off + sz])
    h.update(struct.pack("<I", sz))
    off += (sz + pg - 1) & ~(pg - 1)
buf[0x240:0x254] = h.digest()

DST.write_bytes(buf)
assert hashlib.sha256(GOLD.read_bytes()).hexdigest() == GOLD_SHA256
print("Built:", DST, "SHA-256:", hashlib.sha256(buf).hexdigest())
