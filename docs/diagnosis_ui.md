# UI Bring-Up & Early-Boot Diagnosis (`shim-boot-g7daily7-g710em.img`)

## 1. Executive Summary & Root Causes

Analysis of the `42,356`-byte `SWEETLOG` console capture (`work/sweet-console.txt`), the `16 GiB` HFSX rootfs image (`/var/tmp/ios16-root.img`), the live `/dev/block/sda26` (`userdata`) partition on `LMG710EM8469e82b`, and the `SWEETXNU` kernel binary inside `out-judyln/shim-boot-g7daily7-g710em.img` identified two primary root causes preventing the graphical UI (`backboardd` / `SpringBoard`) from appearing during the captured boot (`Boot 2`):

1. **Uncached, Busy-Spinning UFS Root Block I/O (`ufscache=0`, `ufswait=0`) Blocking `launchd` `BootTasks`**:
   - In `Boot 2` (`sweet-console.txt`), `boot-args` omitted `ufscache=1` and `ufswait=1` (`0069-sweet-ufs-faster.patch`). Without these parameters, `_ufs_scsi` (`file 0x62b1a8` / `VA 0xfffffe00074fcdb8`) performs full `_flush_dcache64` cache flushes across outgoing UTRD/UCD/PRDT descriptors and bounce buffers as well as post-command UCD and bounce-buffer invalidations on every SCSI command, and busy-spins the CPU via `_delay(1)` (`su.wait == 0`) instead of sleeping via `_assert_wait_deadline_with_leeway` + `_thread_block`.
   - Following the dirty reboot after `Boot 1`, `Boot 2` had to replay the `2.9 MiB` HFS+ journal (`3918848..6810624`, lines `130–132`) over uncached UFS I/O, delaying `exec dirs_cleaner` until `30 s` kernel uptime (`[810628574]` Mach ticks = `42.22 s`, line `418`).
   - At `30 s` uptime, `dirs_cleaner` collided directly with `G7 GPU` (`g7gpu=8`, lines `423–449`) and `G7 TOUCH` (`starting in 30 s`, lines `450–459`) hardware bring-up and SMMU fault polling (`lines 460–491`). Consequently, `dirs_cleaner` took **`89.12 seconds`** (`16:00:42.179209` to `16:02:11.302095`, lines `418–510`) to fault in its shared-cache pages and clean `/private/var/dirs_cleaner/`.
   - The final `launchd` `BootTask`, `/usr/libexec/launchd_cache_loader` (`RequireRun=True`, `RequireSuccess=True`), spawned at `16:02:11.674678` (line `544`, Mach ticks `[2528164905]` = `131.68 s`). Because `launchd_cache_loader` links `Security`, `Foundation`, `CoreFoundation`, `IOKit`, `CoreUtils`, and `libobjc.A.dylib` and parses the `795,217`-byte `/System/Library/xpc/launchd.plist` (`195` `4 KiB` blocks), it was still paging in from uncached UFS ~`100 seconds` later when hardware keys (`Power` `key=0` at line `584`, `VolDown` `key=2` at line `586`) triggered reboot into recovery at ~`231 s`. As a result, `launchd` never logged `Early boot complete. Continuing system boot.` and never spawned `LaunchDaemons` (`backboardd`, `SpringBoard`) on `Boot 2`.

2. **Adreno 630 Stage 8 SMMU Context Fault & Console Status Spam (`g7gpu=8`)**:
   - With `g7gpu=8` in `boot-args`, `_g7_gpu_init` (`file 0x635a68` / `VA 0xfffffe0007507678`) spawns `_g7g_thread` (`file 0x635b3c`) and `_g7g_bringup_thread` (`file 0x637a74`), running stages `2`, `3`, `4`, and `8`.
   - On `30h` firmware, stage 8 fails at SMMU context bank 0 initialization (`G7 GPU: stage8 SMMU bank 0 slots 0/1: 0xe00002ca step 4 program 0 route 10 ias 0 oas 36`, `G7 GPU: stage8 full driver bring-up returned -1`, lines `447–448`), and subsequently prints `G7 GPU: stage8: GPU SMMU context failed at step 4 ...` every `10 seconds` (`lines 460–590`).
   - Setting `g7gpu=0` causes `_g7_gpu_init` (`file 0x635a94..0x635a98`, `ldr w8, [x19]; cbz w8, 0xfffffe000750773c`) to return immediately without starting `_g7g_thread` or `_g7g_bringup_thread`. `G7AdrenoAccelerator` (`file 0xbc2c68`) remains unpublished (`registerService()` at `file 0xbc3e90` is never called and `G7AdrenoAccelerator::newUserClient` at `file 0xbc2cfc` returns `0xe00002cd`), ensuring CoreAnimation renders in software via `AppleCLCD` (`1440x3120` stride `5760` at `0x9d400000`, presented as `1125x2436`) and `IOCoreSurfaceRoot` (`SweetSurface`, `0046-sweet-iosurface-iomfb.patch` + `0056-sweet-fb-throttled-present.patch`).

