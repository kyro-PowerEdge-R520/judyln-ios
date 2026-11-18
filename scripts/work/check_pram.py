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

diag6 = open('/mnt/c/Users/kyro/Downloads/judyln-ios/out-judyln/shim-boot-g7diag6-g710em.img', 'rb').read()
daily7 = open('/mnt/c/Users/kyro/Downloads/judyln-ios/out-judyln/shim-boot-g7daily7-g710em.img', 'rb').read()

print("Searching 'pram' and 'nram' in diag6:")
idx = 0
while True:
    pos = diag6.find(b'pram', idx)
    if pos == -1: break
    print(f"diag6 'pram' at {hex(pos)}: {diag6[pos-8:pos+24]}")
    idx = pos + 1

idx = 0
while True:
    pos = diag6.find(b'nram', idx)
    if pos == -1: break
    print(f"diag6 'nram' at {hex(pos)}: {diag6[pos-8:pos+24]}")
    idx = pos + 1

print("\nSearching 'pram' and 'nram' in daily7:")
idx = 0
while True:
    pos = daily7.find(b'pram', idx)
    if pos == -1: break
    print(f"daily7 'pram' at {hex(pos)}: {daily7[pos-8:pos+24]}")
    idx = pos + 1

idx = 0
while True:
    pos = daily7.find(b'nram', idx)
    if pos == -1: break
    print(f"daily7 'nram' at {hex(pos)}: {daily7[pos-8:pos+24]}")
    idx = pos + 1
