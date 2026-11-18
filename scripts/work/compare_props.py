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
daily7_buf = open('/mnt/c/Users/kyro/Downloads/judyln-ios/out-judyln/shim-boot-g7daily7-g710em.img', 'rb').read()

adt_diag6 = diag6_buf[0x11449c0:0x11449c0 + 12772]
adt_daily7 = daily7_buf[0x11449c0:0x11449c0 + 12904]

root_diag6, _ = adt.parse(adt_diag6)
root_daily7, _ = adt.parse(adt_daily7)

def get_prop_map(node, path=""):
    name = node.name
    cur_path = f"{path}/{name}"
    res = {}
    for p, f, v in node.props:
        res[f"{cur_path}:{p}"] = (f, v)
    for c in node.children:
        res.update(get_prop_map(c, cur_path))
    return res

map_diag6 = get_prop_map(root_diag6)
map_daily7 = get_prop_map(root_daily7)

print("Props in daily7 but not diag6:")
for k in map_daily7:
    if k not in map_diag6:
        print(" +", k, map_daily7[k])

print("\nProps in diag6 but not daily7:")
for k in map_diag6:
    if k not in map_daily7:
        print(" -", k, map_diag6[k])

print("\nProps with different values:")
for k in map_diag6:
    if k in map_daily7 and map_diag6[k] != map_daily7[k]:
        print(" *", k, "diag6:", map_diag6[k], "daily7:", map_daily7[k])
