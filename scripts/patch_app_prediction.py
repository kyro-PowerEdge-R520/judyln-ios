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
import struct

def va_to_file_offset(data: bytes, target_va: int) -> int:
    magic, _, _, _, ncmds, sizeofcmds, _, _ = struct.unpack_from("<8I", data, 0)
    assert magic == 0xfeedfacf, "Only 64-bit Mach-O supported"
    off = 32
    for _ in range(ncmds):
        cmd, cmdsize = struct.unpack_from("<II", data, off)
        if cmd == 0x19: # LC_SEGMENT_64
            vmaddr, vmsize, fileoff, filesize = struct.unpack_from("<4Q", data, off + 24)
            if vmaddr <= target_va < vmaddr + vmsize:
                rel = target_va - vmaddr
                if rel < filesize:
                    return fileoff + rel
        off += cmdsize
    return None

def patch_binary(file_path, target_va=None, file_offset=None, out_path=None):
    with open(file_path, "rb") as f:
        data = bytearray(f.read())
    
    if target_va is not None:
        patch_off = va_to_file_offset(data, target_va)
        if patch_off is None:
            patch_off = target_va & 0xFFFFFF
    else:
        patch_off = file_offset

    print(f"[+] Patching file: {file_path} at offset: {hex(patch_off)}")
    print(f"[+] Old bytes: {data[patch_off:patch_off+8].hex()}")
    
    # mov x0, #0 (0xd2800000); ret (0xd65f03c0)
    stub = bytes.fromhex("000080d2c0035fd6")
    data[patch_off:patch_off+len(stub)] = stub
    
    print(f"[+] New bytes: {data[patch_off:patch_off+8].hex()}")
    
    out = out_path or file_path
    with open(out, "wb") as f:
        f.write(data)
    print(f"[+] Successfully wrote patched binary to {out}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 patch_app_prediction.py <path_to_binary> [va_or_offset]")
        sys.exit(1)
    binary = sys.argv[1]
    va = int(sys.argv[2], 0) if len(sys.argv) > 2 else 0x1be13c
    patch_binary(binary, target_va=va)
