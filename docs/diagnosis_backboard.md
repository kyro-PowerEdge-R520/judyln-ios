# Diagnosis & Fix: backboardd & Framebuffer Bring-Up Analysis

## 1. Previous Boot Execution Summary (`sweet-console4.txt` / `sweet-console_latest.txt`)
- In the latest boot, `launchd` completed all `BootTasks`:
  - `mount`, `seputil`, `mobile_obliterator`, `MSUEarlyBootTask`, `cc_fips_test` passed.
  - `keybagd` ran and completed `MKB_INIT` successfully (`System Keybag loaded`, `DONE MKB_INIT`).
  - `usermanagerd`, `dirs_cleaner`, `init_featureflags`, `tzinit`, `FinishRestoreFromBackup`, `sysstatuscheck`, `prng_seedctl` executed cleanly.
  - `launchd_cache_loader` completed and reported:
    `Cache sent to launchd successfully`
    `Early boot complete. Continuing system boot.`
- Following `Early boot complete`, `launchd` spawned `LaunchDaemons`:
  - `UserEventAgent`, `logd`, `routined`, `keybagd`, `configd`, `DumpPanic`, `runningboardd`, `mediaserverd`, `usermanagerd`, `locationd`, `fseventsd`, `lockdownd`, `notifyd`, `amfid`, `timed`, `dasd`.
  - `SpringBoard` and `backboardd` were spawned.
  - No kernel panic, memory abort, or crash dump occurred.

## 2. Display / Console Interleaving Analysis
- `0003-sweet-framebuffer-serial-console.patch` and `0012-sweet-keep-debug-console-after-ttbr0.patch` register `sweet_fbcon` as the early console when `serial=3` is present.
- `0067-sweet-console-mute.patch` sets `sweet_console_muted = 1` only upon the first frame swap (`AppleCLCD::present`).
- While `serial=3` was in `boot-args`, all kprintf and daemon stdout/stderr messages continued rendering via `sweet_fbcon` font rasterization onto the physical continuous splash buffer (`0x9d400000`).
- Removing `serial=3` disables the early fbcon serial driver redirection, allowing the display framebuffer to remain unpolluted by console text rendering.
- `sweetfb_noconsole=1` remains active to ensure console mutes upon GUI presentation.

## 3. Applied Changes to `out-judyln/shim-boot-g7daily7-g710em.img`
- `SWEETXNU.cmdline` at offset `0x132048` (608 bytes, NUL-padded):
  - Removed: `serial=3`
  - Maintained: `debug=0xc keepsyms=1 -enable_kprintf_spam -noprogress rd=ufsroot0 unentitled_ios_sim_launch=1 ignition_level=1 wdt_test=no_user_checkin ufsrw=1 rootrw=1 launchd_unsecure_cache=1 wdt=-1 sweetfb_noconsole=1 sweetfb_hz=60 sweettouch=0 sweetsample=backboardd,SpringBoard g7touch_bar=0 g7touch_init=2 sweetusb=0 cpus=8 sweetsmp=1 g7perf=100 sweetbattery=2 g7gpu=0`
  - `30h` DRAM limit (`0x7e0c0000`) and ADT `b'nram\x00'` intact.
- Recomputed boot.img v1 SHA-1 ID at `0x240`: `7bdada57698ff4d587762cefea765c78415a6de3`.
- Total image size: 18,120,704 bytes.
- Image SHA-256: `82cc827a6b113681d8ff24f08c54b164bccaa0c765cfb7d2cf87ba61f9aff584`.

## 4. Flashing & Verification
- Pushed to `/tmp/boot.img` on device via ADB recovery.
- Written directly to `/dev/block/bootdevice/by-name/boot_a` (4424 blocks of 4096 bytes).
- Verified block device readback checksum matching SHA-256 `82cc827a...`.
- Issued `adb reboot`.
