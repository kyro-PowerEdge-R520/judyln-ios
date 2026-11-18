# Boot Image v3 Analysis & Patch Report (`boot-g7em-gpu8-v3.img`)

## 1. Image Summary & Integrity Verification

| Artifact | Size (bytes) | SHA-256 | Android Boot v1 ID (`0x240..0x254`) |
|---|---:|---|---|
| Source (`work\next-gen\boot-g7em-20j-full.img`) | 18128896 | `376ecdfcbd667f92029c44f86207bcd693eade70086d3bfcff2faf6abe9e1dce` | `17eff122fa155312e4fb96cc789fee144f68f94c` |
| Output (`work\next-gen\boot-g7em-gpu8-v3.img`) | 18128896 | `66d493f3fa1f04b7ba3b665cc814d7c46284c7ccb3682e849898f59cd72c6459` | `2e51db36e8c646617ee68cac7aa60cd9eab57d6c` |
| Golden (`golden_boot\boot_a-cpu-ui-touch.img`) | 18112512 | `766a88577c208af62583d199fa5dbd8f46811342aa109db5c334a5d38607b3e7` | `08b9b1eeecef061d53f2551691bed4a195ad78b2` |

- Golden read-only guard: **verified unchanged** (`766a88577c208af62583d199fa5dbd8f46811342aa109db5c334a5d38607b3e7` == `766a88577c208af62583d199fa5dbd8f46811342aa109db5c334a5d38607b3e7`).
- Total differing bytes between `boot-g7em-20j-full.img` and `boot-g7em-gpu8-v3.img`: **38 bytes** (20 bytes boot header SHA-1 ID + 20 bytes ARM64 instruction patches).

### Preserved Resources & Boot Arguments
- `SWEETXNU.cmdline` (`0x130048`): `debug=0xc serial=3 keepsyms=1 -noprogress rd=ufsroot0 unentitled_ios_sim_launch=1 ignition_level=1 wdt_test=no_user_checkin ufsrw=1 rootrw=1 launchd_unsecure_cache=1 wdt=-1 sweetfb_hz=60 sweettouch=1 g7touch_bar=0 g7touch_init=2 sweetusb=0 cpus=8 sweetsmp=1 g7perf=100 sweetbattery=2 g7gpu=8 sweetfb_noconsole=1`
- `seg[10]` (`G7Zap` ELF32): `va=0xfffffe0008508000`, `vs=0x4000`, `img_off=0x11429e0`, `fz=0x37b0`, `e_type=2`, `e_machine=0xa4`, `e_entry=0x5000`, `e_phoff=52`, `e_phnum=3`
- ADT `/chosen/memory-map/G7Zap` string offset: `0x1c4d97`

## 2. Comparison vs. `golden_boot\boot_a-cpu-ui-touch.img` (Console Suppression)

- Linux kernel shim + appended DTB (`0x1000..0x130000`) identical: **True**
- Source `SWEETXNU.cmdline`: `debug=0xc serial=3 keepsyms=1 -noprogress rd=ufsroot0 unentitled_ios_sim_launch=1 ignition_level=1 wdt_test=no_user_checkin ufsrw=1 rootrw=1 launchd_unsecure_cache=1 wdt=-1 sweetfb_hz=60 sweettouch=1 g7touch_bar=0 g7touch_init=2 sweetusb=0 cpus=8 sweetsmp=1 g7perf=100 sweetbattery=2 g7gpu=8 sweetfb_noconsole=1`
- Golden `SWEETXNU.cmdline`: `debug=0xc serial=3 keepsyms=1 -noprogress rd=ufsroot0 unentitled_ios_sim_launch=1 ignition_level=1 wdt_test=no_user_checkin ufsrw=1 rootrw=1 launchd_unsecure_cache=1 wdt=-1 sweetfb_hz=60 sweettouch=1 g7touch_bar=0 g7touch_init=2 sweetusb=0 cpus=8 sweetsmp=1 g7perf=100 sweetbattery=2 g7gpu=0 sweetfb_noconsole=1`

