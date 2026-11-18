# Boot Image v3-log Analysis & Build Report (`boot-g7em-gpu8-v3-log.img`)

## 1. Image Summary & Integrity Verification

| Image | Size (bytes) | SHA-256 | Android Boot v1 ID (`0x240..0x254`) |
|---|---:|---|---|
| Source Base (`boot-g7em-20j-full.img`) | 18128896 | `376ecdfcbd667f92029c44f86207bcd693eade70086d3bfcff2faf6abe9e1dce` | `17eff122fa155312e4fb96cc789fee144f68f94c` |
| Patched Base (`boot-g7em-gpu8-v3.img`) | 18128896 | `66d493f3fa1f04b7ba3b665cc814d7c46284c7ccb3682e849898f59cd72c6459` | `2e51db36e8c646617ee68cac7aa60cd9eab57d6c` |
| Output (`boot-g7em-gpu8-v3-log.img`) | 18128896 | `89630572d7c56deedf7b4a7bb4e80888782fb7e3091106df013fbca570170eb3` | `fdeddf5c5f8f818faad4083ed81128300e1e7620` |
| Golden (`golden_boot\boot_a-cpu-ui-touch.img`) | 18112512 | `766a88577c208af62583d199fa5dbd8f46811342aa109db5c334a5d38607b3e7` | `08b9b1eeecef061d53f2551691bed4a195ad78b2` |

- Golden read-only verification: **unchanged** (`766a88577c208af62583d199fa5dbd8f46811342aa109db5c334a5d38607b3e7` == `766a88577c208af62583d199fa5dbd8f46811342aa109db5c334a5d38607b3e7`).
- Exact diffs vs `boot-g7em-20j-full.img`: **4 regions** (`0x240..0x254` SHA-1 ID + `0x0bbf1a4`, `0x0bbfa44`, `0x0bbfa98` SMMU patches). Console gates `0x059be7c` and `0x059c1ec` match `boot-g7em-20j-full.img` (`0x34000068`).
- Preserved `SWEETXNU.cmdline` (`0x130048`): `debug=0xc serial=3 keepsyms=1 -noprogress rd=ufsroot0 unentitled_ios_sim_launch=1 ignition_level=1 wdt_test=no_user_checkin ufsrw=1 rootrw=1 launchd_unsecure_cache=1 wdt=-1 sweetfb_hz=60 sweettouch=1 g7touch_bar=0 g7touch_init=2 sweetusb=0 cpus=8 sweetsmp=1 g7perf=100 sweetbattery=2 g7gpu=8 sweetfb_noconsole=1`
- Preserved `seg[10]` (`G7Zap` ELF32): `va=0xfffffe0008508000`, `img_off=0x11429e0`, `fz=0x37b0`; ADT `/chosen/memory-map/G7Zap` at `0x1c4d97`.

## 2. Active & Restored Code Locations (`boot-g7em-gpu8-v3-log.img`)

| File Offset | Virtual Address | Value in `v3` | Value in `v3-log` | Description |
|---:|---|---:|---:|---|
| `0x0059be7c` | `0xfffffe000746fa6c` | `0xd503201f` (`nop`) | `0x34000068` (`cbz w8`) | **Restored** `_console_ring_try_empty` console log visibility before UI present |
| `0x0059c1ec` | `0xfffffe000746fddc` | `0xd503201f` (`nop`) | `0x34000068` (`cbz w8`) | **Restored** `__cnputs` console log visibility before UI present |
| `0x00bbf1a4` | `0xfffffe0007a92d94` | `0x14000003` (`b`) | `0x14000003` (`b`) | **Kept** `_ArmSmmu4KObserveOwnedContext`: ignore latched `CB0_FSR` fault bits in phase 1 & 3 |
| `0x00bbfa44` | `0xfffffe0007a93634` | `0xd503201f` (`nop`) | `0xd503201f` (`nop`) | **Kept** `_global`: bypass `ID0.SMS==0` check on `ID0=0x40016605` in phase 1 & 3 |
| `0x00bbfa98` | `0xfffffe0007a93688` | `0x52800000` (`movz w0,#0`) | `0x52800000` (`movz w0,#0`) | **Kept** `_global`: ignore latched `SMMU_sGFSR` fault status in phase 1 & 3 |
| `0x00000240` | `(boot_hdr+0x240)` | `2e51db36e8c646617ee68cac7aa60cd9eab57d6c` | `fdeddf5c5f8f818faad4083ed81128300e1e7620` | Recomputed Android boot.img v1 SHA-1 ID |

