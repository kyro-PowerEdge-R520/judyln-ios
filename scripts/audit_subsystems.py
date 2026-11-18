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

import re
from pathlib import Path

img = Path(r"golden_boot\boot_a-cpu-ui-touch.img").read_bytes()

# 1. Extract all sweet* and g7* boot-arg strings from kernel strings region
args = sorted(set(re.findall(rb"\b(?:sweet|g7)[a-z0-9_]{1,28}\b", img[0x130000:0x424410])))
print("=== Kernel sweet*/g7* strings & boot-args ===")
print(", ".join(a.decode() for a in args))

# 2. Extract Sweet* and G7* IOKit C++ class names
classes = sorted(set(re.findall(rb"\b(?:Sweet|G7)[A-Za-z0-9_]{3,36}\b", img[0x130000:0x424410])))
print("\n=== Compiled Sweet*/G7* Driver Classes ===")
print(", ".join(c.decode() for c in classes))

# 3. Check WLAN / Audio / USB keywords in kernel
for tag, pat in [
    ("WLAN/Wi-Fi", rb"\b(?:wcn3990|wlanmdsp|bdwlan|sn012776|ath10k|icnss|AppleBCMWLAN|SweetWLAN|G7Wifi)[A-Za-z0-9_.-]*\b"),
    ("Audio", rb"\b(?:wcd9340|tavil|slimbus|adsp|SweetAudio|G7Audio|AppleEmbeddedAudio)[A-Za-z0-9_.-]*\b"),
    ("USB", rb"\b(?:dwc3|usbmux|SweetUSB|G7Usb|AppleSynopsysOTG|IOUSBDevice)[A-Za-z0-9_.-]*\b"),
]:
    hits = sorted(set(re.findall(pat, img[0x130000:0x424410], re.I)))
    print(f"\n=== {tag} symbols/strings ({len(hits)}) ===")
    print(", ".join(h.decode(errors="replace") for h in hits[:35]))

# 4. List staged firmware files in workspace
fw = [str(p) for p in Path(".").rglob("*") if p.suffix.lower() in (".mbn", ".bin", ".tlv", ".elf", ".mdt")]
print("\n=== Staged Firmware Files in Workspace ===")
print("\n".join(fw[:30]) if fw else "(none found in current tree)")
