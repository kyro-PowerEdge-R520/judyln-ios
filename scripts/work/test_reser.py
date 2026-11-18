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

import sys
sys.path.insert(0, '/mnt/c/Users/kyro/Downloads/lancelot-ios/ios-sweet/tools')
import adt

diag6_buf = open('/mnt/c/Users/kyro/Downloads/judyln-ios/out-judyln/shim-boot-g7diag6-g710em.img', 'rb').read()
adt_diag6 = diag6_buf[0x11449c0:0x11449c0 + 12772]

root, _ = adt.parse(adt_diag6)
reser = adt.serialize(root)

print(f"len(adt_diag6) = {len(adt_diag6)}, len(reser) = {len(reser)}")
if reser == adt_diag6:
    print("MATCHES EXACTLY!")
else:
    print("MISMATCH!")
    diffs = [i for i in range(min(len(adt_diag6), len(reser))) if adt_diag6[i] != reser[i]]
    print(f"First mismatch at {hex(diffs[0]) if diffs else 'length'}")
    print("diag6:", adt_diag6[diffs[0]-8:diffs[0]+24].hex())
    print("reser:", reser[diffs[0]-8:diffs[0]+24].hex())