---

## 2. Verification of HFSX Rootfs (`/var/tmp/ios16-root.img`) & Live `userdata` (`/dev/block/sda26`)

All configuration changes from `/var/tmp/mkiosroot.sh` and `/var/tmp/sweet-root-tweaks.py` were verified on `/var/tmp/ios16-root.img` and on the live `/dev/block/sda26` partition:

| Component / Path | Verified State |
| :--- | :--- |
| **Volume Header (`offset 0x400`)** | Case-sensitive journaled HFSX (`sig=0x4858 'HX'`, `version=5`, `blockSize=4096`, `totalBlocks=0x400000` [`16 GiB`], `fileCount=184,161`, `folderCount=137,203`) |
| **`/System/Library/xpc/launchd.plist`** | `uid=0, gid=80, mode=0644, size=795,217 B`, `530` `LaunchDaemons`; `launchd_cache_loader` confirmed as final `BootTask` in `/sbin/launchd` `__TEXT,__config` (`offset 0x6485f`) |
| **`_PanicOnCrash` -> `_PanicOnCrasX`** | `_PanicOnCrash` count = `0`; `_PanicOnCrasX` count = `7` (`containermanagerd`, `remotepairingdeviced`, `lockdown`, `usermanagerd`, `remoted`, `trustd`, `watchdogd`) |
| **`com.apple.CommCenter`** | Removed (`0` entries matching `Label == 'com.apple.CommCenter'`) |
| **`com.apple.backboardd.plist`** | `ProgramArguments=['/usr/libexec/backboardd']`, `UserName='mobile'`, `RunAtLoad=True`, `KeepAlive=True`, `POSIXSpawnType='Interactive'`, `HighPriorityIO=True` |
| **`com.apple.SpringBoard.plist`** | `ProgramArguments=['/System/Library/CoreServices/SpringBoard.app/SpringBoard']`, `UserName='mobile'`, `RunAtLoad=True`, `KeepAlive=True`, `POSIXSpawnType='App'`, `EmbeddedHomeScreen=True`, `ThrottleInterval=5` |
| **Shared Cache (`/System/Library/Caches/com.apple.dyld`)** | `44` hard-linked files (`nlink=2`) from `/private/preboot/Cryptexes/OS/System/Library/Caches/com.apple.dyld` |
| **System Keybag (`/private/var/keybags/systembag.kb`)** | Present (`0:0, 0600, 228 B`), XML plist `{'KeyBagKeys': b'SWEET'}` |
| **Migration Markers (`.migrated`)** | `/private/var/db/{diagnostics,uuidtext,diagnostics/timesync}/.migrated` all present (`272:272, 0644`) |
| **Container Directories (`/private/var/containers`)** | `Bundle` (`33:33 0755`), `Data/System` (`0:0 0755`), `Shared/SystemGroup` (`0:0 0755`), `Temp` (`0:0 0755`) all present; on live `sda26`, `Data/System/E5FD621A-52C4-4861-9FCE-12D3ACB4B6AC/Library/internal/data_ark.plist` (`block 3440640, 459 B`) populated by `mobileactivationd[138]` during `Boot 1`, with activation state selected by ADT `/chosen` security properties (`research-fused=0, security-domain=1, chip-epoch=1, debug-enabled=1`) |
| **Audio & MediaToolbox** | `/Library/Audio/Plug-Ins/HAL.disabled/VirtualAudio.plugin` moved out of `HAL/`; `StartRecorderServer=False` in `MediaToolbox.framework/{D22,D221,Default}/SubServerConfiguration.plist` |
| **Mobile Preferences (`/private/var/mobile/Library/Preferences/`)** | `com.apple.migration.plist` (`LastSystemVersion='20H392'`), `com.apple.springboard.plist` (`BKNoWatchdogs=True`, `MCForceShowCloudConfigurationUI=False`), `com.apple.purplebuddy.plist` (`SetupDone=True`, `SetupFinishedAllSteps=True`, `SetupVersion=11`), `com.apple.purplebuddy.notbackedup.plist` (all 7 `MiniBuddy`/`SilentICDPUpgrade` keys `False`), and `com.apple.managedconfiguration.notbackedup.plist` (`LockdownActivationIndicatesCloudConfigurationAvailable=False`) verified (`501:501, 0600`) |
| **Live `userdata` `Boot 1` vs `Boot 2` & `CrashReporter`** | `Boot 1` (`launchd.log.1`, clean mount) completed `dirs_cleaner` in `13.7 ms` and `launchd_cache_loader` in `327.8 ms`, spawning `SpringBoard[26]` and `backboardd[56]` at `16:00:42.806844`. `/private/var/mobile/Library/Logs/CrashReporter/` (`CNID 4931`) has **zero** daemon or application crash logs. |

---

## 3. Kernel Binary & `boot.img` Patches Applied (`out-judyln/shim-boot-g7daily7-g710em.img`)

