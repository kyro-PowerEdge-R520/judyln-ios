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

daily7 = open('/mnt/c/Users/kyro/Downloads/judyln-ios/out-judyln/shim-boot-g7daily7-g710em.img', 'rb').read()
diag6 = open('/mnt/c/Users/kyro/Downloads/judyln-ios/out-judyln/shim-boot-g7diag6-g710em.img', 'rb').read()

print(f"daily7 len={len(daily7)}, diag6 len={len(diag6)}")

# Compare bytes around 0x11449c0
print("Bytes at 0x11449c0:")
print("diag6: ", diag6[0x11449c0:0x11449c0+32].hex())
print("daily7:", daily7[0x11449c0:0x11449c0+32].hex())

# Let's inspect where daily7 differs from diag6 across the whole image!
diffs = []
for i in range(0, min(len(daily7), len(diag6)), 4096):
    if daily7[i:i+4096] != diag6[i:i+4096]:
        diffs.append(i)

print("Different 4K blocks:", [hex(d) for d in diffs])
