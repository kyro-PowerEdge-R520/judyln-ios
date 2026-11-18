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

import hashlib
import os
import struct

GOLD = r"C:\Users\kyro\Downloads\judyln-ios\golden_boot\boot_a-cpu-ui-touch.img"
OUT_DIR = r"C:\Users\kyro\Downloads\judyln-ios\work\next-gen"
DST = os.path.join(OUT_DIR, "boot-g7em-ui-ready.img")
NOTE = os.path.join(OUT_DIR, "ui_ready_notes.md")
GOLD_EXPECTED_SHA256 = "766a88577c208af62583d199fa5dbd8f46811342aa109db5c334a5d38607b3e7"


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def calc_bootimg_sha1(buf):
    ksz, _, rsz, _, ssz, _, _, pg, hver, _ = struct.unpack_from("<10I", buf, 8)
    rdtbo_sz, _, _ = struct.unpack_from("<IQI", buf, 1632)

    def align(n):
        return ((n + pg - 1) // pg) * pg

    k_off = pg
    r_off = k_off + align(ksz)
    s_off = r_off + align(rsz)

    h = hashlib.sha1()
    h.update(buf[k_off : k_off + ksz])
    h.update(struct.pack("<I", ksz))
    h.update(buf[r_off : r_off + rsz])
    h.update(struct.pack("<I", rsz))
    h.update(buf[s_off : s_off + ssz])
    h.update(struct.pack("<I", ssz))
    # golden_boot has hver=1, rdtbo_sz=0 and omits empty recovery_dtbo from ID hash
    return h.digest()


def main():
    raw = open(GOLD, "rb").read()
    assert len(raw) == 18112512, f"Unexpected size {len(raw)}"
    gold_sha256 = sha256_bytes(raw)
    assert gold_sha256 == GOLD_EXPECTED_SHA256, f"Golden SHA-256 mismatch: {gold_sha256}"

    assert raw[0:8] == b"ANDROID!"
    assert raw[0x130000:0x130008] == b"SWEETXNU"

    cmdline = raw[0x130048:0x1302A0].split(b"\x00", 1)[0].decode("ascii")
    tokens = cmdline.split()
    required = [
        "sweetusb=0",
        "g7gpu=0",
        "sweetfb_noconsole=1",
        "sweetfb_hz=60",
        "sweettouch=1",
        "g7touch_bar=0",
        "g7touch_init=2",
    ]
    forbidden = ["sweetusb=1", "sweetusb=2", "g7gpu=8"]
    for tok in required:
        assert tok in tokens, f"Missing required token {tok}"
    for tok in forbidden:
        assert tok not in tokens, f"Unexpected forbidden token {tok}"

    hdr_sha1 = raw[0x240:0x254]
    calc_sha1 = calc_bootimg_sha1(raw)
    assert hdr_sha1 == calc_sha1, f"Header SHA-1 mismatch: {hdr_sha1.hex()} vs {calc_sha1.hex()}"

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(DST, "wb") as f:
        f.write(raw)

    out = open(DST, "rb").read()
    assert len(out) == 18112512
    assert out == raw, "Output image does not match golden baseline byte-for-byte"
    dst_sha256 = sha256_bytes(out)
    assert dst_sha256 == GOLD_EXPECTED_SHA256

    gold_after_sha256 = sha256_bytes(open(GOLD, "rb").read())
    assert gold_after_sha256 == GOLD_EXPECTED_SHA256

    notes = [
        "# UI-Ready Boot Image Verification Notes (`boot-g7em-ui-ready.img`)",
        "",
        "## Image Paths & Checksums",
        "",
        f"- **Source (read-only baseline)**: `{GOLD}`",
        f"- **Output (verified UI-ready copy)**: `{DST}`",
        f"- **File Size**: `{len(out)}` bytes",
        f"- **Byte-for-Byte Match vs. Golden Baseline**: `True` (`out == golden`)",
        f"- **Source SHA-256**: `{gold_after_sha256}`",
        f"- **Output SHA-256**: `{dst_sha256}`",
        f"- **Android Boot Header v1 SHA-1 ID (`0x240..0x254`)**: `{hdr_sha1.hex()}` (matches recomputed payload digest `{calc_sha1.hex()}`)",
        "",
        "## Verified Boot Configuration (`SWEETXNU.cmdline` @ `0x130048`)",
        "",
        f"```text\n{cmdline}\n```",
        "",
        "- Required tokens present: `sweetusb=0`, `g7gpu=0`, `sweetfb_noconsole=1`, `sweetfb_hz=60`, `sweettouch=1`, `g7touch_bar=0`, `g7touch_init=2`",
        "- Excluded tokens absent: `sweetusb=1`, `sweetusb=2`, `g7gpu=8`",
    ]
    with open(NOTE, "w", encoding="utf-8") as f:
        f.write("\n".join(notes) + "\n")

    print("Done: boot-g7em-ui-ready.img verified.")


if __name__ == "__main__":
    main()
