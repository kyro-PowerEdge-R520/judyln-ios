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

import struct, zipfile
from pathlib import Path

ZIP_PATH = Path(r"C:\Users\kyro\Downloads\crDroidAndroid-16.0-20261010-judyln-v12.12.zip")

def read_varint(buf, pos):
    val = shift = 0
    while True:
        b = buf[pos]; pos += 1
        val |= (b & 0x7f) << shift
        if not (b & 0x80): return val, pos
        shift += 7

def iter_fields(buf):
    pos, end = 0, len(buf)
    while pos < end:
        tag, pos = read_varint(buf, pos)
        fn, wt = tag >> 3, tag & 7
        if wt == 0: val, pos = read_varint(buf, pos)
        elif wt == 1: val, pos = buf[pos:pos+8], pos + 8
        elif wt == 2:
            ln, pos = read_varint(buf, pos)
            val, pos = buf[pos:pos+ln], pos + ln
        elif wt == 5: val, pos = buf[pos:pos+4], pos + 4
        else: raise ValueError(wt)
        yield fn, wt, val

with zipfile.ZipFile(ZIP_PATH) as zf, zf.open("payload.bin") as f:
    magic, ver, m_sz, sig_sz = struct.unpack(">4sQQI", f.read(24))
    manifest = f.read(m_sz)
    for fn, wt, val in iter_fields(manifest):
        if fn == 13:
            name, sz = "", 0
            for pfn, _, pval in iter_fields(val):
                if pfn == 1: name = pval.decode()
                elif pfn == 7:
                    for sfn, _, sval in iter_fields(pval):
                        if sfn == 1: sz = sval
            print(f"{name:16s} -> {sz:,} bytes")
