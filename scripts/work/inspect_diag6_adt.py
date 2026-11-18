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

diag6_buf = open('/mnt/c/Users/kyro/Downloads/judyln-ios/out-judyln/shim-boot-g7diag6-g710em.img', 'rb').read()
adt_diag6 = diag6_buf[0x11449c0:0x11449c0 + 12772]

root, _ = adt.parse(adt_diag6)

for c in root.children:
    print(f"Child: {c.name}")
    if c.name in ('chosen', 'arm-io', 'nram', 'pram'):
        for p, f, v in c.props:
            print(f"  {p} (f={f}) = {adt.fmt(v)}")
        if c.name == 'arm-io':
            for sub in c.children:
                print(f"    Sub: {sub.name}")
                for sp, sf, sv in sub.props:
                    print(f"      {sp} = {adt.fmt(sv)}")
