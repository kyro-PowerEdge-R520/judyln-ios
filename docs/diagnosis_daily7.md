# `shim-boot-g7daily7-g710em.img` `30h` Patch Confirmation

- Target file: `c:\Users\kyro\Downloads\judyln-ios\out-judyln\shim-boot-g7daily7-g710em.img` (`18,120,704` bytes)
- Verified `30h` `boot.img` v1 header + 4 `30h` base DTBs (`0x1000..0x132000`, matching `shim-boot-g7diag6-g710em.img`) and `SWEETXNU` daily7 ramdisk payload (`0x132000..0x1147bb0`, matching original `G7-iOS16-boot/G7-iOS16-boot/shim-boot-g7daily7.img` ramdisk).
- Retained original quiet/UI `boot_args` at `0x132048` (no `debug=0x10c` or `-v` added):
  ```text
  debug=0xc serial=3 keepsyms=1 -enable_kprintf_spam -noprogress rd=ufsroot0 unentitled_ios_sim_launch=1 ignition_level=1 wdt_test=no_user_checkin ufsrw=1 rootrw=1 launchd_unsecure_cache=1 wdt=-1 sweetfb_noconsole=1 sweetfb_hz=60 sweettouch=0 sweetsample=- g7touch_bar=0 g7touch_init=2 sweetusb=0 cpus=8 sweetsmp=1 g7perf=100 sweetbattery=2 g7gpu=8
  ```
- Patches applied and verified by re-read:
  1. `SWEETXNU.mem_size` (`0x132040`): `0x7e1c0000` → **`0x7e0c0000`**
  2. ADT `/chosen/dram-size` (`0x1144c28`): `0x7e1c0000` → **`0x7e0c0000`**
  3. ADT `/pram` `reg` base (`0x1147054`): `<0x17e1c0000 0x100000>` → **`<0x17e0c0000 0x100000>`**
  4. ADT node name (`0x1147000`): `b'pram\x00'` → **`b'nram\x00'`**
  5. `boot.img` v1 header SHA-1 `id` (`0x240`): updated from `553c081521b753e94c5cc4157170bdd562298f21000000000000000000000000` → **`bdfdf9f2e2f1fa1f948583c77dd14fffd99ded2c000000000000000000000000`**