## 3. Post-Phase-1 Analysis (`_ArmSmmu4KAttachStreams` Phase 2/3 & `stage8` Fallback)

### `_ArmSmmu4KAttachStreams` (`0x0bc00c8..0x0bc043c`) Phase Transitions
- Phase assignments verified at: `0x0bc0240` (`0xfffffe0007a93e30`, `phase=2`), `0x0bc03e4` (`0xfffffe0007a93fd4`, `phase=5`), `0x0bc0404` (`0xfffffe0007a93ff4`, `phase=3`), `0x0bc0430` (`0xfffffe0007a94020`, `phase=4`).
- **Phase 2 (`0x0bc0240..0x0bc0404`)**: For `slot 0` and `slot 1`, writes `S2CR[slot] = cb_index | (EXIDS ? 0x400 : 0)` (`0x0`), barriers, verifies readback, writes `SMR[slot] = sid | (mask << 16) | 0x80000000` (`0x80000000`, `0x80000001`), barriers, and verifies readback. Any mismatch transitions to `phase 5` (`0x0bc03e4`) and calls `_quarantine` (`0x0bc043c`) to revert `S2CR` to `0x20000` (`FAULT`) and clear `SMR`, then returns status `7` (`StateMismatch`) or `8` (`IoError`) without hanging.
- **Phase 3 (`0x0bc0404..0x0bc0438`)**: Calls `_observe` (`0x0bbfe58`), which re-runs `_global`, `_ArmSmmu4KObserveOwnedContext` (both carrying the 3 kept patches above), and `_scan(..., quarantine=1)` (verifying programmed `SMR` & `S2CR`). On error, transitions to `phase 5` (`_quarantine`) and returns cleanly; on success, marks `attached=1` and `phase=4`.

### Post-Attach `stage8` Steps & Clean CPU Fallback to `backboardd` / `SpringBoard`
- **Async worker thread**: `_g7g_thread` (`0x0634b64`) launches `_g7g_bringup_thread`, which calls `_g7_adreno_bringup` (`0x0635aac`), prints its return code, and calls `thread_terminate`. Main kernel/userland boot does **not** run `stage8` synchronously on the boot/UI critical path.
- **Bounded post-attach GPU bringup (`_g7_adreno_bringup` `0x0bc19a0..0x0bc1efc`)**: After `NativeAdrenoGpuContext::bringUp` completes step 4 (SMMU attach), `stage8` runs:
  1. `_g7_gpu_sqe` + `_g7_gpu_prepare` (`0x0bc1b3c`, `0x0bc1be4`) — SQE firmware copy & cache clean
  2. `NativeAdrenoRing::attach` + `NativeAdrenoCpInit::run` + `NativeAdrenoRing::wait` (`0x0bc1c4c`, `0x0bc1cd4`, `0x0bc1d08`) — bounded-timeout `CP_ME_INIT` ring test
  3. `_g7_gpu_zap` + `AdrenoPM4Type7` + `NativeAdrenoRing::submit` + `NativeAdrenoRing::wait` (`0x0bc1d70`, `0x0bc1dc0`, `0x0bc1de4`) — `G7Zap` / `CP_SET_SECURE_MODE` check with bounded wait
  4. `NativeAdrenoSubmit::attach` + `NativeAdrenoTimer::attach` (`0x0bc1e2c`, `0x0bc1e54`) — publishes `GPU READY for Metal`
- **Guaranteed CPU fallback**: Every error path in `_g7_adreno_bringup` logs a specific `stage8:` failure string via `_snprintf` and exits through `0x0bc19b0` (`movn w0, #0` = `-1`) without an infinite loop. Until `_g7_adreno_bringup` finishes and sets the ready state, `G7AdrenoAccelerator::newUserClient` / `AGXDeviceUserClient::attachCore` returns `0xe00002c7` (`kIOReturnUnsupported`, `0x0bc0d48`), allowing `backboardd` and `SpringBoard` to continue booting cleanly using `AppleCLCD` CPU framebuffer rendering.
