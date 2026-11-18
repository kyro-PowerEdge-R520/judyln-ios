# G710EM (`judyln`) Early Framebuffer Stall Diagnosis & Fix

## 1. Current State of Patched Boot Image & Rootfs (`userdata`)

### 1.1 `out-judyln/shim-boot-g7diag6-g710em.img` (`18,120,704` bytes)
- Verified `boot.img` v1 header (`ANDROID!`, `page_size=4096`, `hdr_ver=1`, `hdr_sz=1648`, `kernel_size=0x1309c1`, `ramdisk_size=0x1015bb0`, `second_size=0`, `ramdisk_offset=0x132000`).
- `SWEETXNU` header sits at file offset `0x132000`, with the 512-byte zero-padded `boot_args` buffer at `0x132048`.
- `boot_args` was patched earlier in-place (`331` bytes + zero padding) and verified active:
  ```text
  debug=0x10c -v serial=3 keepsyms=1 -enable_kprintf_spam -noprogress rd=ufsroot0 unentitled_ios_sim_launch=1 ignition_level=1 wdt_test=no_user_checkin ufsrw=1 rootrw=1 launchd_unsecure_cache=1 wdt=-1 sweetfb_hz=60 sweettouch=0 sweetsample=- g7touch_bar=0 g7touch_init=2 sweetusb=0 cpus=8 sweetsmp=1 g7perf=100 sweetbattery=2 g7gpu=8
  ```
- Re-flashing `boot_a` with `debug=0x10c -v` succeeded (`17696 KB`, `0.635s`, exit code `0`), yet the framebuffer output still stopped right after:
  - `kprintf initialized.`
  - `Serial mode specified: 000000000` (clipped on left bezel edge as `..arial code specified: 000000000`)

### 1.2 Root Filesystem on `userdata`
- `rd=ufsroot0` (with `ufsrw=1 rootrw=1` and no `ufsroot=` override) maps to the GPT partition named **`userdata`** on UFS LUN 0 (`0x1d84000`, per `0028-sweet-ufs-root-device.patch`).
- Earlier in this session, the `16 GiB` journaled case-sensitive `HFS+` rootfs image built from the local `20H392` IPSW via `mkiosroot.sh` and `sweet-root-tweaks.py` (with unpacked `dyld_shared_cache` and userland binaries) was converted to `out-judyln/ios16-root.simg` (`12,145,430,840` bytes) and flashed across all `47/47` sparse chunks to `userdata` (`387.933s`, exit code `0`). No re-flash of `userdata` is needed.

---

## 2. Live Phone vs. `G710EM30h` KDZ Firmware Comparison

Byte-for-byte comparison (after stripping trailing zero-padding) between live partitions pulled via OrangeFox (`backups/phone-live/`) and partitions extracted from `G710EM30h_00_OPEN_EU_OP_0927.kdz` (`backups/kdz-30h/`):

| Partition | Live Trimmed Size | KDZ `30h` Trimmed Size | Equal (`trimmed_equal`) | Version / Variant Strings |
| --- | ---: | ---: | --- | --- |
| `xbl_a.img` | `3,006,809` | `3,006,809` | `True` | `QC_IMAGE_VERSION_STRING=BOOT.XF.2.0.c3-00002-SDM845LZB-1.223228.1`, `IMAGE_VARIANT_STRING=SDM845LA`, `OEM_IMAGE_VERSION_STRING=MCSBS9R13` |
| `tz_a.img` | `2,043,903` | `2,043,903` | `True` | `QC_IMAGE_VERSION_STRING=TZ.XF.5.0.1.C5-00142`, `IMAGE_VARIANT_STRING=WAXAANAAA`, `OEM_IMAGE_VERSION_STRING=CRM` |
| `hyp_a.img` | `369,340` | `369,340` | `True` | `QC_IMAGE_VERSION_STRING=TZ.XF.5.0.1.C5-00142`, `IMAGE_VARIANT_STRING=WAXAANAAA`, `OEM_IMAGE_VERSION_STRING=CRM` |
| `abl_a.img` | `221,184` | `221,184` | `True` | — |
| `dtbo_a.img` | `8,388,580` | `8,388,579` | `False` | `dtbo_idx=6` (`judyln_lao`) |

The connected `LM-G710EM` is running exact `G710EM30h` (`BOOT.XF.2.0.c3-00002-SDM845LZB-1.223228.1` / `TZ.XF.5.0.1.C5-00142`) bootloaders and TrustZone/Hypervisor. No older (`8.x`/`9.x`) `judyln` firmware partitions exist in the workspace.

