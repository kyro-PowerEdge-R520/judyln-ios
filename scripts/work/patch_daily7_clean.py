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

import sys, os, struct, hashlib
sys.path.insert(0, '/mnt/c/Users/kyro/Downloads/judyln-ios')
sys.path.insert(0, '/mnt/c/Users/kyro/Downloads/lancelot-ios/ios-sweet/tools')
import adt
from work.validate_adt import validate_device_tree

diag6_path = '/mnt/c/Users/kyro/Downloads/judyln-ios/out-judyln/shim-boot-g7diag6-g710em.img'
daily7_path = '/mnt/c/Users/kyro/Downloads/judyln-ios/out-judyln/shim-boot-g7daily7-g710em.img'

diag6_data = open(diag6_path, 'rb').read()
d = bytearray(open(daily7_path, 'rb').read())
assert len(d) == 18120704

# 1. Extract known-good 12,772-byte ADT from diag6
adt_off = 0x11449c0
clean_adt = diag6_data[adt_off : adt_off + 12772]
assert len(clean_adt) == 12772

# Validate with our strict C-equivalent device_tree bounds validator
ok, nodes, props = validate_device_tree(clean_adt)
assert ok and nodes == 23 and props == 295, f"Validation failed: ok={ok}, nodes={nodes}, props={props}"
print(f"Clean ADT strictly validated: nodes={nodes}, props={props}, len={len(clean_adt)}")

# Write clean ADT to daily7 and zero-pad to 0x1148000
avail = len(d) - adt_off
d[adt_off : adt_off + len(clean_adt)] = clean_adt
d[adt_off + len(clean_adt) : len(d)] = b'\x00' * (avail - len(clean_adt))

# Update adt_size in SWEETXNU header at 0x132028
struct.pack_into('<Q', d, 0x132028, len(clean_adt))
print('Updated adt_size in SWEETXNU header to:', len(clean_adt))

# Verify mem_size in SWEETXNU header at 0x132040
struct.pack_into('<Q', d, 0x132040, 0x7e0c0000)
print('Verified mem_size in SWEETXNU header: 0x7e0c0000')

# 2. Update cmdline at 0x132048 (608 bytes, NUL-padded)
cmdline_off = 0x132048
cmdline_len = 608
new_cmd = 'debug=0xc serial=3 keepsyms=1 -enable_kprintf_spam -noprogress rd=ufsroot0 unentitled_ios_sim_launch=1 ignition_level=1 wdt_test=no_user_checkin ufsrw=1 rootrw=1 launchd_unsecure_cache=1 wdt=-1 sweetfb_hz=60 sweettouch=0 sweetsample=backboardd,SpringBoard,containermanagerd sweetiolog=backboardd,SpringBoard,containermanagerd g7touch_bar=0 g7touch_init=2 sweetusb=0 cpus=8 sweetsmp=1 g7perf=100 sweetbattery=2 g7gpu=0 sweetfb_noconsole=1'
assert len(new_cmd) < cmdline_len
d[cmdline_off : cmdline_off + cmdline_len] = new_cmd.encode().ljust(cmdline_len, b'\x00')
print('Updated cmdline:', new_cmd)

# 3. Recompute boot.img v1 SHA-1 ID at 0x240
ks, ka, rs, ra, ss, sa, ta, ps = struct.unpack_from('<8I', d, 8)
hv, = struct.unpack_from('<I', d, 0x28)
rdo_sz, = struct.unpack_from('<I', d, 0x640)
def al(x): return (x + ps - 1) // ps * ps
o = ps; k = d[o:o+ks]; o += al(ks)
r = d[o:o+rs]; o += al(rs)
s = d[o:o+ss]; o += al(ss)
h = hashlib.sha1()
for blob in (k, r, s):
    h.update(blob); h.update(struct.pack('<I', len(blob)))
if hv >= 1:
    ro = d[o:o+rdo_sz]; h.update(ro); h.update(struct.pack('<I', len(ro)))

new_id = h.digest().ljust(32, b'\x00')
d[0x240:0x260] = new_id
print('New boot.img v1 SHA-1 ID:', new_id.hex())

# 4. Save and verify
open(daily7_path, 'wb').write(d)
assert os.path.getsize(daily7_path) == 18120704
sha256 = hashlib.sha256(d).hexdigest()
print('Successfully saved daily7 image! SHA256:', sha256)