| Segment | Virtual Address | Source Img Offset | Golden Img Offset | File Size | Byte-for-Byte Equal |
|---:|---|---:|---:|---:|---|
| `seg[0]` | `0xfffffe0007004000` | `0x0130408` | `0x01303e8` | `0x170000` | True |
| `seg[1]` | `0xfffffe0007174000` | `0x02a0410` | `0x02a03f0` | `0x184000` | True |
| `seg[2]` | `0xfffffe00072f8000` | `0x0424410` | `0x04243f0` | `0x874000` | True |
| `seg[3]` | `0xfffffe0007b6c000` | `0x0c98410` | `0x0c983f0` | `0x004000` | True |
| `seg[4]` | `0xfffffe0007b70000` | `0x0c9c410` | `0x0c9c3f0` | `0x004000` | True |
| `seg[5]` | `0xfffffe0007b74000` | `0x0ca0410` | `0x0ca03f0` | `0x004000` | True |
| `seg[6]` | `0xfffffe0007b78000` | `0x0ca4410` | `0x0ca43f0` | `0x048000` | True |
| `seg[7]` | `0xfffffe00080b0000` | `0x0cec410` | `0x0cec3f0` | `0x04c000` | True |
| `seg[8]` | `0xfffffe00080fc000` | `0x0d38410` | `0x0d383f0` | `0x04c000` | True |
| `seg[9]` | `0xfffffe0008148000` | `0x0d84410` | `0x0d843f0` | `0x3be5c8` | True |

### Why Console Text Still Rendered on Screen in `v2` (`g7gpu=8`)
- Both images contain identical kernel segments, DTB/ADT properties, `-noprogress`, and `sweetfb_noconsole=1`; the sole non-`seg[10]` difference in `golden_boot` is `g7gpu=0` vs `g7gpu=8`.
- `AppleCLCD::present` (`0x0bac86c`, VA `0xfffffe0007a8045c`) parses `sweetfb_noconsole` (`0x27cd91`) and stores `1` to `[0xfffffe0007c154c8]` **only when the UI presents its first frame**.
- Before `AppleCLCD::present` runs, `[0xfffffe0007c154c8]` is `0`, so `_console_ring_try_empty` (`0x059be7c`) and `__cnputs` (`0x059c1ec`) fall through `cbz w8` and render kernel logs onto the framebuffer whenever `g7gpu=8` delays or fails GPU/UI startup.
- All xrefs to `[0xfffffe0007c154c8]` in `__TEXT_EXEC`: `0x059be78` (`0xfffffe000746fa68`, ldr), `0x059c1e8` (`0xfffffe000746fdd8`, ldr), `0x0bac898` (`0xfffffe0007a80488`, str)
- Patching `0x059be7c` and `0x059c1ec` from `cbz w8` to `nop` makes non-panic framebuffer console suppression unconditional from early boot while preserving `bl _panic_active` (real panics still display on screen).

## 3. `stage8` / `route 18 phase 1` Binary Trace

- Format string `"GPU SMMU context failed at step..."`: `img=0x27d99b`, `va=0xfffffe0007151593`
- `_g7_adreno_bringup` xrefs to format string: 
- Printf struct mapping in `_g7_adreno_bringup` (`report` at `sp + 0xe0`):
  - `step %u` <- `[sp, #0xe0]` (`report + 0x00`)
  - `program %u` <- `[sp, #0x110]` (`report + 0x30`)
  - `route %u` <- `[sp, #0x114]` (`report + 0x34`)
  - `phase %u` <- `[sp, #0xf8]` (`report + 0x18`)
- `NativeAdrenoGpuContext::bringUp` (`0x0bc4110..0x0bc411c`): copies `smmu_ + 0x284` (`[x19, #0x484]`) -> `report + 0x34` and `smmu_ + 0x1b0` (`[x19, #0x3b0]`) -> `report + 0x18`.
- Single caller of `_ArmSmmu4KAttachStreams` (`0xfffffe0007a93cb8`): `0x0bc9168` (`0xfffffe0007a9cd58`) (`NativeAdrenoSmmuContext::attach+0x6c`, stores `w0` directly to `[x20, #0x284]` and adds `8` to `0xe00002c2` -> `0xe00002ca`).
- Immediate `18` (`0x12`) scan hits in SMMU / Adreno attach functions: **0** (`[]`).
- All return values encoded across `ArmSmmu4K` attach helpers (strictly `ArmSmmu4KStatus` `0..11`):
  - `_ArmSmmu4KAttachStreams`: `w0` imm=[], `w26` imm=[1, 7, 8, 10]
  - `_global`: `w0` imm=[1, 6, 7, 8], `w26` imm=[]
  - `_ArmSmmu4KObserveOwnedContext`: `w0` imm=[0, 8, 11], `w26` imm=[]
  - `_prepare`: `w0` imm=[1, 2, 6, 8], `w26` imm=[]
  - `_read_image`: `w0` imm=[1], `w26` imm=[]
  - `_ArmSmmu4KValidateContextReadback`: `w0` imm=[0, 1, 7], `w26` imm=[]
  - `_ArmSmmu4KEncodeContext`: `w0` imm=[0], `w26` imm=[]
  - `_scan`: `w0` imm=[0, 1, 3, 7, 8, 10], `w26` imm=[0]
  - `_quarantine`: `w0` imm=[0, 1], `w26` imm=[]
  - `_observe`: `w0` imm=[7], `w26` imm=[]
  - `_ArmSmmu4KObserveStreams`: `w0` imm=[1, 7], `w26` imm=[]
  - `_g7_adreno_bringup`: `w0` imm=[0, 102, 256, 2056, 2096, 2097, 3648], `w26` imm=[]