---

## 3. FDT `/reserved-memory` & ADT Memory Map Diff

### 3.1 Base DTB `/reserved-memory` Regions (Original `shim-boot-g7diag6.img` vs. `30h` Base DTB + `dtbo_a[6]`)
Both the original DTB in `shim-boot-g7diag6.img` and the `30h` base DTB define identical lower/mid fixed `/reserved-memory` ranges:

| Region | Start | End | Size | Source |
| --- | --- | --- | --- | --- |
| `hyp_region@85700000` | `0x85700000` | `0x85d00000` | `0x600000` | Original DTB & `30h` Base DTB |
| `xbl_region@85e00000` | `0x85e00000` | `0x85f00000` | `0x100000` | Original DTB & `30h` Base DTB |
| `removed_region@85fc0000` | `0x85fc0000` | `0x88f00000` | `0x2f40000` | Original DTB & `30h` Base DTB |
| `qseecom_region@0x8ab00000` | `0x8ab00000` | `0x8bf00000` | `0x1400000` | Original DTB & `30h` Base DTB |
| `camera_region@0x8bf00000` | `0x8bf00000` | `0x8c400000` | `0x500000` | Original DTB & `30h` Base DTB |
| `ips_fw_region@0x8c400000` | `0x8c400000` | `0x8c410000` | `0x10000` | Original DTB & `30h` Base DTB |
| `ipa_gsi_region@0x8c410000` | `0x8c410000` | `0x8c415000` | `0x5000` | Original DTB & `30h` Base DTB |
| `gpu_region@0x8c415000` | `0x8c415000` | `0x8c417000` | `0x2000` | Original DTB & `30h` Base DTB |
| `adsp_region@0x8c500000` | `0x8c500000` | `0x8df00000` | `0x1a00000` | Original DTB & `30h` Base DTB |
| `wlan_fw_region@0x8df00000` | `0x8df00000` | `0x8e000000` | `0x100000` | Original DTB & `30h` Base DTB |
| `modem_region@0x8e000000` | `0x8e000000` | `0x95800000` | `0x7800000` | Original DTB & `30h` Base DTB |
| `video_region@0x95800000` | `0x95800000` | `0x95d00000` | `0x500000` | Original DTB & `30h` Base DTB |
| `cdsp_region@0x95d00000` | `0x95d00000` | `0x96500000` | `0x800000` | Original DTB & `30h` Base DTB |
| `mba_region@0x96500000` | `0x96500000` | `0x96700000` | `0x200000` | Original DTB & `30h` Base DTB |
| `slpi_region@0x96700000` | `0x96700000` | `0x97b00000` | `0x1400000` | Original DTB & `30h` Base DTB |
| `pil_spss_region@0x97b00000` | `0x97b00000` | `0x97c00000` | `0x100000` | Original DTB & `30h` Base DTB |
| `cont_splash_region@9d400000` | `0x9d400000` | `0x9f800000` | `0x2400000` | Original DTB & `30h` Base DTB |
| `ramoops_region@b0000000` | `0xb0000000` | `0xb0100000` | `0x100000` | Added by `dtbo_a[6]` |
| `crash_fb_mem@b0100000` | `0xb0100000` | `0xb1900000` | `0x1800000` | Added by `dtbo_a[6]` |

### 3.2 Upper DDR (`0x100000000+`) and `/pram` Boundary
- On the live `30h` device, the shim red-screen output displays `PHYS base=[1]00000000 size=7E1C0000`.
- `SWEETXNU` and the embedded ADT previously configured:
  - `/chosen/dram-base = 0x100000000`
  - `SWEETXNU.mem_size` (`0x132040`) = `0x7e1c0000`
  - `/chosen/dram-size` (`0x1144c28`) = `0x7e1c0000` (giving `0x100000000..0x17e1c0000`)
  - `/pram` `reg` (`0x1147054`) = `<0x17e1c0000 0x100000>` (`0x17e1c0000..0x17e2c0000`)
- Because `0x17e1c0000..0x180000000` lies in the top-of-RAM TZ/HYP/XPU carveout on `TZ.XF.5.0.1.C5-00142` (`30h`), `/pram` was mapped directly onto protected memory at `0x17e1c0000`.

---

## 4. Exact Execution Trace After `Serial mode specified: %08X\n`

Disassembly of the `SWEETXNU` Mach-O (`__TEXT_EXEC` at `0xfffffe00072f8000`) immediately after `Serial mode specified: %08X\n` (`0xfffffe0007b09170`):

