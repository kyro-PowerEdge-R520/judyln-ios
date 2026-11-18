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

# Let's find where sweet_sample_start is in the binary
# In sweet_sample.c:
# void sweet_sample_start(void) {
#    thread_t thread;
#    if (kernel_thread_start(sweet_sample_thread, NULL, &thread) == KERN_SUCCESS) {
#        thread_deallocate(thread);
#    }
# }
# Look for string "sweetsmp" at 0x1c50d7
# Let's search for instructions referencing 0x1c50d7
# In segment 1 (vmaddr = 0xfffffe0007174000, fileoff = 0x1703f0)
# String offset within segment: 0x1c50d7 - 0x1703f0 = 0x54ce7
# String VA = 0xfffffe0007174000 + 0x54ce7 = 0xfffffe00071c8ce7

print("Searching for sweet_sample_thread...")
# Let's find ADRP instructions that target page 0x71c8000
# or search for BL to kernel_thread_start
