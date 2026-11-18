# Third-Party Notices & Upstream Attributions

This project gratefully credits the following upstream repositories and open-source components:

## 1. HakiOS (`hakios-xnu-kernel`)
- **Repository:** https://github.com/oosexgang/hakios-xnu-kernel
- **Role:** Kernel bring-up framework, SDM845 device configuration templates (`device.conf`, `soc.args`, `judyln.config`, `judyln_defconfig`), and firmware extraction workflow (`pull-firmware.sh`).

## 2. ios-sweet (`SWEETXNU`)
- **Repository:** https://github.com/dipa-studio/ios-sweet
- **Role:** `SWEETXNU` bootloader shim architecture, SDM845 platform drivers (`SweetFB`/`AppleCLCD`, `SweetTouch`, `SweetUSB`, `SweetBattery`, `SweetSMP`, `SweetSurface`, `ArmSmmu4K`), and device boot-arg conventions.

## 3. Apple OSS Distributions (`xnu`)
- **Repository:** https://github.com/apple-oss-distributions/xnu
- **License:** Apple Public Source License 2.0 (APSL-2.0)
- **Role:** Upstream XNU kernel architecture, IOKit registry/matching subsystems, and Mach-O kernelcache layout referenced by the diagnostic and patching scripts.

## 4. Android Open Source Project (`mkbootimg.py`)
- **File:** `scripts/third_party/mkbootimg.py`
- **Copyright:** Copyright 2015, The Android Open Source Project
- **License:** Apache License, Version 2.0 (`Apache-2.0`)
- **Note:** Preserved unmodified with its original copyright and license header.
