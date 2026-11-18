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

with open('/mnt/c/Users/kyro/Downloads/judyln-ios/work/sweet-console9.txt') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'SMP' in l:
        print(f"Line {i+1}: {l.strip()}")
        # print 5 lines before and after
        start = max(0, i - 3)
        end = min(len(lines), i + 4)
        for j in range(start, end):
            print(f"   [{j+1}] {lines[j].strip()}")
        print("-" * 40)
