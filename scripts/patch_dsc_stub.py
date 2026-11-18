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

import glob, struct, sys

dsc = "/root/hackios/ios165/20F66__iPhone10,3_6/dyld_shared_cache_arm64"
target_va = 0x1a4b6813c

# mov x0, #0 (0xd2800000); ret (0xd65f03c0)
stub = bytes.fromhex("000080d2c0035fd6")

files = [dsc] + sorted(p for p in glob.glob(dsc + ".*") if not p.endswith((".map", ".dylddata", ".dyldlinkedit")))

patched = False
for fp in files:
    with open(fp, "rb") as f:
        h = f.read(512)
        if not h.startswith(b"dyld_v1"):
            continue
        mo, mc = struct.unpack_from("<II", h, 0x10)
        f.seek(mo)
        vm_ranges = []
        for _ in range(mc):
            va, sz, fo, _, _ = struct.unpack("<QQQII", f.read(32))
            if sz:
                vm_ranges.append((va, va + sz, fo))

    # Check if target_va falls within this file's VM ranges
    for start_va, end_va, file_off in vm_ranges:
        if start_va <= target_va < end_va:
            offset = file_off + (target_va - start_va)
            print(f"[+] Found target VA {hex(target_va)} in {fp} at file offset {hex(offset)}")
            
            with open(fp, "r+b") as f:
                f.seek(offset)
                old_bytes = f.read(8)
                print(f"[+] Old bytes: {old_bytes.hex()}")
                f.seek(offset)
                f.write(stub)
                f.seek(offset)
                new_bytes = f.read(8)
                print(f"[+] New bytes: {new_bytes.hex()} (mov x0, #0; ret)")
            patched = True
            break
    if patched:
        break

if patched:
    print("[+] Successfully patched shared cache!")
else:
    print("[-] Error: Target VA not found in any shared cache VM range.")
