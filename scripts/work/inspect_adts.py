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

import struct, sys
sys.path.insert(0, '/mnt/c/Users/kyro/Downloads/lancelot-ios/ios-sweet/tools')
import adt

files = [
    ('orig', '/mnt/c/Users/kyro/Downloads/judyln-ios/G7-iOS16-boot/G7-iOS16-boot/shim-boot-g7daily7.img'),
    ('diag6', '/mnt/c/Users/kyro/Downloads/judyln-ios/out-judyln/shim-boot-g7diag6-g710em.img'),
    ('daily7', '/mnt/c/Users/kyro/Downloads/judyln-ios/out-judyln/shim-boot-g7daily7-g710em.img'),
]

for name, path in files:
    buf = open(path, 'rb').read()
    magic, kstart, kend, entry, adt_off, adt_sz, mem_sz = struct.unpack_from('<8sQQQQQQ', buf, 0x132000)
    cmdline = buf[0x132048:0x132048+250].split(b'\0')[0].decode('ascii', errors='replace')
    print(f'=== {name} ===')
    print(f'len: {len(buf)} magic: {magic} adt_off: {hex(adt_off)} adt_sz: {adt_sz} ({hex(adt_sz)}) mem_sz: {hex(mem_sz)}')
    print(f'cmdline: {cmdline}')
    
    adt_blob = buf[0x11449c0:0x11449c0 + adt_sz]
    try:
        root, end_off = adt.parse(adt_blob)
        print(f'adt parse success: parsed {end_off} bytes (blob has {len(adt_blob)})')
    except Exception as e:
        print(f'adt parse failed: {e}')
