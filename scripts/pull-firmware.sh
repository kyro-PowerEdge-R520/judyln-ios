#!/bin/bash
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

# pull-firmware.sh: Extract vendor firmware blobs from connected LG G7 ThinQ (judyln)
set -euo pipefail

DEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/firmware"
mkdir -p "${DEST_DIR}/gpu" "${DEST_DIR}/wifi" "${DEST_DIR}/dsp" "${DEST_DIR}/touch"

echo "=== Pulling firmware from LG G7 ThinQ (judyln) ==="

# Check adb device
if ! adb get-state 1>/dev/null 2>&1; then
    echo "Error: LG G7 ThinQ not detected via adb. Please connect phone with USB debugging enabled."
    exit 1
fi

echo "[1/4] Pulling Adreno 630 GPU firmware..."
adb shell "su -c 'cp /vendor/firmware/a630* /sdcard/ 2>/dev/null || true'" || true
adb pull /vendor/firmware/a630_zap.mbn "${DEST_DIR}/gpu/" 2>/dev/null || true
adb pull /vendor/firmware/a630_zap.elf "${DEST_DIR}/gpu/" 2>/dev/null || true
adb pull /vendor/firmware/a630_sqe.fw "${DEST_DIR}/gpu/" 2>/dev/null || true

echo "[2/4] Pulling WCN3990 Wi-Fi/BT firmware..."
adb pull /vendor/firmware/wlan "${DEST_DIR}/wifi/" 2>/dev/null || true
adb pull /vendor/firmware_mnt/image/wlanmdsp.mbn "${DEST_DIR}/wifi/" 2>/dev/null || true
adb pull /vendor/firmware_mnt/image/bdwlan.bin "${DEST_DIR}/wifi/" 2>/dev/null || true

echo "[3/4] Pulling DSP (ADSP / CDSP) firmware..."
adb pull /vendor/firmware_mnt/image/adsp.mbn "${DEST_DIR}/dsp/" 2>/dev/null || true
adb pull /vendor/firmware_mnt/image/cdsp.mbn "${DEST_DIR}/dsp/" 2>/dev/null || true

echo "[4/4] Pulling touch firmware..."
adb pull /vendor/firmware/touch "${DEST_DIR}/touch/" 2>/dev/null || true

echo "Firmware extraction complete into ${DEST_DIR}"
