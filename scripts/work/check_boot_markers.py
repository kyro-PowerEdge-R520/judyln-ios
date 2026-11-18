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
    text = f.read()

# Look for kernel boot markers:
markers = ["Darwin Kernel Version", "initialize_screen", "pmap_startup", "Early boot complete", "exec launchd"]
for m in markers:
    idx = 0
    count = 0
    while True:
        pos = text.find(m, idx)
        if pos == -1: break
        count += 1
        line_no = text[:pos].count('\n') + 1
        print(f"Marker '{m}' found at line {line_no}")
        idx = pos + 1
