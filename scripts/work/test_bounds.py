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

buf_daily7 = open('/mnt/c/Users/kyro/Downloads/judyln-ios/out-judyln/shim-boot-g7daily7-g710em.img', 'rb').read()
buf_diag6 = open('/mnt/c/Users/kyro/Downloads/judyln-ios/out-judyln/shim-boot-g7diag6-g710em.img', 'rb').read()

adt_daily7 = buf_daily7[0x11449c0:0x11449c0 + 12904]
adt_diag6 = buf_diag6[0x11449c0:0x11449c0 + 12772]

def validate_dt(blob, label=""):
    print(f"\n=== Validating {label} (len={len(blob)}) ===")
    
    # Simulate XNU DTBase and DTEnd
    # Let's track absolute simulated pointers: DTBase = 0xfffffe0088508000
    DTBase = 0xfffffe0088508000
    DTEnd = DTBase + len(blob)
    
    def walk(off, path=""):
        if off + 8 > len(blob):
            raise ValueError(f"Node header at {hex(off)} out of bounds [0, {hex(len(blob))})")
        nprops, nchildren = struct.unpack_from('<II', blob, off)
        cur = off + 8
        
        node_name = "?"
        # check properties
        for i in range(nprops):
            prop_ptr = cur
            if prop_ptr + 36 > len(blob):
                raise ValueError(f"Property header {i} at {hex(prop_ptr)} out of bounds")
            name_raw = blob[prop_ptr:prop_ptr+32]
            name = name_raw.split(b'\0')[0].decode('latin1', 'replace')
            length, = struct.unpack_from('<I', blob, prop_ptr+32)
            
            # Check length: In XNU next_prop_region:
            # os_add3_overflow((uintptr_t)prop, prop->length, sizeof(DeviceTreeNodeProperty) + 3, &next_addr)
            # next_addr &= ~3ULL;
            # Note: in XNU, prop is uintptr_t (64-bit). prop->length is uint32_t!
            # If bit 31 is set or if length is huge:
            val_len = length & 0x7fffffff
            val_ptr = prop_ptr + 36
            if val_ptr + val_len > len(blob):
                raise ValueError(f"Property {name} value ({hex(val_len)} bytes) at {hex(val_ptr)} exceeds blob {hex(len(blob))}")
            
            val = blob[val_ptr:val_ptr+val_len]
            if name == 'name':
                node_name = val.split(b'\0')[0].decode('latin1', 'replace')
            
            # Check for bit 31 flag!
            if length & 0x80000000:
                print(f"  [FLAG BIT 31] {path}/{node_name}:{name} length={hex(length)}")
            
            next_prop = (prop_ptr + 36 + length + 3) & ~3
            if next_prop > len(blob):
                print(f"  [OVERFLOW] {path}/{node_name}:{name} next_prop={hex(next_prop)} > len={hex(len(blob))}")
            
            # Advance to next prop
            cur = (prop_ptr + 36 + val_len + 3) & ~3

        cur_path = f"{path}/{node_name}"
        # walk children
        for j in range(nchildren):
            cur = walk(cur, cur_path)
            
        return cur

    end_off = walk(0)
    print(f"Walk completed at {hex(end_off)} / {hex(len(blob))}")

validate_dt(adt_diag6, "diag6")
validate_dt(adt_daily7, "daily7")
