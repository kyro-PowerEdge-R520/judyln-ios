# UI-Ready Boot Image Verification Notes (`boot-g7em-ui-ready.img`)

## Image Paths & Checksums

- **Source (read-only baseline)**: `C:\Users\kyro\Downloads\judyln-ios\golden_boot\boot_a-cpu-ui-touch.img`
- **Output (verified UI-ready copy)**: `C:\Users\kyro\Downloads\judyln-ios\work\next-gen\boot-g7em-ui-ready.img`
- **File Size**: `18112512` bytes
- **Byte-for-Byte Match vs. Golden Baseline**: `True` (`out == golden`)
- **Source SHA-256**: `766a88577c208af62583d199fa5dbd8f46811342aa109db5c334a5d38607b3e7`
- **Output SHA-256**: `766a88577c208af62583d199fa5dbd8f46811342aa109db5c334a5d38607b3e7`
- **Android Boot Header v1 SHA-1 ID (`0x240..0x254`)**: `08b9b1eeecef061d53f2551691bed4a195ad78b2` (matches recomputed payload digest `08b9b1eeecef061d53f2551691bed4a195ad78b2`)

## Verified Boot Configuration (`SWEETXNU.cmdline` @ `0x130048`)

```text
debug=0xc serial=3 keepsyms=1 -noprogress rd=ufsroot0 unentitled_ios_sim_launch=1 ignition_level=1 wdt_test=no_user_checkin ufsrw=1 rootrw=1 launchd_unsecure_cache=1 wdt=-1 sweetfb_hz=60 sweettouch=1 g7touch_bar=0 g7touch_init=2 sweetusb=0 cpus=8 sweetsmp=1 g7perf=100 sweetbattery=2 g7gpu=0 sweetfb_noconsole=1
```

- Required tokens present: `sweetusb=0`, `g7gpu=0`, `sweetfb_noconsole=1`, `sweetfb_hz=60`, `sweettouch=1`, `g7touch_bar=0`, `g7touch_init=2`
- Excluded tokens absent: `sweetusb=1`, `sweetusb=2`, `g7gpu=8`