### Kernel Binary Capabilities Verified (`SWEETXNU` Mach-O at file offset `0x1323e8`)
- **`ufscache=1` & `ufswait=1` (`0069-sweet-ufs-faster.patch`)**:
  - Parsed in `_sweet_ufs_rootdev` (`file 0x62aac8` / `VA 0xfffffe00074fc6d8`): string `"ufscache"` at `file 0x1c4d87` sets `su.cache` (`_su + 0x35`, `0xfffffe000808862d`), and `"ufswait"` at `file 0x1c4d90` sets `su.wait` (`_su + 0x36`, `0xfffffe000808862e`).
  - Enables `_clean_dcache64` (`0xfffffe00074927d0`) for outgoing DMA writes, 32-byte `ucd.resp` invalidation, and `200 us` thread sleep intervals (`_assert_wait_deadline_with_leeway` + `_thread_block`) after `50 us` spin.
- **`sweetfb_noconsole=1` & `serial=3` (`0067-sweet-console-mute.patch`)**:
  - `AppleCLCD::present` (`file 0xbae804` / `VA 0xfffffe0007a80414`) parses `"sweetfb_noconsole"` (`file 0x27ed71`) on the first frame presentation and sets `_sweet_console_muted = 1` (`0xfffffe0007c154c8`), suppressing on-screen console text drawing in `__cnputs` (`file 0x59e194`) while continuing to append all output to `SWEETLOG` via `_sweet_log_append` (`file 0x59e1c0`).
- **`sweetsample=backboardd,SpringBoard` (`0054-sweet-process-sampler.patch`)**:
  - Parsed in `_sweet_sample_thread` (`file 0x62c108` / `VA 0xfffffe00074fdd18`, string at `file 0x1c50b4`), sampling `backboardd` and `SpringBoard` into `SWEETLOG` after `90 * hz`.

### Patched `out-judyln/shim-boot-g7daily7-g710em.img` Verification
- **File Size**: `18,120,704` bytes (`0x1148000`)
- **Preserved `30h` Memory & ADT Fixes**:
  - `SWEETXNU.mem_size` at `0x132040`: `0x7e0c0000`
  - ADT `/chosen/dram-size` at `0x1144c28`: `0x7e0c0000`
  - ADT `/nram` node name at `0x1147000`: `b'nram\x00'` (`reg` at `0x1147054`: `<0x17e0c0000 0x100000>`)
- **`SWEETXNU.cmdline` (`608` bytes at `0x132048..0x1322a8`, NUL-padded)**:
  - **Before (`346` ASCII bytes + `262` NUL bytes)**:
    ```text
    debug=0xc serial=3 keepsyms=1 -enable_kprintf_spam -noprogress rd=ufsroot0 unentitled_ios_sim_launch=1 ignition_level=1 wdt_test=no_user_checkin ufsrw=1 rootrw=1 launchd_unsecure_cache=1 wdt=-1 sweetfb_noconsole=1 sweetfb_hz=60 sweettouch=0 sweetsample=- g7touch_bar=0 g7touch_init=2 sweetusb=0 cpus=8 sweetsmp=1 g7perf=100 sweetbattery=2 g7gpu=8
    ```
  - **After (`388` ASCII bytes + `220` NUL bytes)**:
    ```text
    debug=0xc serial=3 keepsyms=1 -enable_kprintf_spam -noprogress rd=ufsroot0 unentitled_ios_sim_launch=1 ignition_level=1 wdt_test=no_user_checkin ufsrw=1 ufscache=1 ufswait=1 rootrw=1 launchd_unsecure_cache=1 wdt=-1 sweetfb_noconsole=1 sweetfb_hz=60 sweettouch=0 sweetsample=backboardd,SpringBoard g7touch_bar=0 g7touch_init=2 sweetusb=0 cpus=8 sweetsmp=1 g7perf=100 sweetbattery=2 g7gpu=0
    ```
- **Recomputed `boot.img` v1 Header SHA-1 `id` (`32` bytes at `0x240..0x260`)**:
  - **Before**: `bdfdf9f2e2f1fa1f948583c77dd14fffd99ded2c000000000000000000000000`
  - **After**: `b438fc08c89e7c32a22e8b295e6446566e792570000000000000000000000000`
- **Full Image SHA-256**: `dcf9dcba1f4a3c3fafd51848382a83c68c1543209623ed20ff73621b46388f7a`

---

## 4. Device Flash & Reboot Verification (`LMG710EM8469e82b`)

- Pushed `out-judyln/shim-boot-g7daily7-g710em.img` (`18,120,704` bytes) to `/tmp/boot.img` on `LMG710EM8469e82b`.
- Flashed `/dev/block/bootdevice/by-name/boot_a` (`4424` blocks at `bs=4096`).
- Verified readback SHA-256 on `/dev/block/bootdevice/by-name/boot_a`: `dcf9dcba1f4a3c3fafd51848382a83c68c1543209623ed20ff73621b46388f7a`.
- Issued `adb reboot` to boot into `boot_a`.