1. `0xfffffe0007b0923c`: `bl _switch_to_serial_console` (`0xfffffe000746f5a0` -> immediate `ret` at `0xfffffe000746f5c0`)
2. `0xfffffe0007b0924c`: `bl _PE_create_console` (`0xfffffe0007aacec4`):
   - Looks up ADT `/pram` (`reg` = `<0x17e1c0000 0x100000>`)
   - `0xfffffe0007aacf6c`: `bl _ml_io_map_wcomb` (maps `/pram`)
   - `0xfffffe0007aacfa0`: `ldr w9, [x0]` (reads first 32-bit word of mapped `/pram`)
   - `0xfffffe0007aacfe8`: `bl _bzero` (zeroes `0x100000` bytes of `/pram`)
   - `0xfffffe0007aad004`: `bl _initialize_screen` (`0xfffffe0007473068`, which prints `initialize_screen: b=%08llX, ...` at `0xfffffe0007473180`)
3. `0xfffffe0007b09254`: `bl _PE_init_printf` (`b _vcattach` -> enables `vcattach` video console text output)
4. `0xfffffe0007b0925c`: `bl _cpu_machine_idle_init`
5. `0xfffffe0007b0926c`: `bl _PE_init_platform` -> `0xfffffe0007aacb9c`: `bl _pe_arm_init_interrupts` (`kprintf("pe_arm_init_interrupts: args: %p\n")`)
6. `0xfffffe0007b09290`: `bl _PE_init_cpu` -> `0xfffffe0007aab4f4`: `b _pe_init_fiq` (`kprintf("SWEET GIC: virtual timer INTID %u\n")`)

**Root cause of the stop right after `Serial mode specified: 000000000`:**
Because neither `initialize_screen: b=...` nor `pe_arm_init_interrupts: ...` nor `SWEET GIC: ...` appeared even with `debug=0x10c -v`, execution faulted inside `_PE_create_console` when reading/zeroing `/pram` (`0x17e1c0000..0x17e2c0000`) inside the `30h` TZ/XPU-protected region above `0x17e1c0000`, before reaching `_initialize_screen`, `_vcattach`, `_PE_init_platform`, `_pe_arm_init_interrupts`, or `_pe_init_fiq`.

---

## 5. Fix Selected & Applied: Option A

Option A directly relocates `/pram` below `0x17e1c0000` inside `out-judyln/shim-boot-g7diag6-g710em.img` without rebuilding the kernel or regenerating the ADT from scratch (Option B only controls the uncompressed ADT properties and is equivalent once `SWEETXNU.mem_size`, `/chosen/dram-size`, and `/pram/reg` are updated):

Applied to `c:\Users\kyro\Downloads\judyln-ios\out-judyln\shim-boot-g7diag6-g710em.img` (`18,120,704` bytes):
- `SWEETXNU.mem_size` (`0x132040`): `0x7e1c0000` → **`0x7e0c0000`** (dram range `0x100000000..0x17e0c0000`)
- ADT `/chosen/dram-size` (`0x1144c28`): `0x7e1c0000` → **`0x7e0c0000`**
- ADT `/pram/reg` (`0x1147054`): `<0x17e1c0000 0x100000>` → **`<0x17e0c0000 0x100000>`** (placed inside unreserved upper DDR just below `0x17e1c0000`)
- `boot_args` (`0x132048`): retained `debug=0x10c -v serial=3 ...`
- `boot.img` v1 header SHA-1 `id` (`0x240`): recomputed as `8deb3813b5e3d6357c8b8f9271e87fffb1ecf63b000000000000000000000000`

### Next Flash Step
`fastboot.exe devices` showed no device currently in fastboot mode (phone is still on the XNU console). Hold **Volume Down + Power** until the screen turns black, keep holding **Volume Down** to enter fastboot, and then flash `boot_a` with the updated `out-judyln/shim-boot-g7diag6-g710em.img` and reboot.

---

## 6. `/pram` Bypass Patch Confirmation (`"pram\x00"` → `"nram\x00"`)

- In `c:\Users\kyro\Downloads\judyln-ios\out-judyln\shim-boot-g7diag6-g710em.img` (`18,120,704` bytes), renamed the ADT node `name` property value at file offset `0x1147000` in-place from `b'pram\x00'` to `b'nram\x00'` (identical 5-byte length; zero offset shifts).
- Recomputed the `boot.img` v1 header SHA-1 `id` field at offset `0x240` (`576`): `102b069b446d9a0b750f94d1852a95f6e2cf637a000000000000000000000000`.
- Re-reading the file verified `len == 18120704` and `data[0x1147000:0x1147005] == b'nram\x00'`.
