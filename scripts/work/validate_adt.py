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

def validate_device_tree(blob):
    """
    Exact XNU skipProperties / next_prop_region / skipTree validation.
    Returns (True, num_nodes, num_props) on success, or raises ValueError.
    """
    total_len = len(blob)
    total_props = 0
    total_nodes = 0

    def parse_node(offset, path=""):
        nonlocal total_props, total_nodes
        total_nodes += 1
        
        if offset + 8 > total_len:
            raise ValueError(f"Node header at {hex(offset)} exceeds ADT length {hex(total_len)}")
        
        nprops, nchildren = struct.unpack_from('<II', blob, offset)
        curr = offset + 8
        node_name = "?"

        # Walk properties exactly as XNU does
        for i in range(nprops):
            prop_offset = curr
            if prop_offset + 36 > total_len:
                raise ValueError(f"Property {i} header at {hex(prop_offset)} exceeds ADT length {hex(total_len)}")
            
            raw_name = blob[prop_offset:prop_offset+32]
            if b'\0' not in raw_name:
                raise ValueError(f"Property {i} at {hex(prop_offset)} name is not null-terminated")
            name = raw_name.split(b'\0')[0].decode('ascii', errors='replace')
            
            length, = struct.unpack_from('<I', blob, prop_offset+32)
            
            # Critical check: bit 31 flag
            if length & 0x80000000:
                raise ValueError(f"Property '{name}' at {hex(prop_offset)} has bit 31 set: {hex(length)}")
            
            val_offset = prop_offset + 36
            if val_offset + length > total_len:
                raise ValueError(f"Property '{name}' value at {hex(val_offset)} (len {hex(length)}) exceeds ADT length {hex(total_len)}")
            
            if name == 'name':
                val = blob[val_offset:val_offset+length]
                node_name = val.split(b'\0')[0].decode('ascii', errors='replace')
            
            total_props += 1
            
            # XNU next_prop_region calculation:
            # next_addr = (prop + 36 + length + 3) & ~3
            next_prop_offset = (prop_offset + 36 + length + 3) & ~3
            if next_prop_offset > total_len:
                raise ValueError(f"Property '{name}' next_prop_offset {hex(next_prop_offset)} exceeds ADT length {hex(total_len)}")
            
            curr = next_prop_offset

        cur_path = f"{path}/{node_name}"
        # Walk children
        for j in range(nchildren):
            curr = parse_node(curr, cur_path)

        return curr

    end_offset = parse_node(0)
    if end_offset != total_len:
        raise ValueError(f"ADT walk ended at {hex(end_offset)}, but total length is {hex(total_len)}")
    
    return True, total_nodes, total_props

if __name__ == '__main__':
    diag6 = open('/mnt/c/Users/kyro/Downloads/judyln-ios/out-judyln/shim-boot-g7diag6-g710em.img', 'rb').read()
    adt_diag6 = diag6[0x11449c0:0x11449c0 + 12772]
    
    ok, nodes, props = validate_device_tree(adt_diag6)
    print(f"Validation result: ok={ok}, nodes={nodes}, props={props}, len={len(adt_diag6)}")