### Phase 1 Validation Evaluation (`ID0=0x40016605`, `IDR1=0x20000805`, `sCR0=0x200626`, `S2CR=0x200ff`)
- `_global` (`0x0bbf95c`):
  - `0x0bbfa44`: `ID0.SMS == 0` -> returns `6` (`Unsupported`). **Patched -> `nop`**.
  - `0x0bbfa4c..a60`: `NUMSMRG = 5 != 0`, `0xc14 <= 0x10000` -> passes.
  - `0x0bbfa6c..a88`: `(0x200626 & 0x407) == 0x406` and `EXIDENABLE == ID0.EXIDS == 0` -> passes.
  - `0x0bbfa98`: `SMMU_sGFSR != 0` -> returns `11` (`Fault`). **Patched -> `movz w0, #0x0`**.
- `_ArmSmmu4KObserveOwnedContext` (`0x0bbf0b4`):
  - `0x0bbf148`: `_ArmSmmu4KValidateContextReadback` verifies `CB0` config (`program 0`).
  - `0x0bbf1a4`: `CB0_FSR & 0xc00001fe != 0` -> returns `11` (`Fault`), which was *not* checked by `NativeAdrenoSmmuContext::program()` and *not* patched in `v2`. **Patched (`0x0bbf1a4`) -> unconditional branch to success (`0xfffffe0007a92da0`)** so `phase 1` & `phase 3` proceed cleanly when pre-existing `CB0_FSR` bits are latched.
- `_scan` (`0x0bbfaa8`):
  - `0x0bbfcdc..cf0`: `0x0bbfce4` (`eor w13, w13, #0xffffff00`) already masks out `cbndx` `[7:0]` (`0x200ff & 0xffffff00 == 0x20000`); `SMR = 0` (`VALID = 0`) skips cleanly at `0x0bbfcf4`.

## 4. Applied Patches (`boot-g7em-gpu8-v3.img`)

| File Offset | Virtual Address | Original Word | Patched Word | Assembly Change | Purpose |
|---:|---|---:|---:|---|---|
| `0x059be7c` | `0xfffffe000746fa6c` | `0x34000068` | `0xd503201f` | `cbz w8, 0xfffffe000746fa78 -> nop` | _console_ring_try_empty: enforce sweetfb_noconsole from early boot (keeps _panic_active screen output) |
| `0x059c1ec` | `0xfffffe000746fddc` | `0x34000068` | `0xd503201f` | `cbz w8, 0xfffffe000746fde8 -> nop` | __cnputs: enforce sweetfb_noconsole from early boot (keeps _panic_active screen output) |
| `0x0bbf1a4` | `0xfffffe0007a92d94` | `0x54000060` | `0x14000003` | `b.eq 0xfffffe0007a92da0 -> b 0xfffffe0007a92da0` | _ArmSmmu4KObserveOwnedContext: ignore pre-existing latched CB0_FSR fault bits (11) in phase 1 & phase 3 |
| `0x0bbfa44` | `0xfffffe0007a93634` | `0x36d80108` | `0xd503201f` | `tbz w8, #27, 0xfffffe0007a93654 -> nop` | _global: bypass ID0.SMS==0 check on ID0=0x40016605 in phase 1 & phase 3 |
| `0x0bbfa98` | `0xfffffe0007a93688` | `0x1a8903e0` | `0x52800000` | `csel w0, wzr, w9, eq -> movz w0, #0x0` | _global: do not fail phase 1 & phase 3 on latched SMMU_sGFSR fault status |
| `0x0000240` | `(boot_hdr+0x240)` | `17eff122fa155312e4fb96cc789fee144f68f94c` | `2e51db36e8c646617ee68cac7aa60cd9eab57d6c` | 20-byte SHA-1 ID | Recomputed Android boot.img v1 checksum |
