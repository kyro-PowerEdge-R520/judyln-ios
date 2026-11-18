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

buf = open('/mnt/c/Users/kyro/Downloads/judyln-ios/out-judyln/shim-boot-g7daily7-g710em.img', 'rb').read()

# sweet_sample_start starts with a function prologue and calls kernel_thread_start
# Let's search for references to string "sweetsmp"
str_pos = buf.find(b'sweetsmp\0')
print("sweetsmp string offset:", hex(str_pos))

# In the kernel, virtual base is 0xfffffe0007404000, unslid 0xfffffe0007004000
# File offset to VA:
# Let's inspect the payload segments in SWEETXNU header:
magic, version, nsegs, virt_base, entry_va, adt_off, adt_size, kernel_end, phys_base, mem_size = struct.unpack_from('<8sIIQQQQQQQ', buf, 0x132000)
print(f"virt_base: {hex(virt_base)}, entry_va: {hex(entry_va)}")

segs = []
off = 0x132000 + 0x2a8
for i in range(nsegs):
    vmaddr, vmsize, fileoff, filesize = struct.unpack_from('<4Q', buf, off)
    segs.append((vmaddr, vmsize, fileoff, filesize))
    off += 32

for s in segs:
    print(f"Segment: vmaddr={hex(s[0])} vmsize={hex(s[1])} fileoff={hex(s[2])} filesize={hex(s[3])}")
