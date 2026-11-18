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

# Let's find the function sweet_sample_thread / sweet_sample_start
# In sweet_sample.c:
# strings: "SpringBoard,backboardd", "sweetsample", "SMP --- sample %d\n"
pos = buf.find(b'SMP --- sample %d\n')
print("String at", hex(pos))

# In arm64, adrp + add or ldr loads the string address
# String VA: kernel_end = 0xfffffe0008508000, text base = 0xfffffe0007404000
# Let's search for BL instructions to sweet_sample_start
pos_start = buf.find(b'sweetsmp\0')
print("sweetsmp at", hex(pos_start))
