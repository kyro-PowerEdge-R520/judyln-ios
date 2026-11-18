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

daily7 = open('/mnt/c/Users/kyro/Downloads/judyln-ios/out-judyln/shim-boot-g7daily7-g710em.img', 'rb').read()
adt = daily7[0x11449c0:0x11449c0 + 12904]

import struct

for i in range(len(adt) - 4):
    val, = struct.unpack_from('<I', adt, i)
    if (val & 0xff000000) in (0x80000000, 0xb0000000, 0x40000000):
        print(f"Offset {hex(i)}: val = {hex(val)}")
