# USB & Boot-Args Analysis Report (`golden_boot\boot_a-cpu-ui-touch.img`)

## 1. Source & Output Images

- **Baseline (`golden_boot\boot_a-cpu-ui-touch.img`)**: `18112512` bytes, SHA-256: `766a88577c208af62583d199fa5dbd8f46811342aa109db5c334a5d38607b3e7` (verified read-only & untouched)
- **`SWEETXNU` Header**: offset `0x130000`, version `1`, `nsegs=10`
- **Current `CMDLINE` (`0x130048`)**: `debug=0xc serial=3 keepsyms=1 -noprogress rd=ufsroot0 unentitled_ios_sim_launch=1 ignition_level=1 wdt_test=no_user_checkin ufsrw=1 rootrw=1 launchd_unsecure_cache=1 wdt=-1 sweetfb_hz=60 sweettouch=1 g7touch_bar=0 g7touch_init=2 sweetusb=0 cpus=8 sweetsmp=1 g7perf=100 sweetbattery=2 g7gpu=0 sweetfb_noconsole=1`
- **Output 1 (`work\next-gen\boot-g7em-usb1.img`)**: `18112512` bytes, `sweetusb=1` (replaced `sweetusb=0` in-place at `0x13012d`, same byte length), SHA-256: `70d071130869532a4ae9108b5415c24a1101fad492e4ec44252428617328edd7`, boot header SHA-1 ID (`0x240`): `499d6e516ae9fcce7a2f04b7061ade550f0a5a87`
- **Output 2 (`work\next-gen\boot-g7em-usb2.img`)**: `18112512` bytes, `sweetusb=2` (at `0x13012d`; reason: `_sweet_usb_probe` checks cmp value(s) [0, 1, 2, 7]), SHA-256: `a7ad6a07b66df9bd85dc6627c4f6b7aafaef2c775409d99c894d252c33e314c5`, boot header SHA-1 ID (`0x240`): `6d103a7df733128dc5694619e56af7b199a6a73a`

## 2. Mach-O `LC_SEGMENT_64` & `SWEETXNU` Segment Layout

| Mach-O Segment | VM Start | VM Size | File Offset | File Size | `nsects` |
|---|---|---:|---:|---:|---:|
| `__TEXT` | `0xfffffe0007004000` | `0x170000` | `0x0` | `0x170000` | 6 |
| `__DATA_CONST` | `0xfffffe0007174000` | `0x184000` | `0x170000` | `0x184000` | 7 |
| `__TEXT_EXEC` | `0xfffffe00072f8000` | `0x874000` | `0x2f4000` | `0x874000` | 3 |
| `__KLD` | `0xfffffe0007b6c000` | `0x4000` | `0xb68000` | `0x4000` | 1 |
| `__LASTDATA_CONST` | `0xfffffe0007b70000` | `0x4000` | `0xb6c000` | `0x4000` | 1 |
| `__LAST` | `0xfffffe0007b74000` | `0x0` | `0x0` | `0x0` | 1 |
| `__KLDDATA` | `0xfffffe0007b74000` | `0x4000` | `0xb70000` | `0x4000` | 5 |
| `__DATA` | `0xfffffe0007b78000` | `0x538000` | `0xb74000` | `0x48000` | 11 |
| `__BOOTDATA` | `0xfffffe00080b0000` | `0x4c000` | `0xbbc000` | `0x4c000` | 3 |
| `__PRELINK_TEXT` | `0xfffffe0004004000` | `0x0` | `0xc08000` | `0x0` | 1 |
| `__PRELINK_INFO` | `0xfffffe00080fc000` | `0x0` | `0xc08000` | `0x0` | 1 |
| `__PLK_TEXT_EXEC` | `0xfffffe00080fc000` | `0x0` | `0xc08000` | `0x0` | 1 |
| `__PRELINK_DATA` | `0xfffffe00080fc000` | `0x0` | `0xc08000` | `0x0` | 1 |
| `__PLK_DATA_CONST` | `0xfffffe00080fc000` | `0x0` | `0xc08000` | `0x0` | 1 |
| `__PLK_LLVM_COV` | `0xfffffe00080fc000` | `0x0` | `0xc08000` | `0x0` | 1 |
| `__PLK_LINKEDIT` | `0xfffffe00080fc000` | `0x0` | `0xc08000` | `0x0` | 1 |
| `__LINKINFO` | `0xfffffe00080fc000` | `0x4c000` | `0xc08000` | `0x4c000` | 1 |
| `__CTF` | `0xfffffe0008148000` | `0x0` | `0xc54000` | `0x94000` | 1 |
| `__LINKEDIT` | `0xfffffe0008148000` | `0x3c0000` | `0xce8000` | `0x3be5c8` | 0 |

| `SWEETXNU` Index | VM Start | VM Size | Image Offset | File Size |
|---:|---|---:|---:|---:|
| `seg[0]` | `0xfffffe0007004000` | `0x170000` | `0x01303e8` | `0x170000` |
| `seg[1]` | `0xfffffe0007174000` | `0x184000` | `0x02a03f0` | `0x184000` |
| `seg[2]` | `0xfffffe00072f8000` | `0x874000` | `0x04243f0` | `0x874000` |
| `seg[3]` | `0xfffffe0007b6c000` | `0x4000` | `0x0c983f0` | `0x4000` |
| `seg[4]` | `0xfffffe0007b70000` | `0x4000` | `0x0c9c3f0` | `0x4000` |
| `seg[5]` | `0xfffffe0007b74000` | `0x4000` | `0x0ca03f0` | `0x4000` |
| `seg[6]` | `0xfffffe0007b78000` | `0x538000` | `0x0ca43f0` | `0x48000` |
| `seg[7]` | `0xfffffe00080b0000` | `0x4c000` | `0x0cec3f0` | `0x4c000` |
| `seg[8]` | `0xfffffe00080fc000` | `0x4c000` | `0x0d383f0` | `0x4c000` |
| `seg[9]` | `0xfffffe0008148000` | `0x3c0000` | `0x0d843f0` | `0x3be5c8` |

## 2b. Mode & Value Expectations (`sweetusb`, `sweet_usb`, `sweetusblog`, `sweetkeys`)

- **`sweetusb`** (parsed in `_sweet_usb_probe` at `0x062e6c8` via `PE_parse_boot_argn`; defaults to `1` at `0x062e6c0` if omitted from boot-args):
  - `0` (current `golden_boot` setting): `0x062e6e0` (`cbz w8`) disables USB probing and skips DWC3 register/gadget bringup.
  - `1`: DWC3 clock/register probe & **report only** (`0x062e9e0`: `report only (sweetusb=1)`); reads/logs DWC3 registers (`GSNPSID`, `GCTL`, `GSTS`, `GUSB2PHYCFG`, `DCFG`, `DCTL`, `DEVTEN`, `DSTS`, `DALEPENA`, `GEVNT*`, `GHWPARAMS0`), then stops at `0x062eaf8` (`cmp w8, #0x2; b.lt`).
  - `2` (or `>= 2`): Passes `0x062eaf8` (`cmp w8, #0x2; b.lt`), allocates USB buffers/locks (`sweet_usb` lock group at `0x062ec58`), and starts full DWC3 device/gadget mode.
- **`sweet_usb`**: Lock group name string at `0x062ec58` (not a separate boot-arg).
- **`sweetusblog`** (`0x062f214`, defaults to `1` at `0x062f20c`): Non-zero starts the `sweetusblog` kernel worker thread (`0x062f24c`) when active.
- **`DWC3` / `usb-drd,t8027`**: `DWC3` strings at `0x01c40c7..0x01c420c` are used in `_sweet_usb_probe` (`0x062ea40..0x062ebdc`) for Qualcomm SDM845 DWC3 diagnostics; `usb-drd,t8027` has `0` occurrences in this image.
- **`sweetkeys`** (parsed in `_sweet_keys_init` at `0x062a380` via `PE_parse_boot_argn`):
  - `0`: `0x062a398` (`cbz w8`) logs `SWEET KEYS: disabled (sweetkeys=0)` and disables key polling.
  - `!= 0` (e.g. `1`, or omitted default non-zero): Enables GPIO/PMIC hardware key polling and parses `sweetkeys_ai`, `sweetkeys_ai_page`, and `sweetkeys_ai_usage` (`0x062aa1c..0x062aa64`).

## 3. Keyword Strings & `__TEXT_EXEC` Cross-References

### `sweetusb`
- String/symbol occurrences (4):
  - img `0x013012d` (VA n/a): `_init=2 sweetusb=0 cpus=8 sweetsmp=1 g7perf=100 sweetbattery=2 g7gpu=0 s`
  - img `0x01c3fae` (VA `0xfffffe0007097bc6`): `sweetusb`
  - img `0x01c413b` (VA `0xfffffe0007097d53`): `report only (sweetusb=1)`
  - img `0x01c450a` (VA `0xfffffe0007098122`): `sweetusblog`
- `__TEXT_EXEC` `ADRP+ADD` xrefs (3):
  - img `0x062e6c8` (VA `0xfffffe00075022d8`, `<_sweet_usb_probe+0x38>`) -> `0xfffffe0007097bc6`
  - img `0x062e9e0` (VA `0xfffffe00075025f0`, `<_sweet_usb_probe+0x350>`) -> `0xfffffe0007097d46`
  - img `0x062f214` (VA `0xfffffe0007502e24`, `<_sweet_usb_probe+0xb84>`) -> `0xfffffe0007098122`

### `sweet_usb`
- String/symbol occurrences (2):
  - img `0x01c4516` (VA `0xfffffe000709812e`): `sweet_usb`
  - img `0x0fd6bfe` (VA `0xfffffe000839a80e`): `ootdev`
- `__TEXT_EXEC` `ADRP+ADD` xrefs (1):
  - img `0x062ec58` (VA `0xfffffe0007502868`, `<_sweet_usb_probe+0x5c8>`) -> `0xfffffe000709812e`

### `sweetusblog`
- String/symbol occurrences (1):
  - img `0x01c450a` (VA `0xfffffe0007098122`): `sweetusblog`
- `__TEXT_EXEC` `ADRP+ADD` xrefs (1):
  - img `0x062f214` (VA `0xfffffe0007502e24`, `<_sweet_usb_probe+0xb84>`) -> `0xfffffe0007098122`

### `DWC3`
- String/symbol occurrences (5):
  - img `0x01c40c7` (VA `0xfffffe0007097cdf`): `SWEET USB: controller unpowered or unclocked; DWC3 not read
`
  - img `0x01c4152` (VA `0xfffffe0007097d6a`): `SWEET USB: DWC3 map failed
`
  - img `0x01c416e` (VA `0xfffffe0007097d86`): `SWEET USB: DWC3 GSNPSID 0x%08x GCTL 0x%08x GSTS 0x%08x GUSB2PHYCFG 0x%08x
`
  - img `0x01c41b9` (VA `0xfffffe0007097dd1`): `SWEET USB: DWC3 DCFG 0x%08x DCTL 0x%08x DEVTEN 0x%08x DSTS 0x%08x DALEPENA 0x%08x
`
  - img `0x01c420c` (VA `0xfffffe0007097e24`): `SWEET USB: DWC3 GEVNTADR 0x%08x%08x GEVNTSIZ 0x%08x GEVNTCOUNT 0x%08x GHWPARAMS0 0x%08x
`
- `__TEXT_EXEC` `ADRP+ADD` xrefs (5):
  - img `0x062ea40` (VA `0xfffffe0007502650`, `<_sweet_usb_probe+0x3b0>`) -> `0xfffffe0007097d7b`
  - img `0x062ea94` (VA `0xfffffe00075026a4`, `<_sweet_usb_probe+0x404>`) -> `0xfffffe0007097dc6`
  - img `0x062eae8` (VA `0xfffffe00075026f8`, `<_sweet_usb_probe+0x458>`) -> `0xfffffe0007097e19`
  - img `0x062ebac` (VA `0xfffffe00075027bc`, `<_sweet_usb_probe+0x51c>`) -> `0xfffffe0007097cb1`
  - img `0x062ebdc` (VA `0xfffffe00075027ec`, `<_sweet_usb_probe+0x54c>`) -> `0xfffffe0007097d5f`

### `usb-drd,t8027`
- String/symbol occurrences (0):
- `__TEXT_EXEC` `ADRP+ADD` xrefs (0):

### `sweetkeys`
- String/symbol occurrences (5):
  - img `0x01c30f3` (VA `0xfffffe0007096d0b`): `sweetkeys`
  - img `0x01c3113` (VA `0xfffffe0007096d2b`): `SWEET KEYS: disabled (sweetkeys=0)
`
  - img `0x01c324c` (VA `0xfffffe0007096e64`): `sweetkeys_ai`
  - img `0x01c3259` (VA `0xfffffe0007096e71`): `sweetkeys_ai_page`
  - img `0x01c326b` (VA `0xfffffe0007096e83`): `sweetkeys_ai_usage`
- `__TEXT_EXEC` `ADRP+ADD` xrefs (5):
  - img `0x062a380` (VA `0xfffffe00074fdf90`, `<_sweet_keys_init+0x3c>`) -> `0xfffffe0007096d0b`
  - img `0x062a494` (VA `0xfffffe00074fe0a4`, `<_sweet_keys_init+0x150>`) -> `0xfffffe0007096d15`
  - img `0x062aa1c` (VA `0xfffffe00074fe62c`, `<_sweet_keys_init+0x6d8>`) -> `0xfffffe0007096e64`
  - img `0x062aa38` (VA `0xfffffe00074fe648`, `<_sweet_keys_init+0x6f4>`) -> `0xfffffe0007096e71`
  - img `0x062aa50` (VA `0xfffffe00074fe660`, `<_sweet_keys_init+0x70c>`) -> `0xfffffe0007096e83`

## 4. Surrounding Disassembly for Each Cross-Reference

### Xref `sweetusb` at `0x062e6c8` (`0xfffffe00075022d8` `<_sweet_usb_probe+0x38>`)
```asm
0x062e6b8 (0xfffffe00075022c8): f945b108  ldr x8, [x8, #0xb60]
0x062e6bc (0xfffffe00075022cc): f81a83a8  .word 0xf81a83a8
0x062e6c0 (0xfffffe00075022d0): 52800028  movz w8, #0x1
0x062e6c4 (0xfffffe00075022d4): b90037e8  str w8, [sp, #0x34]
0x062e6c8 (0xfffffe00075022d8): b0ffdca0  adrp x0, 0xfffffe0007097000  <-- xref
0x062e6cc (0xfffffe00075022dc): 912f1800  add x0, x0, #0xbc6
0x062e6d0 (0xfffffe00075022e0): 9100d3e1  add x1, sp, #0x34
0x062e6d4 (0xfffffe00075022e4): 52800082  movz w2, #0x4
0x062e6d8 (0xfffffe00075022e8): 94169e63  bl 0xfffffe0007aa9c74 <_PE_parse_boot_argn>
0x062e6dc (0xfffffe00075022ec): b94037e8  ldr w8, [sp, #0x34]
0x062e6e0 (0xfffffe00075022f0): 340028a8  cbz w8, 0xfffffe0007502804
0x062e6e4 (0xfffffe00075022f4): f90027ff  str x31, [sp, #0x48]
0x062e6e8 (0xfffffe00075022f8): 10005be0  adr x0, 0xfffffe0007502e74
0x062e6ec (0xfffffe00075022fc): d503201f  nop
0x062e6f0 (0xfffffe0007502300): 910123e2  add x2, sp, #0x48
0x062e6f4 (0xfffffe0007502304): d2800001  movz x1, #0x0
0x062e6f8 (0xfffffe0007502308): 97fa32a0  bl 0xfffffe000738ed88 <_kernel_thread_start>
0x062e6fc (0xfffffe000750230c): 35000060  cbnz w0, 0xfffffe0007502318
0x062e700 (0xfffffe0007502310): f94027e0  ldr x0, [sp, #0x48]
0x062e704 (0xfffffe0007502314): 97fa2b73  bl 0xfffffe000738d0e0 <_thread_deallocate>
0x062e708 (0xfffffe0007502318): 52a00200  movz w0, #0x10, lsl #16
0x062e70c (0xfffffe000750231c): 52a00121  movz w1, #0x9, lsl #16
0x062e710 (0xfffffe0007502320): 97fe8bf8  bl 0xfffffe00074a5300 <_ml_io_map>
0x062e714 (0xfffffe0007502324): b4000480  cbz x0, 0xfffffe00075023b4
0x062e718 (0xfffffe0007502328): aa0003f3  mov x19, x0
0x062e71c (0xfffffe000750232c): 529e0088  movz w8, #0xf004
0x062e720 (0xfffffe0007502330): b8686818  .word 0xb8686818
0x062e724 (0xfffffe0007502334): d50331bf  .word 0xd50331bf
0x062e728 (0xfffffe0007502338): b0ffdcb6  adrp x22, 0xfffffe0007097000
0x062e72c (0xfffffe000750233c): 913086d6  add x22, x22, #0xc21
0x062e730 (0xfffffe0007502340): 90ffdb37  adrp x23, 0xfffffe0007066000
0x062e734 (0xfffffe0007502344): 910302f7  add x23, x23, #0xc0
```

### Xref `sweetusb` at `0x062e9e0` (`0xfffffe00075025f0` `<_sweet_usb_probe+0x350>`)
```asm
0x062e9d0 (0xfffffe00075025e0): 97fe8b48  bl 0xfffffe00074a5300 <_ml_io_map>
0x062e9d4 (0xfffffe00075025e4): d0005c28  adrp x8, 0xfffffe0008088000
0x062e9d8 (0xfffffe00075025e8): f9050100  str x0, [x8, #0xa00]
0x062e9dc (0xfffffe00075025ec): b94037e8  ldr w8, [sp, #0x34]
0x062e9e0 (0xfffffe00075025f0): b0ffdca9  adrp x9, 0xfffffe0007097000  <-- xref
0x062e9e4 (0xfffffe00075025f4): 91351929  add x9, x9, #0xd46
0x062e9e8 (0xfffffe00075025f8): b0ffdcaa  adrp x10, 0xfffffe0007097000
0x062e9ec (0xfffffe00075025fc): 9134954a  add x10, x10, #0xd25
0x062e9f0 (0xfffffe0007502600): 7100051f  cmp w8, #0x1
0x062e9f4 (0xfffffe0007502604): 9a89c148  .word 0x9a89c148
0x062e9f8 (0xfffffe0007502608): f00034f4  adrp x20, 0xfffffe0007ba1000
0x062e9fc (0xfffffe000750260c): f902a288  str x8, [x20, #0x540]
0x062ea00 (0xfffffe0007502610): b4000ee0  cbz x0, 0xfffffe00075027ec
0x062ea04 (0xfffffe0007502614): aa0003f3  mov x19, x0
0x062ea08 (0xfffffe0007502618): 52982408  movz w8, #0xc120
0x062ea0c (0xfffffe000750261c): b8686808  .word 0xb8686808
0x062ea10 (0xfffffe0007502620): d50331bf  .word 0xd50331bf
0x062ea14 (0xfffffe0007502624): 52982209  movz w9, #0xc110
0x062ea18 (0xfffffe0007502628): b8696809  .word 0xb8696809
0x062ea1c (0xfffffe000750262c): d50331bf  .word 0xd50331bf
0x062ea20 (0xfffffe0007502630): 5298230a  movz w10, #0xc118
0x062ea24 (0xfffffe0007502634): b86a680a  .word 0xb86a680a
0x062ea28 (0xfffffe0007502638): d50331bf  .word 0xd50331bf
0x062ea2c (0xfffffe000750263c): 5298400b  movz w11, #0xc200
0x062ea30 (0xfffffe0007502640): b86b680b  .word 0xb86b680b
0x062ea34 (0xfffffe0007502644): d50331bf  .word 0xd50331bf
0x062ea38 (0xfffffe0007502648): a9012fea  stp x10, x11, [sp, #0x10]
0x062ea3c (0xfffffe000750264c): a90027e8  stp x8, x9, [sp, #0x0]
0x062ea40 (0xfffffe0007502650): b0ffdca0  adrp x0, 0xfffffe0007097000
0x062ea44 (0xfffffe0007502654): 9135ec00  add x0, x0, #0xd7b
0x062ea48 (0xfffffe0007502658): 97f96d0b  bl 0xfffffe000735da84 <_printf>
0x062ea4c (0xfffffe000750265c): 5298e008  movz w8, #0xc700
```

### Xref `sweetusb` at `0x062f214` (`0xfffffe0007502e24` `<_sweet_usb_probe+0xb84>`)
```asm
0x062f204 (0xfffffe0007502e14): f9401fe0  ldr x0, [sp, #0x38]
0x062f208 (0xfffffe0007502e18): 97fa28b2  bl 0xfffffe000738d0e0 <_thread_deallocate>
0x062f20c (0xfffffe0007502e1c): 52800028  movz w8, #0x1
0x062f210 (0xfffffe0007502e20): b9004be8  str w8, [sp, #0x48]
0x062f214 (0xfffffe0007502e24): d0ffdca0  adrp x0, 0xfffffe0007098000  <-- xref
0x062f218 (0xfffffe0007502e28): 91048800  add x0, x0, #0x122
0x062f21c (0xfffffe0007502e2c): 910123e1  add x1, sp, #0x48
0x062f220 (0xfffffe0007502e30): 52800082  movz w2, #0x4
0x062f224 (0xfffffe0007502e34): 94169b90  bl 0xfffffe0007aa9c74 <_PE_parse_boot_argn>
0x062f228 (0xfffffe0007502e38): b9404be8  ldr w8, [sp, #0x48]
0x062f22c (0xfffffe0007502e3c): 34ffc968  cbz w8, 0xfffffe0007502768
0x062f230 (0xfffffe0007502e40): d0005c28  adrp x8, 0xfffffe0008088000
0x062f234 (0xfffffe0007502e44): f9452508  ldr x8, [x8, #0xa48]
0x062f238 (0xfffffe0007502e48): b4ffc908  cbz x8, 0xfffffe0007502768
0x062f23c (0xfffffe0007502e4c): 10007620  adr x0, 0xfffffe0007503d10
0x062f240 (0xfffffe0007502e50): d503201f  nop
0x062f244 (0xfffffe0007502e54): 9100e3e2  add x2, sp, #0x38
0x062f248 (0xfffffe0007502e58): d2800001  movz x1, #0x0
0x062f24c (0xfffffe0007502e5c): 97fa2fcb  bl 0xfffffe000738ed88 <_kernel_thread_start>
0x062f250 (0xfffffe0007502e60): 35ffc840  cbnz w0, 0xfffffe0007502768
0x062f254 (0xfffffe0007502e64): f9401fe0  ldr x0, [sp, #0x38]
0x062f258 (0xfffffe0007502e68): 97fa289e  bl 0xfffffe000738d0e0 <_thread_deallocate>
0x062f25c (0xfffffe0007502e6c): 17fffe3f  b 0xfffffe0007502768 <_sweet_usb_probe+0x4c8>
0x062f260 (0xfffffe0007502e70): 9412a5d3  bl 0xfffffe00079ac5bc <___stack_chk_fail>
0x062f264 (0xfffffe0007502e74): d10243ff  sub sp, sp, #0x90
0x062f268 (0xfffffe0007502e78): a9036ffc  stp x28, x27, [sp, #0x30]
0x062f26c (0xfffffe0007502e7c): a90467fa  stp x26, x25, [sp, #0x40]
0x062f270 (0xfffffe0007502e80): a9055ff8  stp x24, x23, [sp, #0x50]
0x062f274 (0xfffffe0007502e84): a90657f6  stp x22, x21, [sp, #0x60]
0x062f278 (0xfffffe0007502e88): a9074ff4  stp x20, x19, [sp, #0x70]
0x062f27c (0xfffffe0007502e8c): a9087bfd  stp x29, x30, [sp, #0x80]
0x062f280 (0xfffffe0007502e90): 910203fd  add x29, sp, #0x80
```

### Xref `sweet_usb` at `0x062ec58` (`0xfffffe0007502868` `<_sweet_usb_probe+0x5c8>`)
```asm
0x062ec48 (0xfffffe0007502858): d3727c08  .word 0xd3727c08
0x062ec4c (0xfffffe000750285c): d0005c37  adrp x23, 0xfffffe0008088000
0x062ec50 (0xfffffe0007502860): 9128a2f7  add x23, x23, #0xa28
0x062ec54 (0xfffffe0007502864): f90002e8  str x8, [x23, #0x0]
0x062ec58 (0xfffffe0007502868): d0ffdca0  adrp x0, 0xfffffe0007098000  <-- xref
0x062ec5c (0xfffffe000750286c): 9104b800  add x0, x0, #0x12e
0x062ec60 (0xfffffe0007502870): d2800001  movz x1, #0x0
0x062ec64 (0xfffffe0007502874): 97f92acc  bl 0xfffffe000734d3a4 <_lck_grp_alloc_init>
0x062ec68 (0xfffffe0007502878): d0005c28  adrp x8, 0xfffffe0008088000
0x062ec6c (0xfffffe000750287c): f905bd00  str x0, [x8, #0xb78]
0x062ec70 (0xfffffe0007502880): d2800001  movz x1, #0x0
0x062ec74 (0xfffffe0007502884): 97f92d25  bl 0xfffffe000734dd18 <_lck_mtx_alloc_init>
0x062ec78 (0xfffffe0007502888): f90016e0  str x0, [x23, #0x28]
0x062ec7c (0xfffffe000750288c): 910123e8  add x8, sp, #0x48
0x062ec80 (0xfffffe0007502890): 91002108  add x8, x8, #0x8
0x062ec84 (0xfffffe0007502894): 6f00e400  .word 0x6f00e400
0x062ec88 (0xfffffe0007502898): ad080100  stp x0, x0, [x8, #0x80]
0x062ec8c (0xfffffe000750289c): ad090100  stp x0, x0, [x8, #0x90]
0x062ec90 (0xfffffe00075028a0): 3d805100  .word 0x3d805100
0x062ec94 (0xfffffe00075028a4): ad0283e0  stp x0, x0, [sp, #0x28]
0x062ec98 (0xfffffe00075028a8): ad0383e0  stp x0, x0, [sp, #0x38]
0x062ec9c (0xfffffe00075028ac): ad0483e0  stp x0, x0, [sp, #0x48]
0x062eca0 (0xfffffe00075028b0): 3c8b03e0  .word 0x3c8b03e0
0x062eca4 (0xfffffe00075028b4): 3c878260  .word 0x3c878260
0x062eca8 (0xfffffe00075028b8): 3c888260  .word 0x3c888260
0x062ecac (0xfffffe00075028bc): 3c898260  .word 0x3c898260
0x062ecb0 (0xfffffe00075028c0): 3c8a8260  .word 0x3c8a8260
0x062ecb4 (0xfffffe00075028c4): 3c8b8260  .word 0x3c8b8260
0x062ecb8 (0xfffffe00075028c8): 3c8c8260  .word 0x3c8c8260
0x062ecbc (0xfffffe00075028cc): 3c8d8260  .word 0x3c8d8260
0x062ecc0 (0xfffffe00075028d0): 3c8e8260  .word 0x3c8e8260
0x062ecc4 (0xfffffe00075028d4): 3c8f8260  .word 0x3c8f8260
```

### Xref `sweetusblog` at `0x062f214` (`0xfffffe0007502e24` `<_sweet_usb_probe+0xb84>`)
```asm
0x062f204 (0xfffffe0007502e14): f9401fe0  ldr x0, [sp, #0x38]
0x062f208 (0xfffffe0007502e18): 97fa28b2  bl 0xfffffe000738d0e0 <_thread_deallocate>
0x062f20c (0xfffffe0007502e1c): 52800028  movz w8, #0x1
0x062f210 (0xfffffe0007502e20): b9004be8  str w8, [sp, #0x48]
0x062f214 (0xfffffe0007502e24): d0ffdca0  adrp x0, 0xfffffe0007098000  <-- xref
0x062f218 (0xfffffe0007502e28): 91048800  add x0, x0, #0x122
0x062f21c (0xfffffe0007502e2c): 910123e1  add x1, sp, #0x48
0x062f220 (0xfffffe0007502e30): 52800082  movz w2, #0x4
0x062f224 (0xfffffe0007502e34): 94169b90  bl 0xfffffe0007aa9c74 <_PE_parse_boot_argn>
0x062f228 (0xfffffe0007502e38): b9404be8  ldr w8, [sp, #0x48]
0x062f22c (0xfffffe0007502e3c): 34ffc968  cbz w8, 0xfffffe0007502768
0x062f230 (0xfffffe0007502e40): d0005c28  adrp x8, 0xfffffe0008088000
0x062f234 (0xfffffe0007502e44): f9452508  ldr x8, [x8, #0xa48]
0x062f238 (0xfffffe0007502e48): b4ffc908  cbz x8, 0xfffffe0007502768
0x062f23c (0xfffffe0007502e4c): 10007620  adr x0, 0xfffffe0007503d10
0x062f240 (0xfffffe0007502e50): d503201f  nop
0x062f244 (0xfffffe0007502e54): 9100e3e2  add x2, sp, #0x38
0x062f248 (0xfffffe0007502e58): d2800001  movz x1, #0x0
0x062f24c (0xfffffe0007502e5c): 97fa2fcb  bl 0xfffffe000738ed88 <_kernel_thread_start>
0x062f250 (0xfffffe0007502e60): 35ffc840  cbnz w0, 0xfffffe0007502768
0x062f254 (0xfffffe0007502e64): f9401fe0  ldr x0, [sp, #0x38]
0x062f258 (0xfffffe0007502e68): 97fa289e  bl 0xfffffe000738d0e0 <_thread_deallocate>
0x062f25c (0xfffffe0007502e6c): 17fffe3f  b 0xfffffe0007502768 <_sweet_usb_probe+0x4c8>
0x062f260 (0xfffffe0007502e70): 9412a5d3  bl 0xfffffe00079ac5bc <___stack_chk_fail>
0x062f264 (0xfffffe0007502e74): d10243ff  sub sp, sp, #0x90
0x062f268 (0xfffffe0007502e78): a9036ffc  stp x28, x27, [sp, #0x30]
0x062f26c (0xfffffe0007502e7c): a90467fa  stp x26, x25, [sp, #0x40]
0x062f270 (0xfffffe0007502e80): a9055ff8  stp x24, x23, [sp, #0x50]
0x062f274 (0xfffffe0007502e84): a90657f6  stp x22, x21, [sp, #0x60]
0x062f278 (0xfffffe0007502e88): a9074ff4  stp x20, x19, [sp, #0x70]
0x062f27c (0xfffffe0007502e8c): a9087bfd  stp x29, x30, [sp, #0x80]
0x062f280 (0xfffffe0007502e90): 910203fd  add x29, sp, #0x80
```

### Xref `DWC3` at `0x062ea40` (`0xfffffe0007502650` `<_sweet_usb_probe+0x3b0>`)
```asm
0x062ea30 (0xfffffe0007502640): b86b680b  .word 0xb86b680b
0x062ea34 (0xfffffe0007502644): d50331bf  .word 0xd50331bf
0x062ea38 (0xfffffe0007502648): a9012fea  stp x10, x11, [sp, #0x10]
0x062ea3c (0xfffffe000750264c): a90027e8  stp x8, x9, [sp, #0x0]
0x062ea40 (0xfffffe0007502650): b0ffdca0  adrp x0, 0xfffffe0007097000  <-- xref
0x062ea44 (0xfffffe0007502654): 9135ec00  add x0, x0, #0xd7b
0x062ea48 (0xfffffe0007502658): 97f96d0b  bl 0xfffffe000735da84 <_printf>
0x062ea4c (0xfffffe000750265c): 5298e008  movz w8, #0xc700
0x062ea50 (0xfffffe0007502660): b8686a68  .word 0xb8686a68
0x062ea54 (0xfffffe0007502664): d50331bf  .word 0xd50331bf
0x062ea58 (0xfffffe0007502668): 5298e089  movz w9, #0xc704
0x062ea5c (0xfffffe000750266c): b8696a69  .word 0xb8696a69
0x062ea60 (0xfffffe0007502670): d50331bf  .word 0xd50331bf
0x062ea64 (0xfffffe0007502674): 5298e10a  movz w10, #0xc708
0x062ea68 (0xfffffe0007502678): b86a6a6a  .word 0xb86a6a6a
0x062ea6c (0xfffffe000750267c): d50331bf  .word 0xd50331bf
0x062ea70 (0xfffffe0007502680): 5298e18b  movz w11, #0xc70c
0x062ea74 (0xfffffe0007502684): b86b6a6b  .word 0xb86b6a6b
0x062ea78 (0xfffffe0007502688): d50331bf  .word 0xd50331bf
0x062ea7c (0xfffffe000750268c): 5298e40c  movz w12, #0xc720
0x062ea80 (0xfffffe0007502690): b86c6a6c  .word 0xb86c6a6c
0x062ea84 (0xfffffe0007502694): d50331bf  .word 0xd50331bf
0x062ea88 (0xfffffe0007502698): a901b3eb  stp x11, x12, [sp, #0x18]
0x062ea8c (0xfffffe000750269c): a900abe9  stp x9, x10, [sp, #0x8]
0x062ea90 (0xfffffe00075026a0): f90003e8  str x8, [sp, #0x0]
0x062ea94 (0xfffffe00075026a4): b0ffdca0  adrp x0, 0xfffffe0007097000
0x062ea98 (0xfffffe00075026a8): 91371800  add x0, x0, #0xdc6
0x062ea9c (0xfffffe00075026ac): 97f96cf6  bl 0xfffffe000735da84 <_printf>
0x062eaa0 (0xfffffe00075026b0): 52988088  movz w8, #0xc404
0x062eaa4 (0xfffffe00075026b4): b8686a68  .word 0xb8686a68
0x062eaa8 (0xfffffe00075026b8): d50331bf  .word 0xd50331bf
0x062eaac (0xfffffe00075026bc): 52988009  movz w9, #0xc400
```

### Xref `DWC3` at `0x062ea94` (`0xfffffe00075026a4` `<_sweet_usb_probe+0x404>`)
```asm
0x062ea84 (0xfffffe0007502694): d50331bf  .word 0xd50331bf
0x062ea88 (0xfffffe0007502698): a901b3eb  stp x11, x12, [sp, #0x18]
0x062ea8c (0xfffffe000750269c): a900abe9  stp x9, x10, [sp, #0x8]
0x062ea90 (0xfffffe00075026a0): f90003e8  str x8, [sp, #0x0]
0x062ea94 (0xfffffe00075026a4): b0ffdca0  adrp x0, 0xfffffe0007097000  <-- xref
0x062ea98 (0xfffffe00075026a8): 91371800  add x0, x0, #0xdc6
0x062ea9c (0xfffffe00075026ac): 97f96cf6  bl 0xfffffe000735da84 <_printf>
0x062eaa0 (0xfffffe00075026b0): 52988088  movz w8, #0xc404
0x062eaa4 (0xfffffe00075026b4): b8686a68  .word 0xb8686a68
0x062eaa8 (0xfffffe00075026b8): d50331bf  .word 0xd50331bf
0x062eaac (0xfffffe00075026bc): 52988009  movz w9, #0xc400
0x062eab0 (0xfffffe00075026c0): b8696a69  .word 0xb8696a69
0x062eab4 (0xfffffe00075026c4): d50331bf  .word 0xd50331bf
0x062eab8 (0xfffffe00075026c8): 5298810a  movz w10, #0xc408
0x062eabc (0xfffffe00075026cc): b86a6a6a  .word 0xb86a6a6a
0x062eac0 (0xfffffe00075026d0): d50331bf  .word 0xd50331bf
0x062eac4 (0xfffffe00075026d4): 5298818b  movz w11, #0xc40c
0x062eac8 (0xfffffe00075026d8): b86b6a6b  .word 0xb86b6a6b
0x062eacc (0xfffffe00075026dc): d50331bf  .word 0xd50331bf
0x062ead0 (0xfffffe00075026e0): 5298280c  movz w12, #0xc140
0x062ead4 (0xfffffe00075026e4): b86c6a6c  .word 0xb86c6a6c
0x062ead8 (0xfffffe00075026e8): d50331bf  .word 0xd50331bf
0x062eadc (0xfffffe00075026ec): a901b3eb  stp x11, x12, [sp, #0x18]
0x062eae0 (0xfffffe00075026f0): a900abe9  stp x9, x10, [sp, #0x8]
0x062eae4 (0xfffffe00075026f4): f90003e8  str x8, [sp, #0x0]
0x062eae8 (0xfffffe00075026f8): b0ffdca0  adrp x0, 0xfffffe0007097000
0x062eaec (0xfffffe00075026fc): 91386400  add x0, x0, #0xe19
0x062eaf0 (0xfffffe0007502700): 97f96ce1  bl 0xfffffe000735da84 <_printf>
0x062eaf4 (0xfffffe0007502704): b94037e8  ldr w8, [sp, #0x34]
0x062eaf8 (0xfffffe0007502708): 7100091f  cmp w8, #0x2
0x062eafc (0xfffffe000750270c): 540002eb  b.lt 0xfffffe0007502768
0x062eb00 (0xfffffe0007502710): d0005c36  adrp x22, 0xfffffe0008088000
```

### Xref `DWC3` at `0x062eae8` (`0xfffffe00075026f8` `<_sweet_usb_probe+0x458>`)
```asm
0x062ead8 (0xfffffe00075026e8): d50331bf  .word 0xd50331bf
0x062eadc (0xfffffe00075026ec): a901b3eb  stp x11, x12, [sp, #0x18]
0x062eae0 (0xfffffe00075026f0): a900abe9  stp x9, x10, [sp, #0x8]
0x062eae4 (0xfffffe00075026f4): f90003e8  str x8, [sp, #0x0]
0x062eae8 (0xfffffe00075026f8): b0ffdca0  adrp x0, 0xfffffe0007097000  <-- xref
0x062eaec (0xfffffe00075026fc): 91386400  add x0, x0, #0xe19
0x062eaf0 (0xfffffe0007502700): 97f96ce1  bl 0xfffffe000735da84 <_printf>
0x062eaf4 (0xfffffe0007502704): b94037e8  ldr w8, [sp, #0x34]
0x062eaf8 (0xfffffe0007502708): 7100091f  cmp w8, #0x2
0x062eafc (0xfffffe000750270c): 540002eb  b.lt 0xfffffe0007502768
0x062eb00 (0xfffffe0007502710): d0005c36  adrp x22, 0xfffffe0008088000
0x062eb04 (0xfffffe0007502714): 912862d6  add x22, x22, #0xa18
0x062eb08 (0xfffffe0007502718): f90002d3  str x19, [x22, #0x0]
0x062eb0c (0xfffffe000750271c): 90ffe428  adrp x8, 0xfffffe0007186000
0x062eb10 (0xfffffe0007502720): d503201f  nop
0x062eb14 (0xfffffe0007502724): f9414500  ldr x0, [x8, #0x288]
0x062eb18 (0xfffffe0007502728): 52880001  movz w1, #0x4000
0x062eb1c (0xfffffe000750272c): 5287ffe2  movz w2, #0x3fff
0x062eb20 (0xfffffe0007502730): 52800003  movz w3, #0x0
0x062eb24 (0xfffffe0007502734): 52800004  movz w4, #0x0
0x062eb28 (0xfffffe0007502738): 52900805  movz w5, #0x8040
0x062eb2c (0xfffffe000750273c): 72a00205  movk w5, #0x10, lsl #16
0x062eb30 (0xfffffe0007502740): 52800066  movz w6, #0x3
0x062eb34 (0xfffffe0007502744): 97fbdcea  bl 0xfffffe00073f9aec <_kmem_alloc_contig_guard>
0x062eb38 (0xfffffe0007502748): f90006c1  str x1, [x22, #0x8]
0x062eb3c (0xfffffe000750274c): 34000780  cbz w0, 0xfffffe000750283c
0x062eb40 (0xfffffe0007502750): b0ffdca0  adrp x0, 0xfffffe0007097000
0x062eb44 (0xfffffe0007502754): 913e8400  add x0, x0, #0xfa1
0x062eb48 (0xfffffe0007502758): 97f96ccb  bl 0xfffffe000735da84 <_printf>
0x062eb4c (0xfffffe000750275c): b0ffdca8  adrp x8, 0xfffffe0007097000
0x062eb50 (0xfffffe0007502760): 913eed08  add x8, x8, #0xfbb
0x062eb54 (0xfffffe0007502764): f902a288  str x8, [x20, #0x540]
```

### Xref `DWC3` at `0x062ebac` (`0xfffffe00075027bc` `<_sweet_usb_probe+0x51c>`)
```asm
0x062eb9c (0xfffffe00075027ac): a90027e8  stp x8, x9, [sp, #0x0]
0x062eba0 (0xfffffe00075027b0): b0ffdca0  adrp x0, 0xfffffe0007097000
0x062eba4 (0xfffffe00075027b4): 913a9000  add x0, x0, #0xea4
0x062eba8 (0xfffffe00075027b8): 14000012  b 0xfffffe0007502800 <_sweet_usb_probe+0x560>
0x062ebac (0xfffffe00075027bc): b0ffdca0  adrp x0, 0xfffffe0007097000  <-- xref
0x062ebb0 (0xfffffe00075027c0): 9132c400  add x0, x0, #0xcb1
0x062ebb4 (0xfffffe00075027c4): 97f96cb0  bl 0xfffffe000735da84 <_printf>
0x062ebb8 (0xfffffe00075027c8): b0ffdca8  adrp x8, 0xfffffe0007097000
0x062ebbc (0xfffffe00075027cc): 91344108  add x8, x8, #0xd10
0x062ebc0 (0xfffffe00075027d0): b0ffdca9  adrp x9, 0xfffffe0007097000
0x062ebc4 (0xfffffe00075027d4): 9133b929  add x9, x9, #0xcee
0x062ebc8 (0xfffffe00075027d8): 7100031f  cmp w24, #0x0
0x062ebcc (0xfffffe00075027dc): 9a88b128  .word 0x9a88b128
0x062ebd0 (0xfffffe00075027e0): f00034e9  adrp x9, 0xfffffe0007ba1000
0x062ebd4 (0xfffffe00075027e4): f902a128  str x8, [x9, #0x540]
0x062ebd8 (0xfffffe00075027e8): 14000007  b 0xfffffe0007502804 <_sweet_usb_probe+0x564>
0x062ebdc (0xfffffe00075027ec): b0ffdca0  adrp x0, 0xfffffe0007097000
0x062ebe0 (0xfffffe00075027f0): 91357c00  add x0, x0, #0xd5f
0x062ebe4 (0xfffffe00075027f4): 14000003  b 0xfffffe0007502800 <_sweet_usb_probe+0x560>
0x062ebe8 (0xfffffe00075027f8): b0ffdca0  adrp x0, 0xfffffe0007097000
0x062ebec (0xfffffe00075027fc): 9139c800  add x0, x0, #0xe72
0x062ebf0 (0xfffffe0007502800): 97f96ca1  bl 0xfffffe000735da84 <_printf>
0x062ebf4 (0xfffffe0007502804): f85a83a8  .word 0xf85a83a8
0x062ebf8 (0xfffffe0007502808): 90003a89  adrp x9, 0xfffffe0007c52000
0x062ebfc (0xfffffe000750280c): d503201f  nop
0x062ec00 (0xfffffe0007502810): f945b129  ldr x9, [x9, #0xb60]
0x062ec04 (0xfffffe0007502814): eb08013f  cmp x9, x8
0x062ec08 (0xfffffe0007502818): 540032c1  b.ne 0xfffffe0007502e70
0x062ec0c (0xfffffe000750281c): 9107c3ff  add sp, sp, #0x1f0
0x062ec10 (0xfffffe0007502820): a9457bfd  ldp x29, x30, [sp, #0x50]
0x062ec14 (0xfffffe0007502824): a9444ff4  ldp x20, x19, [sp, #0x40]
0x062ec18 (0xfffffe0007502828): a94357f6  ldp x22, x21, [sp, #0x30]
```

### Xref `DWC3` at `0x062ebdc` (`0xfffffe00075027ec` `<_sweet_usb_probe+0x54c>`)
```asm
0x062ebcc (0xfffffe00075027dc): 9a88b128  .word 0x9a88b128
0x062ebd0 (0xfffffe00075027e0): f00034e9  adrp x9, 0xfffffe0007ba1000
0x062ebd4 (0xfffffe00075027e4): f902a128  str x8, [x9, #0x540]
0x062ebd8 (0xfffffe00075027e8): 14000007  b 0xfffffe0007502804 <_sweet_usb_probe+0x564>
0x062ebdc (0xfffffe00075027ec): b0ffdca0  adrp x0, 0xfffffe0007097000  <-- xref
0x062ebe0 (0xfffffe00075027f0): 91357c00  add x0, x0, #0xd5f
0x062ebe4 (0xfffffe00075027f4): 14000003  b 0xfffffe0007502800 <_sweet_usb_probe+0x560>
0x062ebe8 (0xfffffe00075027f8): b0ffdca0  adrp x0, 0xfffffe0007097000
0x062ebec (0xfffffe00075027fc): 9139c800  add x0, x0, #0xe72
0x062ebf0 (0xfffffe0007502800): 97f96ca1  bl 0xfffffe000735da84 <_printf>
0x062ebf4 (0xfffffe0007502804): f85a83a8  .word 0xf85a83a8
0x062ebf8 (0xfffffe0007502808): 90003a89  adrp x9, 0xfffffe0007c52000
0x062ebfc (0xfffffe000750280c): d503201f  nop
0x062ec00 (0xfffffe0007502810): f945b129  ldr x9, [x9, #0xb60]
0x062ec04 (0xfffffe0007502814): eb08013f  cmp x9, x8
0x062ec08 (0xfffffe0007502818): 540032c1  b.ne 0xfffffe0007502e70
0x062ec0c (0xfffffe000750281c): 9107c3ff  add sp, sp, #0x1f0
0x062ec10 (0xfffffe0007502820): a9457bfd  ldp x29, x30, [sp, #0x50]
0x062ec14 (0xfffffe0007502824): a9444ff4  ldp x20, x19, [sp, #0x40]
0x062ec18 (0xfffffe0007502828): a94357f6  ldp x22, x21, [sp, #0x30]
0x062ec1c (0xfffffe000750282c): a9425ff8  ldp x24, x23, [sp, #0x20]
0x062ec20 (0xfffffe0007502830): a94167fa  ldp x26, x25, [sp, #0x10]
0x062ec24 (0xfffffe0007502834): a8c66ffc  ldp x28, x27, [sp, #0x60]
0x062ec28 (0xfffffe0007502838): d65f03c0  ret
0x062ec2c (0xfffffe000750283c): b0ffe428  adrp x8, 0xfffffe0007187000
0x062ec30 (0xfffffe0007502840): d503201f  nop
0x062ec34 (0xfffffe0007502844): f9448500  ldr x0, [x8, #0x908]
0x062ec38 (0xfffffe0007502848): 97fe0a27  bl 0xfffffe00074850e4 <_pmap_find_phys>
0x062ec3c (0xfffffe000750284c): 34fff8e0  cbz w0, 0xfffffe0007502768
0x062ec40 (0xfffffe0007502850): 910123f3  add x19, sp, #0x48
0x062ec44 (0xfffffe0007502854): f9001fff  str x31, [sp, #0x38]
0x062ec48 (0xfffffe0007502858): d3727c08  .word 0xd3727c08
```

### Xref `sweetkeys` at `0x062a380` (`0xfffffe00074fdf90` `<_sweet_keys_init+0x3c>`)
```asm
0x062a370 (0xfffffe00074fdf80): 395b212a  ldrb w10, [x9, #0x6c8]
0x062a374 (0xfffffe00074fdf84): 37003e6a  tbnz w10, #0, 0xfffffe00074fe750
0x062a378 (0xfffffe00074fdf88): f81983bf  .word 0xf81983bf
0x062a37c (0xfffffe00074fdf8c): 391b2128  strb w8, [x9, #0x6c8]
0x062a380 (0xfffffe00074fdf90): b0ffdcc0  adrp x0, 0xfffffe0007096000  <-- xref
0x062a384 (0xfffffe00074fdf94): 91342c00  add x0, x0, #0xd0b
0x062a388 (0xfffffe00074fdf98): d10173a1  sub x1, x29, #0x5c
0x062a38c (0xfffffe00074fdf9c): 52800082  movz w2, #0x4
0x062a390 (0xfffffe00074fdfa0): 9416af35  bl 0xfffffe0007aa9c74 <_PE_parse_boot_argn>
0x062a394 (0xfffffe00074fdfa4): b85a43a8  .word 0xb85a43a8
0x062a398 (0xfffffe00074fdfa8): 340007e8  cbz w8, 0xfffffe00074fe0a4
0x062a39c (0xfffffe00074fdfac): 52a18880  movz w0, #0xc44, lsl #16
0x062a3a0 (0xfffffe00074fdfb0): 52840001  movz w1, #0x2000
0x062a3a4 (0xfffffe00074fdfb4): 97fe9cd3  bl 0xfffffe00074a5300 <_ml_io_map>
0x062a3a8 (0xfffffe00074fdfb8): f0005c55  adrp x21, 0xfffffe0008088000
0x062a3ac (0xfffffe00074fdfbc): f9036aa0  str x0, [x21, #0x6d0]
0x062a3b0 (0xfffffe00074fdfc0): 52940000  movz w0, #0xa000
0x062a3b4 (0xfffffe00074fdfc4): 72a18800  movk w0, #0xc40, lsl #16
0x062a3b8 (0xfffffe00074fdfc8): 52820001  movz w1, #0x1000
0x062a3bc (0xfffffe00074fdfcc): 97fe9ccd  bl 0xfffffe00074a5300 <_ml_io_map>
0x062a3c0 (0xfffffe00074fdfd0): f0005c56  adrp x22, 0xfffffe0008088000
0x062a3c4 (0xfffffe00074fdfd4): f9036ec0  str x0, [x22, #0x6d8]
0x062a3c8 (0xfffffe00074fdfd8): 52a1cc00  movz w0, #0xe60, lsl #16
0x062a3cc (0xfffffe00074fdfdc): 52a00021  movz w1, #0x1, lsl #16
0x062a3d0 (0xfffffe00074fdfe0): 97fe9cc8  bl 0xfffffe00074a5300 <_ml_io_map>
0x062a3d4 (0xfffffe00074fdfe4): f0005c58  adrp x24, 0xfffffe0008088000
0x062a3d8 (0xfffffe00074fdfe8): f9037300  str x0, [x24, #0x6e0]
0x062a3dc (0xfffffe00074fdfec): f9436aa8  ldr x8, [x21, #0x6d0]
0x062a3e0 (0xfffffe00074fdff0): b4000608  cbz x8, 0xfffffe00074fe0b0
0x062a3e4 (0xfffffe00074fdff4): f9436ec9  ldr x9, [x22, #0x6d8]
0x062a3e8 (0xfffffe00074fdff8): b40005c9  cbz x9, 0xfffffe00074fe0b0
0x062a3ec (0xfffffe00074fdffc): b40005a0  cbz x0, 0xfffffe00074fe0b0
```

### Xref `sweetkeys` at `0x062a494` (`0xfffffe00074fe0a4` `<_sweet_keys_init+0x150>`)
```asm
0x062a484 (0xfffffe00074fe094): 7200099f  tst/ands w12, ...
0x062a488 (0xfffffe00074fe098): 7a4019a4  .word 0x7a4019a4
0x062a48c (0xfffffe00074fe09c): 1a8b010b  .word 0x1a8b010b
0x062a490 (0xfffffe00074fe0a0): 17ffffee  b 0xfffffe00074fe058 <_sweet_keys_init+0x104>
0x062a494 (0xfffffe00074fe0a4): 90ffdcc0  adrp x0, 0xfffffe0007096000  <-- xref
0x062a498 (0xfffffe00074fe0a8): 91345400  add x0, x0, #0xd15
0x062a49c (0xfffffe00074fe0ac): 140001a8  b 0xfffffe00074fe74c <_sweet_keys_init+0x7f8>
0x062a4a0 (0xfffffe00074fe0b0): 90ffdcc0  adrp x0, 0xfffffe0007096000
0x062a4a4 (0xfffffe00074fe0b4): 9134e400  add x0, x0, #0xd39
0x062a4a8 (0xfffffe00074fe0b8): 140001a5  b 0xfffffe00074fe74c <_sweet_keys_init+0x7f8>
0x062a4ac (0xfffffe00074fe0bc): a9004fe8  stp x8, x19, [sp, #0x0]
0x062a4b0 (0xfffffe00074fe0c0): 90ffdcc0  adrp x0, 0xfffffe0007096000
0x062a4b4 (0xfffffe00074fe0c4): 91356800  add x0, x0, #0xd5a
0x062a4b8 (0xfffffe00074fe0c8): 140001a1  b 0xfffffe00074fe74c <_sweet_keys_init+0x7f8>
0x062a4bc (0xfffffe00074fe0cc): d2800009  movz x9, #0x0
0x062a4c0 (0xfffffe00074fe0d0): f000350f  adrp x15, 0xfffffe0007ba1000
0x062a4c4 (0xfffffe00074fe0d4): 790a59eb  strh w11, [x15, #0x52c]
0x062a4c8 (0xfffffe00074fe0d8): 529fffea  movz w10, #0xffff
0x062a4cc (0xfffffe00074fe0dc): 5280e00b  movz w11, #0x700
0x062a4d0 (0xfffffe00074fe0e0): 5298a00c  movz w12, #0xc500
0x062a4d4 (0xfffffe00074fe0e4): 529fffe8  movz w8, #0xffff
0x062a4d8 (0xfffffe00074fe0e8): 14000005  b 0xfffffe00074fe0fc <_sweet_keys_init+0x1a8>
0x062a4dc (0xfffffe00074fe0ec): 91000529  add x9, x9, #0x1
0x062a4e0 (0xfffffe00074fe0f0): 9100116b  add x11, x11, #0x4
0x062a4e4 (0xfffffe00074fe0f4): eb09027f  cmp x19, x9
0x062a4e8 (0xfffffe00074fe0f8): 54000200  b.eq 0xfffffe00074fe138
0x062a4ec (0xfffffe00074fe0fc): f9436aad  ldr x13, [x21, #0x6d0]
0x062a4f0 (0xfffffe00074fe100): 8b0d016d  .word 0x8b0d016d
0x062a4f4 (0xfffffe00074fe104): b94201ad  ldr w13, [x13, #0x200]
0x062a4f8 (0xfffffe00074fe108): d50331bf  .word 0xd50331bf
0x062a4fc (0xfffffe00074fe10c): 12182dad  .word 0x12182dad
0x062a500 (0xfffffe00074fe110): 6b0c01bf  cmp w13, w12
```

### Xref `sweetkeys` at `0x062aa1c` (`0xfffffe00074fe62c` `<_sweet_keys_init+0x6d8>`)
```asm
0x062aa0c (0xfffffe00074fe61c): 97f97d1a  bl 0xfffffe000735da84 <_printf>
0x062aa10 (0xfffffe00074fe620): 529fffe8  movz w8, #0xffff
0x062aa14 (0xfffffe00074fe624): f0003509  adrp x9, 0xfffffe0007ba1000
0x062aa18 (0xfffffe00074fe628): 790a5d28  strh w8, [x9, #0x52e]
0x062aa1c (0xfffffe00074fe62c): 90ffdcc0  adrp x0, 0xfffffe0007096000  <-- xref
0x062aa20 (0xfffffe00074fe630): 91399000  add x0, x0, #0xe64
0x062aa24 (0xfffffe00074fe634): f0003513  adrp x19, 0xfffffe0007ba1000
0x062aa28 (0xfffffe00074fe638): 9114c273  add x19, x19, #0x530
0x062aa2c (0xfffffe00074fe63c): aa1303e1  mov x1, x19
0x062aa30 (0xfffffe00074fe640): 52800082  movz w2, #0x4
0x062aa34 (0xfffffe00074fe644): 9416ad8c  bl 0xfffffe0007aa9c74 <_PE_parse_boot_argn>
0x062aa38 (0xfffffe00074fe648): 90ffdcc0  adrp x0, 0xfffffe0007096000
0x062aa3c (0xfffffe00074fe64c): 9139c400  add x0, x0, #0xe71
0x062aa40 (0xfffffe00074fe650): f0003501  adrp x1, 0xfffffe0007ba1000
0x062aa44 (0xfffffe00074fe654): 9114d021  add x1, x1, #0x534
0x062aa48 (0xfffffe00074fe658): 52800082  movz w2, #0x4
0x062aa4c (0xfffffe00074fe65c): 9416ad86  bl 0xfffffe0007aa9c74 <_PE_parse_boot_argn>
0x062aa50 (0xfffffe00074fe660): 90ffdcc0  adrp x0, 0xfffffe0007096000
0x062aa54 (0xfffffe00074fe664): 913a0c00  add x0, x0, #0xe83
0x062aa58 (0xfffffe00074fe668): f0003501  adrp x1, 0xfffffe0007ba1000
0x062aa5c (0xfffffe00074fe66c): 9114e021  add x1, x1, #0x538
0x062aa60 (0xfffffe00074fe670): 52800082  movz w2, #0x4
0x062aa64 (0xfffffe00074fe674): 9416ad80  bl 0xfffffe0007aa9c74 <_PE_parse_boot_argn>
0x062aa68 (0xfffffe00074fe678): b9400268  ldr w8, [x19, #0x0]
0x062aa6c (0xfffffe00074fe67c): d0005c53  adrp x19, 0xfffffe0008088000
0x062aa70 (0xfffffe00074fe680): 34000788  cbz w8, 0xfffffe00074fe770
0x062aa74 (0xfffffe00074fe684): 52920000  movz w0, #0x9000
0x062aa78 (0xfffffe00074fe688): 72a07aa0  movk w0, #0x3d5, lsl #16
0x062aa7c (0xfffffe00074fe68c): 52820001  movz w1, #0x1000
0x062aa80 (0xfffffe00074fe690): 97fe9b1c  bl 0xfffffe00074a5300 <_ml_io_map>
0x062aa84 (0xfffffe00074fe694): f9037a60  str x0, [x19, #0x6f0]
0x062aa88 (0xfffffe00074fe698): b40003e0  cbz x0, 0xfffffe00074fe714
```

### Xref `sweetkeys` at `0x062aa38` (`0xfffffe00074fe648` `<_sweet_keys_init+0x6f4>`)
```asm
0x062aa28 (0xfffffe00074fe638): 9114c273  add x19, x19, #0x530
0x062aa2c (0xfffffe00074fe63c): aa1303e1  mov x1, x19
0x062aa30 (0xfffffe00074fe640): 52800082  movz w2, #0x4
0x062aa34 (0xfffffe00074fe644): 9416ad8c  bl 0xfffffe0007aa9c74 <_PE_parse_boot_argn>
0x062aa38 (0xfffffe00074fe648): 90ffdcc0  adrp x0, 0xfffffe0007096000  <-- xref
0x062aa3c (0xfffffe00074fe64c): 9139c400  add x0, x0, #0xe71
0x062aa40 (0xfffffe00074fe650): f0003501  adrp x1, 0xfffffe0007ba1000
0x062aa44 (0xfffffe00074fe654): 9114d021  add x1, x1, #0x534
0x062aa48 (0xfffffe00074fe658): 52800082  movz w2, #0x4
0x062aa4c (0xfffffe00074fe65c): 9416ad86  bl 0xfffffe0007aa9c74 <_PE_parse_boot_argn>
0x062aa50 (0xfffffe00074fe660): 90ffdcc0  adrp x0, 0xfffffe0007096000
0x062aa54 (0xfffffe00074fe664): 913a0c00  add x0, x0, #0xe83
0x062aa58 (0xfffffe00074fe668): f0003501  adrp x1, 0xfffffe0007ba1000
0x062aa5c (0xfffffe00074fe66c): 9114e021  add x1, x1, #0x538
0x062aa60 (0xfffffe00074fe670): 52800082  movz w2, #0x4
0x062aa64 (0xfffffe00074fe674): 9416ad80  bl 0xfffffe0007aa9c74 <_PE_parse_boot_argn>
0x062aa68 (0xfffffe00074fe678): b9400268  ldr w8, [x19, #0x0]
0x062aa6c (0xfffffe00074fe67c): d0005c53  adrp x19, 0xfffffe0008088000
0x062aa70 (0xfffffe00074fe680): 34000788  cbz w8, 0xfffffe00074fe770
0x062aa74 (0xfffffe00074fe684): 52920000  movz w0, #0x9000
0x062aa78 (0xfffffe00074fe688): 72a07aa0  movk w0, #0x3d5, lsl #16
0x062aa7c (0xfffffe00074fe68c): 52820001  movz w1, #0x1000
0x062aa80 (0xfffffe00074fe690): 97fe9b1c  bl 0xfffffe00074a5300 <_ml_io_map>
0x062aa84 (0xfffffe00074fe694): f9037a60  str x0, [x19, #0x6f0]
0x062aa88 (0xfffffe00074fe698): b40003e0  cbz x0, 0xfffffe00074fe714
0x062aa8c (0xfffffe00074fe69c): b9400008  ldr w8, [x0, #0x0]
0x062aa90 (0xfffffe00074fe6a0): d50331bf  .word 0xd50331bf
0x062aa94 (0xfffffe00074fe6a4): 128047e9  movn w9, #0x23f
0x062aa98 (0xfffffe00074fe6a8): 0a090108  .word 0x0a090108
0x062aa9c (0xfffffe00074fe6ac): 32000508  .word 0x32000508
0x062aaa0 (0xfffffe00074fe6b0): d50332bf  .word 0xd50332bf
0x062aaa4 (0xfffffe00074fe6b4): f9437a69  ldr x9, [x19, #0x6f0]
```

### Xref `sweetkeys` at `0x062aa50` (`0xfffffe00074fe660` `<_sweet_keys_init+0x70c>`)
```asm
0x062aa40 (0xfffffe00074fe650): f0003501  adrp x1, 0xfffffe0007ba1000
0x062aa44 (0xfffffe00074fe654): 9114d021  add x1, x1, #0x534
0x062aa48 (0xfffffe00074fe658): 52800082  movz w2, #0x4
0x062aa4c (0xfffffe00074fe65c): 9416ad86  bl 0xfffffe0007aa9c74 <_PE_parse_boot_argn>
0x062aa50 (0xfffffe00074fe660): 90ffdcc0  adrp x0, 0xfffffe0007096000  <-- xref
0x062aa54 (0xfffffe00074fe664): 913a0c00  add x0, x0, #0xe83
0x062aa58 (0xfffffe00074fe668): f0003501  adrp x1, 0xfffffe0007ba1000
0x062aa5c (0xfffffe00074fe66c): 9114e021  add x1, x1, #0x538
0x062aa60 (0xfffffe00074fe670): 52800082  movz w2, #0x4
0x062aa64 (0xfffffe00074fe674): 9416ad80  bl 0xfffffe0007aa9c74 <_PE_parse_boot_argn>
0x062aa68 (0xfffffe00074fe678): b9400268  ldr w8, [x19, #0x0]
0x062aa6c (0xfffffe00074fe67c): d0005c53  adrp x19, 0xfffffe0008088000
0x062aa70 (0xfffffe00074fe680): 34000788  cbz w8, 0xfffffe00074fe770
0x062aa74 (0xfffffe00074fe684): 52920000  movz w0, #0x9000
0x062aa78 (0xfffffe00074fe688): 72a07aa0  movk w0, #0x3d5, lsl #16
0x062aa7c (0xfffffe00074fe68c): 52820001  movz w1, #0x1000
0x062aa80 (0xfffffe00074fe690): 97fe9b1c  bl 0xfffffe00074a5300 <_ml_io_map>
0x062aa84 (0xfffffe00074fe694): f9037a60  str x0, [x19, #0x6f0]
0x062aa88 (0xfffffe00074fe698): b40003e0  cbz x0, 0xfffffe00074fe714
0x062aa8c (0xfffffe00074fe69c): b9400008  ldr w8, [x0, #0x0]
0x062aa90 (0xfffffe00074fe6a0): d50331bf  .word 0xd50331bf
0x062aa94 (0xfffffe00074fe6a4): 128047e9  movn w9, #0x23f
0x062aa98 (0xfffffe00074fe6a8): 0a090108  .word 0x0a090108
0x062aa9c (0xfffffe00074fe6ac): 32000508  .word 0x32000508
0x062aaa0 (0xfffffe00074fe6b0): d50332bf  .word 0xd50332bf
0x062aaa4 (0xfffffe00074fe6b4): f9437a69  ldr x9, [x19, #0x6f0]
0x062aaa8 (0xfffffe00074fe6b8): b9000128  str w8, [x9, #0x0]
0x062aaac (0xfffffe00074fe6bc): d503339f  .word 0xd503339f
0x062aab0 (0xfffffe00074fe6c0): 52800c80  movz w0, #0x64
0x062aab4 (0xfffffe00074fe6c4): 97f8d465  bl 0xfffffe0007333858 <_delay>
0x062aab8 (0xfffffe00074fe6c8): f9437a68  ldr x8, [x19, #0x6f0]
0x062aabc (0xfffffe00074fe6cc): b9400108  ldr w8, [x8, #0x0]
```

## 5. Relevant USB & Keys Functions Disassembly

### `_sweet_keys_init` (`0x062a344`, VA `0xfffffe00074fdf54`, size `0x834`)
```asm
0x062a344 (0xfffffe00074fdf54): d10403ff  sub sp, sp, #0x100
0x062a348 (0xfffffe00074fdf58): a90a6ffc  stp x28, x27, [sp, #0xa0]
0x062a34c (0xfffffe00074fdf5c): a90b67fa  stp x26, x25, [sp, #0xb0]
0x062a350 (0xfffffe00074fdf60): a90c5ff8  stp x24, x23, [sp, #0xc0]
0x062a354 (0xfffffe00074fdf64): a90d57f6  stp x22, x21, [sp, #0xd0]
0x062a358 (0xfffffe00074fdf68): a90e4ff4  stp x20, x19, [sp, #0xe0]
0x062a35c (0xfffffe00074fdf6c): a90f7bfd  stp x29, x30, [sp, #0xf0]
0x062a360 (0xfffffe00074fdf70): 9103c3fd  add x29, sp, #0xf0
0x062a364 (0xfffffe00074fdf74): 52800028  movz w8, #0x1
0x062a368 (0xfffffe00074fdf78): b81a43a8  .word 0xb81a43a8
0x062a36c (0xfffffe00074fdf7c): f0005c49  adrp x9, 0xfffffe0008088000
0x062a370 (0xfffffe00074fdf80): 395b212a  ldrb w10, [x9, #0x6c8]
0x062a374 (0xfffffe00074fdf84): 37003e6a  tbnz w10, #0, 0xfffffe00074fe750
0x062a378 (0xfffffe00074fdf88): f81983bf  .word 0xf81983bf
0x062a37c (0xfffffe00074fdf8c): 391b2128  strb w8, [x9, #0x6c8]
0x062a380 (0xfffffe00074fdf90): b0ffdcc0  adrp x0, 0xfffffe0007096000
0x062a384 (0xfffffe00074fdf94): 91342c00  add x0, x0, #0xd0b
0x062a388 (0xfffffe00074fdf98): d10173a1  sub x1, x29, #0x5c
0x062a38c (0xfffffe00074fdf9c): 52800082  movz w2, #0x4
0x062a390 (0xfffffe00074fdfa0): 9416af35  bl 0xfffffe0007aa9c74 <_PE_parse_boot_argn>
0x062a394 (0xfffffe00074fdfa4): b85a43a8  .word 0xb85a43a8
0x062a398 (0xfffffe00074fdfa8): 340007e8  cbz w8, 0xfffffe00074fe0a4
0x062a39c (0xfffffe00074fdfac): 52a18880  movz w0, #0xc44, lsl #16
0x062a3a0 (0xfffffe00074fdfb0): 52840001  movz w1, #0x2000
0x062a3a4 (0xfffffe00074fdfb4): 97fe9cd3  bl 0xfffffe00074a5300 <_ml_io_map>
0x062a3a8 (0xfffffe00074fdfb8): f0005c55  adrp x21, 0xfffffe0008088000
0x062a3ac (0xfffffe00074fdfbc): f9036aa0  str x0, [x21, #0x6d0]
0x062a3b0 (0xfffffe00074fdfc0): 52940000  movz w0, #0xa000
0x062a3b4 (0xfffffe00074fdfc4): 72a18800  movk w0, #0xc40, lsl #16
0x062a3b8 (0xfffffe00074fdfc8): 52820001  movz w1, #0x1000
0x062a3bc (0xfffffe00074fdfcc): 97fe9ccd  bl 0xfffffe00074a5300 <_ml_io_map>
0x062a3c0 (0xfffffe00074fdfd0): f0005c56  adrp x22, 0xfffffe0008088000
0x062a3c4 (0xfffffe00074fdfd4): f9036ec0  str x0, [x22, #0x6d8]
0x062a3c8 (0xfffffe00074fdfd8): 52a1cc00  movz w0, #0xe60, lsl #16
0x062a3cc (0xfffffe00074fdfdc): 52a00021  movz w1, #0x1, lsl #16
0x062a3d0 (0xfffffe00074fdfe0): 97fe9cc8  bl 0xfffffe00074a5300 <_ml_io_map>
0x062a3d4 (0xfffffe00074fdfe4): f0005c58  adrp x24, 0xfffffe0008088000
0x062a3d8 (0xfffffe00074fdfe8): f9037300  str x0, [x24, #0x6e0]
0x062a3dc (0xfffffe00074fdfec): f9436aa8  ldr x8, [x21, #0x6d0]
0x062a3e0 (0xfffffe00074fdff0): b4000608  cbz x8, 0xfffffe00074fe0b0
0x062a3e4 (0xfffffe00074fdff4): f9436ec9  ldr x9, [x22, #0x6d8]
0x062a3e8 (0xfffffe00074fdff8): b40005c9  cbz x9, 0xfffffe00074fe0b0
0x062a3ec (0xfffffe00074fdffc): b40005a0  cbz x0, 0xfffffe00074fe0b0
0x062a3f0 (0xfffffe00074fe000): b9400108  ldr w8, [x8, #0x0]
0x062a3f4 (0xfffffe00074fe004): d50331bf  .word 0xd50331bf
0x062a3f8 (0xfffffe00074fe008): d0005c54  adrp x20, 0xfffffe0008088000
0x062a3fc (0xfffffe00074fe00c): b906ea88  str w8, [x20, #0x6e8]
0x062a400 (0xfffffe00074fe010): f9436aa8  ldr x8, [x21, #0x6d0]
0x062a404 (0xfffffe00074fe014): b9400508  ldr w8, [x8, #0x4]
0x062a408 (0xfffffe00074fe018): d50331bf  .word 0xd50331bf
0x062a40c (0xfffffe00074fe01c): 92402913  .word 0x92402913
0x062a410 (0xfffffe00074fe020): b946ea88  ldr w8, [x20, #0x6e8]
0x062a414 (0xfffffe00074fe024): 52b20009  movz w9, #0x9000, lsl #16
0x062a418 (0xfffffe00074fe028): 0b090109  .word 0x0b090109
0x062a41c (0xfffffe00074fe02c): 531d7d29  .word 0x531d7d29
0x062a420 (0xfffffe00074fe030): 71001d3f  cmp w9, #0x7
0x062a424 (0xfffffe00074fe034): 54000443  b.cc 0xfffffe00074fe0bc
0x062a428 (0xfffffe00074fe038): 34000433  cbz w19, 0xfffffe00074fe0bc
0x062a42c (0xfffffe00074fe03c): 7108067f  cmp w19, #0x201
0x062a430 (0xfffffe00074fe040): 540003e2  b.cs 0xfffffe00074fe0bc
0x062a434 (0xfffffe00074fe044): d2800008  movz x8, #0x0
0x062a438 (0xfffffe00074fe048): 529fffe9  movz w9, #0xffff
0x062a43c (0xfffffe00074fe04c): 5280e00a  movz w10, #0x700
0x062a440 (0xfffffe00074fe050): 529fffeb  movz w11, #0xffff
0x062a444 (0xfffffe00074fe054): 14000005  b 0xfffffe00074fe068 <_sweet_keys_init+0x114>
0x062a448 (0xfffffe00074fe058): 91000508  add x8, x8, #0x1
0x062a44c (0xfffffe00074fe05c): 9100114a  add x10, x10, #0x4
0x062a450 (0xfffffe00074fe060): eb08027f  cmp x19, x8
0x062a454 (0xfffffe00074fe064): 54000340  b.eq 0xfffffe00074fe0cc
0x062a458 (0xfffffe00074fe068): f9436aac  ldr x12, [x21, #0x6d0]
0x062a45c (0xfffffe00074fe06c): 8b0c014c  .word 0x8b0c014c
0x062a460 (0xfffffe00074fe070): b942018c  ldr w12, [x12, #0x200]
0x062a464 (0xfffffe00074fe074): d50331bf  .word 0xd50331bf
0x062a468 (0xfffffe00074fe078): 12182d8c  .word 0x12182d8c
0x062a46c (0xfffffe00074fe07c): 7120019f  cmp w12, #0x800
0x062a470 (0xfffffe00074fe080): 54fffec1  b.ne 0xfffffe00074fe058
0x062a474 (0xfffffe00074fe084): f9436ecc  ldr x12, [x22, #0x6d8]
0x062a478 (0xfffffe00074fe088): b86c694c  .word 0xb86c694c
0x062a47c (0xfffffe00074fe08c): d50331bf  .word 0xd50331bf
0x062a480 (0xfffffe00074fe090): 0a2b012d  .word 0x0a2b012d
0x062a484 (0xfffffe00074fe094): 7200099f  tst/ands w12, ...
0x062a488 (0xfffffe00074fe098): 7a4019a4  .word 0x7a4019a4
0x062a48c (0xfffffe00074fe09c): 1a8b010b  .word 0x1a8b010b
0x062a490 (0xfffffe00074fe0a0): 17ffffee  b 0xfffffe00074fe058 <_sweet_keys_init+0x104>
0x062a494 (0xfffffe00074fe0a4): 90ffdcc0  adrp x0, 0xfffffe0007096000
0x062a498 (0xfffffe00074fe0a8): 91345400  add x0, x0, #0xd15
0x062a49c (0xfffffe00074fe0ac): 140001a8  b 0xfffffe00074fe74c <_sweet_keys_init+0x7f8>
0x062a4a0 (0xfffffe00074fe0b0): 90ffdcc0  adrp x0, 0xfffffe0007096000
0x062a4a4 (0xfffffe00074fe0b4): 9134e400  add x0, x0, #0xd39
0x062a4a8 (0xfffffe00074fe0b8): 140001a5  b 0xfffffe00074fe74c <_sweet_keys_init+0x7f8>
0x062a4ac (0xfffffe00074fe0bc): a9004fe8  stp x8, x19, [sp, #0x0]
0x062a4b0 (0xfffffe00074fe0c0): 90ffdcc0  adrp x0, 0xfffffe0007096000
0x062a4b4 (0xfffffe00074fe0c4): 91356800  add x0, x0, #0xd5a
0x062a4b8 (0xfffffe00074fe0c8): 140001a1  b 0xfffffe00074fe74c <_sweet_keys_init+0x7f8>
0x062a4bc (0xfffffe00074fe0cc): d2800009  movz x9, #0x0
0x062a4c0 (0xfffffe00074fe0d0): f000350f  adrp x15, 0xfffffe0007ba1000
0x062a4c4 (0xfffffe00074fe0d4): 790a59eb  strh w11, [x15, #0x52c]
0x062a4c8 (0xfffffe00074fe0d8): 529fffea  movz w10, #0xffff
0x062a4cc (0xfffffe00074fe0dc): 5280e00b  movz w11, #0x700
0x062a4d0 (0xfffffe00074fe0e0): 5298a00c  movz w12, #0xc500
0x062a4d4 (0xfffffe00074fe0e4): 529fffe8  movz w8, #0xffff
0x062a4d8 (0xfffffe00074fe0e8): 14000005  b 0xfffffe00074fe0fc <_sweet_keys_init+0x1a8>
0x062a4dc (0xfffffe00074fe0ec): 91000529  add x9, x9, #0x1
0x062a4e0 (0xfffffe00074fe0f0): 9100116b  add x11, x11, #0x4
0x062a4e4 (0xfffffe00074fe0f4): eb09027f  cmp x19, x9
0x062a4e8 (0xfffffe00074fe0f8): 54000200  b.eq 0xfffffe00074fe138
0x062a4ec (0xfffffe00074fe0fc): f9436aad  ldr x13, [x21, #0x6d0]
0x062a4f0 (0xfffffe00074fe100): 8b0d016d  .word 0x8b0d016d
0x062a4f4 (0xfffffe00074fe104): b94201ad  ldr w13, [x13, #0x200]
0x062a4f8 (0xfffffe00074fe108): d50331bf  .word 0xd50331bf
0x062a4fc (0xfffffe00074fe10c): 12182dad  .word 0x12182dad
0x062a500 (0xfffffe00074fe110): 6b0c01bf  cmp w13, w12
0x062a504 (0xfffffe00074fe114): 54fffec1  b.ne 0xfffffe00074fe0ec
0x062a508 (0xfffffe00074fe118): f9436ecd  ldr x13, [x22, #0x6d8]
0x062a50c (0xfffffe00074fe11c): b86d696d  .word 0xb86d696d
0x062a510 (0xfffffe00074fe120): d50331bf  .word 0xd50331bf
0x062a514 (0xfffffe00074fe124): 0a28014e  .word 0x0a28014e
0x062a518 (0xfffffe00074fe128): 720009bf  tst/ands w13, ...
0x062a51c (0xfffffe00074fe12c): 7a4019c4  .word 0x7a4019c4
0x062a520 (0xfffffe00074fe130): 1a880128  .word 0x1a880128
0x062a524 (0xfffffe00074fe134): 17ffffee  b 0xfffffe00074fe0ec <_sweet_keys_init+0x198>
0x062a528 (0xfffffe00074fe138): 5280201c  movz w28, #0x100
0x062a52c (0xfffffe00074fe13c): 72a1001c  movk w28, #0x800, lsl #16
0x062a530 (0xfffffe00074fe140): f000351a  adrp x26, 0xfffffe0007ba1000
0x062a534 (0xfffffe00074fe144): 790a5f48  strh w8, [x26, #0x52e]
0x062a538 (0xfffffe00074fe148): 794a59e9  ldrh w9, [x15, #0x52c]
0x062a53c (0xfffffe00074fe14c): 529ffff7  movz w23, #0xffff
0x062a540 (0xfffffe00074fe150): d0005c5b  adrp x27, 0xfffffe0008088000
0x062a544 (0xfffffe00074fe154): eb17013f  cmp x9, x23
0x062a548 (0xfffffe00074fe158): 540003a0  b.eq 0xfffffe00074fe1cc
0x062a54c (0xfffffe00074fe15c): d379e135  .word 0xd379e135
0x062a550 (0xfffffe00074fe160): d50332bf  .word 0xd50332bf
0x062a554 (0xfffffe00074fe164): f9437308  ldr x8, [x24, #0x6e0]
0x062a558 (0xfffffe00074fe168): b835691c  .word 0xb835691c
0x062a55c (0xfffffe00074fe16c): d503339f  .word 0xd503339f
0x062a560 (0xfffffe00074fe170): 52800116  movz w22, #0x8
0x062a564 (0xfffffe00074fe174): b3793d36  .word 0xb3793d36
0x062a568 (0xfffffe00074fe178): f9437308  ldr x8, [x24, #0x6e0]
0x062a56c (0xfffffe00074fe17c): b8766908  .word 0xb8766908
0x062a570 (0xfffffe00074fe180): d50331bf  .word 0xd50331bf
0x062a574 (0xfffffe00074fe184): b906fb68  str w8, [x27, #0x6f8]
0x062a578 (0xfffffe00074fe188): 37000168  tbnz w8, #0, 0xfffffe00074fe1b4
0x062a57c (0xfffffe00074fe18c): 52807d19  movz w25, #0x3e8
0x062a580 (0xfffffe00074fe190): 52800020  movz w0, #0x1
0x062a584 (0xfffffe00074fe194): 97f8d5b1  bl 0xfffffe0007333858 <_delay>
0x062a588 (0xfffffe00074fe198): 71000739  subs w25, w25, #0x1
0x062a58c (0xfffffe00074fe19c): 54000360  b.eq 0xfffffe00074fe208
0x062a590 (0xfffffe00074fe1a0): f9437308  ldr x8, [x24, #0x6e0]
0x062a594 (0xfffffe00074fe1a4): b8766908  .word 0xb8766908
0x062a598 (0xfffffe00074fe1a8): d50331bf  .word 0xd50331bf
0x062a59c (0xfffffe00074fe1ac): b906fb68  str w8, [x27, #0x6f8]
0x062a5a0 (0xfffffe00074fe1b0): 3607ff08  tbz w8, #0, 0xfffffe00074fe190
0x062a5a4 (0xfffffe00074fe1b4): 721f091f  tst/ands w8, ...
0x062a5a8 (0xfffffe00074fe1b8): 54000180  b.eq 0xfffffe00074fe1e8
0x062a5ac (0xfffffe00074fe1bc): 5280000b  movz w11, #0x0
0x062a5b0 (0xfffffe00074fe1c0): 52800009  movz w9, #0x0
0x062a5b4 (0xfffffe00074fe1c4): 52800028  movz w8, #0x1
0x062a5b8 (0xfffffe00074fe1c8): 14000012  b 0xfffffe00074fe210 <_sweet_keys_init+0x2bc>
0x062a5bc (0xfffffe00074fe1cc): 5280000b  movz w11, #0x0
0x062a5c0 (0xfffffe00074fe1d0): b81943bf  .word 0xb81943bf
0x062a5c4 (0xfffffe00074fe1d4): 6a2802ff  .word 0x6a2802ff
0x062a5c8 (0xfffffe00074fe1d8): 54000261  b.ne 0xfffffe00074fe224
0x062a5cc (0xfffffe00074fe1dc): 52800016  movz w22, #0x0
0x062a5d0 (0xfffffe00074fe1e0): 5280000c  movz w12, #0x0
0x062a5d4 (0xfffffe00074fe1e4): 14000061  b 0xfffffe00074fe368 <_sweet_keys_init+0x414>
0x062a5d8 (0xfffffe00074fe1e8): f9437308  ldr x8, [x24, #0x6e0]
0x062a5dc (0xfffffe00074fe1ec): 2a1503e9  mov w9, w21
0x062a5e0 (0xfffffe00074fe1f0): b27d0529  .word 0xb27d0529
0x062a5e4 (0xfffffe00074fe1f4): b869690b  .word 0xb869690b
0x062a5e8 (0xfffffe00074fe1f8): d50331bf  .word 0xd50331bf
0x062a5ec (0xfffffe00074fe1fc): 52800028  movz w8, #0x1
0x062a5f0 (0xfffffe00074fe200): 52800029  movz w9, #0x1
0x062a5f4 (0xfffffe00074fe204): 14000003  b 0xfffffe00074fe210 <_sweet_keys_init+0x2bc>
0x062a5f8 (0xfffffe00074fe208): 5280000b  movz w11, #0x0
0x062a5fc (0xfffffe00074fe20c): 52800008  movz w8, #0x0
0x062a600 (0xfffffe00074fe210): 0a090108  .word 0x0a090108
0x062a604 (0xfffffe00074fe214): b81943a8  .word 0xb81943a8
0x062a608 (0xfffffe00074fe218): 794a5f48  ldrh w8, [x26, #0x52e]
0x062a60c (0xfffffe00074fe21c): 6a2802ff  .word 0x6a2802ff
0x062a610 (0xfffffe00074fe220): 54fffde0  b.eq 0xfffffe00074fe1dc
0x062a614 (0xfffffe00074fe224): 92403d09  .word 0x92403d09
0x062a618 (0xfffffe00074fe228): d379e135  .word 0xd379e135
0x062a61c (0xfffffe00074fe22c): d50332bf  .word 0xd50332bf
0x062a620 (0xfffffe00074fe230): f9437309  ldr x9, [x24, #0x6e0]
0x062a624 (0xfffffe00074fe234): b835693c  .word 0xb835693c
0x062a628 (0xfffffe00074fe238): d503339f  .word 0xd503339f
0x062a62c (0xfffffe00074fe23c): 52800116  movz w22, #0x8
0x062a630 (0xfffffe00074fe240): b3793d16  .word 0xb3793d16
0x062a634 (0xfffffe00074fe244): f9437308  ldr x8, [x24, #0x6e0]
0x062a638 (0xfffffe00074fe248): b8766908  .word 0xb8766908
0x062a63c (0xfffffe00074fe24c): d50331bf  .word 0xd50331bf
0x062a640 (0xfffffe00074fe250): b906fb68  str w8, [x27, #0x6f8]
0x062a644 (0xfffffe00074fe254): 370001a8  tbnz w8, #0, 0xfffffe00074fe288
0x062a648 (0xfffffe00074fe258): aa0b03f9  mov x25, x11
0x062a64c (0xfffffe00074fe25c): 52807d17  movz w23, #0x3e8
0x062a650 (0xfffffe00074fe260): 52800020  movz w0, #0x1
0x062a654 (0xfffffe00074fe264): 97f8d57d  bl 0xfffffe0007333858 <_delay>
0x062a658 (0xfffffe00074fe268): 710006f7  subs w23, w23, #0x1
0x062a65c (0xfffffe00074fe26c): 540002a0  b.eq 0xfffffe00074fe2c0
0x062a660 (0xfffffe00074fe270): f9437308  ldr x8, [x24, #0x6e0]
0x062a664 (0xfffffe00074fe274): b8766908  .word 0xb8766908
0x062a668 (0xfffffe00074fe278): d50331bf  .word 0xd50331bf
0x062a66c (0xfffffe00074fe27c): b906fb68  str w8, [x27, #0x6f8]
0x062a670 (0xfffffe00074fe280): 3607ff08  tbz w8, #0, 0xfffffe00074fe260
0x062a674 (0xfffffe00074fe284): aa1903eb  mov x11, x25
0x062a678 (0xfffffe00074fe288): 721f091f  tst/ands w8, ...
0x062a67c (0xfffffe00074fe28c): 540000a0  b.eq 0xfffffe00074fe2a0
0x062a680 (0xfffffe00074fe290): 5280000c  movz w12, #0x0
0x062a684 (0xfffffe00074fe294): 52800009  movz w9, #0x0
0x062a688 (0xfffffe00074fe298): 52800028  movz w8, #0x1
0x062a68c (0xfffffe00074fe29c): 1400000c  b 0xfffffe00074fe2cc <_sweet_keys_init+0x378>
0x062a690 (0xfffffe00074fe2a0): f9437308  ldr x8, [x24, #0x6e0]
0x062a694 (0xfffffe00074fe2a4): 2a1503e9  mov w9, w21
0x062a698 (0xfffffe00074fe2a8): b27d0529  .word 0xb27d0529
0x062a69c (0xfffffe00074fe2ac): b869690c  .word 0xb869690c
0x062a6a0 (0xfffffe00074fe2b0): d50331bf  .word 0xd50331bf
0x062a6a4 (0xfffffe00074fe2b4): 52800028  movz w8, #0x1
0x062a6a8 (0xfffffe00074fe2b8): 52800029  movz w9, #0x1
0x062a6ac (0xfffffe00074fe2bc): 14000004  b 0xfffffe00074fe2cc <_sweet_keys_init+0x378>
0x062a6b0 (0xfffffe00074fe2c0): 5280000c  movz w12, #0x0
0x062a6b4 (0xfffffe00074fe2c4): 52800008  movz w8, #0x0
0x062a6b8 (0xfffffe00074fe2c8): aa1903eb  mov x11, x25
0x062a6bc (0xfffffe00074fe2cc): 0a090119  .word 0x0a090119
0x062a6c0 (0xfffffe00074fe2d0): 794a5f48  ldrh w8, [x26, #0x52e]
0x062a6c4 (0xfffffe00074fe2d4): 529ffff7  movz w23, #0xffff
0x062a6c8 (0xfffffe00074fe2d8): eb17011f  cmp x8, x23
0x062a6cc (0xfffffe00074fe2dc): 54000440  b.eq 0xfffffe00074fe364
0x062a6d0 (0xfffffe00074fe2e0): d379e115  .word 0xd379e115
0x062a6d4 (0xfffffe00074fe2e4): d50332bf  .word 0xd50332bf
0x062a6d8 (0xfffffe00074fe2e8): f9437309  ldr x9, [x24, #0x6e0]
0x062a6dc (0xfffffe00074fe2ec): 110c038a  add w10, w28, #0x300
0x062a6e0 (0xfffffe00074fe2f0): b835692a  .word 0xb835692a
0x062a6e4 (0xfffffe00074fe2f4): d503339f  .word 0xd503339f
0x062a6e8 (0xfffffe00074fe2f8): 52800116  movz w22, #0x8
0x062a6ec (0xfffffe00074fe2fc): b3793d16  .word 0xb3793d16
0x062a6f0 (0xfffffe00074fe300): f9437308  ldr x8, [x24, #0x6e0]
0x062a6f4 (0xfffffe00074fe304): b8766908  .word 0xb8766908
0x062a6f8 (0xfffffe00074fe308): d50331bf  .word 0xd50331bf
0x062a6fc (0xfffffe00074fe30c): b906fb68  str w8, [x27, #0x6f8]
0x062a700 (0xfffffe00074fe310): 2931e7ac  stp w12, w25, [x29, #0x-74]
0x062a704 (0xfffffe00074fe314): 370001c8  tbnz w8, #0, 0xfffffe00074fe34c
0x062a708 (0xfffffe00074fe318): aa0b03fc  mov x28, x11
0x062a70c (0xfffffe00074fe31c): 52807d17  movz w23, #0x3e8
0x062a710 (0xfffffe00074fe320): 52800020  movz w0, #0x1
0x062a714 (0xfffffe00074fe324): 97f8d54d  bl 0xfffffe0007333858 <_delay>
0x062a718 (0xfffffe00074fe328): 710006f7  subs w23, w23, #0x1
0x062a71c (0xfffffe00074fe32c): 540003c0  b.eq 0xfffffe00074fe3a4
0x062a720 (0xfffffe00074fe330): f9437308  ldr x8, [x24, #0x6e0]
0x062a724 (0xfffffe00074fe334): b8766908  .word 0xb8766908
0x062a728 (0xfffffe00074fe338): d50331bf  .word 0xd50331bf
0x062a72c (0xfffffe00074fe33c): b906fb68  str w8, [x27, #0x6f8]
0x062a730 (0xfffffe00074fe340): 3607ff08  tbz w8, #0, 0xfffffe00074fe320
0x062a734 (0xfffffe00074fe344): aa1c03eb  mov x11, x28
0x062a738 (0xfffffe00074fe348): b858c3ac  .word 0xb858c3ac
0x062a73c (0xfffffe00074fe34c): 721f091f  tst/ands w8, ...
0x062a740 (0xfffffe00074fe350): 540001a0  b.eq 0xfffffe00074fe384
0x062a744 (0xfffffe00074fe354): 52800019  movz w25, #0x0
0x062a748 (0xfffffe00074fe358): 52800009  movz w9, #0x0
0x062a74c (0xfffffe00074fe35c): 52800028  movz w8, #0x1
0x062a750 (0xfffffe00074fe360): 14000015  b 0xfffffe00074fe3b4 <_sweet_keys_init+0x460>
0x062a754 (0xfffffe00074fe364): aa1903f6  mov x22, x25
0x062a758 (0xfffffe00074fe368): 52800015  movz w21, #0x0
0x062a75c (0xfffffe00074fe36c): 5280001a  movz w26, #0x0
0x062a760 (0xfffffe00074fe370): 52800019  movz w25, #0x0
0x062a764 (0xfffffe00074fe374): 5280001c  movz w28, #0x0
0x062a768 (0xfffffe00074fe378): 52800018  movz w24, #0x0
0x062a76c (0xfffffe00074fe37c): 5280001b  movz w27, #0x0
0x062a770 (0xfffffe00074fe380): 14000082  b 0xfffffe00074fe588 <_sweet_keys_init+0x634>
0x062a774 (0xfffffe00074fe384): f9437308  ldr x8, [x24, #0x6e0]
0x062a778 (0xfffffe00074fe388): 2a1503e9  mov w9, w21
0x062a77c (0xfffffe00074fe38c): b27d0529  .word 0xb27d0529
0x062a780 (0xfffffe00074fe390): b8696919  .word 0xb8696919
0x062a784 (0xfffffe00074fe394): d50331bf  .word 0xd50331bf
0x062a788 (0xfffffe00074fe398): 52800028  movz w8, #0x1
0x062a78c (0xfffffe00074fe39c): 52800029  movz w9, #0x1
0x062a790 (0xfffffe00074fe3a0): 14000005  b 0xfffffe00074fe3b4 <_sweet_keys_init+0x460>
0x062a794 (0xfffffe00074fe3a4): 52800019  movz w25, #0x0
0x062a798 (0xfffffe00074fe3a8): 52800008  movz w8, #0x0
0x062a79c (0xfffffe00074fe3ac): aa1c03eb  mov x11, x28
0x062a7a0 (0xfffffe00074fe3b0): b858c3ac  .word 0xb858c3ac
0x062a7a4 (0xfffffe00074fe3b4): 0a09011c  .word 0x0a09011c
0x062a7a8 (0xfffffe00074fe3b8): 794a5f48  ldrh w8, [x26, #0x52e]
0x062a7ac (0xfffffe00074fe3bc): 529ffff7  movz w23, #0xffff
0x062a7b0 (0xfffffe00074fe3c0): eb17011f  cmp x8, x23
0x062a7b4 (0xfffffe00074fe3c4): 54000460  b.eq 0xfffffe00074fe450
0x062a7b8 (0xfffffe00074fe3c8): d379e115  .word 0xd379e115
0x062a7bc (0xfffffe00074fe3cc): d50332bf  .word 0xd50332bf
0x062a7c0 (0xfffffe00074fe3d0): f9437309  ldr x9, [x24, #0x6e0]
0x062a7c4 (0xfffffe00074fe3d4): 5280200a  movz w10, #0x100
0x062a7c8 (0xfffffe00074fe3d8): 72a1000a  movk w10, #0x800, lsl #16
0x062a7cc (0xfffffe00074fe3dc): 110d814a  add w10, w10, #0x360
0x062a7d0 (0xfffffe00074fe3e0): b835692a  .word 0xb835692a
0x062a7d4 (0xfffffe00074fe3e4): d503339f  .word 0xd503339f
0x062a7d8 (0xfffffe00074fe3e8): 52800117  movz w23, #0x8
0x062a7dc (0xfffffe00074fe3ec): b3793d17  .word 0xb3793d17
0x062a7e0 (0xfffffe00074fe3f0): f9437308  ldr x8, [x24, #0x6e0]
0x062a7e4 (0xfffffe00074fe3f4): b8776908  .word 0xb8776908
0x062a7e8 (0xfffffe00074fe3f8): d50331bf  .word 0xd50331bf
0x062a7ec (0xfffffe00074fe3fc): b906fb68  str w8, [x27, #0x6f8]
0x062a7f0 (0xfffffe00074fe400): 370001c8  tbnz w8, #0, 0xfffffe00074fe438
0x062a7f4 (0xfffffe00074fe404): aa0b03f6  mov x22, x11
0x062a7f8 (0xfffffe00074fe408): 52807d1a  movz w26, #0x3e8
0x062a7fc (0xfffffe00074fe40c): 52800020  movz w0, #0x1
0x062a800 (0xfffffe00074fe410): 97f8d512  bl 0xfffffe0007333858 <_delay>
0x062a804 (0xfffffe00074fe414): 7100075a  subs w26, w26, #0x1
0x062a808 (0xfffffe00074fe418): 54000320  b.eq 0xfffffe00074fe47c
0x062a80c (0xfffffe00074fe41c): f9437308  ldr x8, [x24, #0x6e0]
0x062a810 (0xfffffe00074fe420): b8776908  .word 0xb8776908
0x062a814 (0xfffffe00074fe424): d50331bf  .word 0xd50331bf
0x062a818 (0xfffffe00074fe428): b906fb68  str w8, [x27, #0x6f8]
0x062a81c (0xfffffe00074fe42c): 3607ff08  tbz w8, #0, 0xfffffe00074fe40c
0x062a820 (0xfffffe00074fe430): aa1603eb  mov x11, x22
0x062a824 (0xfffffe00074fe434): b858c3ac  .word 0xb858c3ac
0x062a828 (0xfffffe00074fe438): 721f091f  tst/ands w8, ...
0x062a82c (0xfffffe00074fe43c): 54000100  b.eq 0xfffffe00074fe45c
0x062a830 (0xfffffe00074fe440): 5280001a  movz w26, #0x0
0x062a834 (0xfffffe00074fe444): 52800009  movz w9, #0x0
0x062a838 (0xfffffe00074fe448): 52800028  movz w8, #0x1
0x062a83c (0xfffffe00074fe44c): 1400000f  b 0xfffffe00074fe488 <_sweet_keys_init+0x534>
0x062a840 (0xfffffe00074fe450): 52800015  movz w21, #0x0
0x062a844 (0xfffffe00074fe454): 5280001a  movz w26, #0x0
0x062a848 (0xfffffe00074fe458): 14000037  b 0xfffffe00074fe534 <_sweet_keys_init+0x5e0>
0x062a84c (0xfffffe00074fe45c): f9437308  ldr x8, [x24, #0x6e0]
0x062a850 (0xfffffe00074fe460): 2a1503e9  mov w9, w21
0x062a854 (0xfffffe00074fe464): b27d0529  .word 0xb27d0529
0x062a858 (0xfffffe00074fe468): b869691a  .word 0xb869691a
0x062a85c (0xfffffe00074fe46c): d50331bf  .word 0xd50331bf
0x062a860 (0xfffffe00074fe470): 52800028  movz w8, #0x1
0x062a864 (0xfffffe00074fe474): 52800029  movz w9, #0x1
0x062a868 (0xfffffe00074fe478): 14000004  b 0xfffffe00074fe488 <_sweet_keys_init+0x534>
0x062a86c (0xfffffe00074fe47c): 52800008  movz w8, #0x0
0x062a870 (0xfffffe00074fe480): aa1603eb  mov x11, x22
0x062a874 (0xfffffe00074fe484): b858c3ac  .word 0xb858c3ac
0x062a878 (0xfffffe00074fe488): 0a090115  .word 0x0a090115
0x062a87c (0xfffffe00074fe48c): f0003508  adrp x8, 0xfffffe0007ba1000
0x062a880 (0xfffffe00074fe490): 794a5d08  ldrh w8, [x8, #0x52e]
0x062a884 (0xfffffe00074fe494): 529ffff7  movz w23, #0xffff
0x062a888 (0xfffffe00074fe498): eb17011f  cmp x8, x23
0x062a88c (0xfffffe00074fe49c): 540004c0  b.eq 0xfffffe00074fe534
0x062a890 (0xfffffe00074fe4a0): d379e10d  .word 0xd379e10d
0x062a894 (0xfffffe00074fe4a4): d50332bf  .word 0xd50332bf
0x062a898 (0xfffffe00074fe4a8): f9437309  ldr x9, [x24, #0x6e0]
0x062a89c (0xfffffe00074fe4ac): 5280200a  movz w10, #0x100
0x062a8a0 (0xfffffe00074fe4b0): 72a1000a  movk w10, #0x800, lsl #16
0x062a8a4 (0xfffffe00074fe4b4): 5102c14a  sub w10, w10, #0xb0
0x062a8a8 (0xfffffe00074fe4b8): b82d692a  .word 0xb82d692a
0x062a8ac (0xfffffe00074fe4bc): d503339f  .word 0xd503339f
0x062a8b0 (0xfffffe00074fe4c0): 52800117  movz w23, #0x8
0x062a8b4 (0xfffffe00074fe4c4): b3793d17  .word 0xb3793d17
0x062a8b8 (0xfffffe00074fe4c8): f9437308  ldr x8, [x24, #0x6e0]
0x062a8bc (0xfffffe00074fe4cc): b8776908  .word 0xb8776908
0x062a8c0 (0xfffffe00074fe4d0): d50331bf  .word 0xd50331bf
0x062a8c4 (0xfffffe00074fe4d4): b906fb68  str w8, [x27, #0x6f8]
0x062a8c8 (0xfffffe00074fe4d8): 37000228  tbnz w8, #0, 0xfffffe00074fe51c
0x062a8cc (0xfffffe00074fe4dc): f9003bed  str x13, [sp, #0x70]
0x062a8d0 (0xfffffe00074fe4e0): aa0b03f6  mov x22, x11
0x062a8d4 (0xfffffe00074fe4e4): 52807d14  movz w20, #0x3e8
0x062a8d8 (0xfffffe00074fe4e8): 52800020  movz w0, #0x1
0x062a8dc (0xfffffe00074fe4ec): 97f8d4db  bl 0xfffffe0007333858 <_delay>
0x062a8e0 (0xfffffe00074fe4f0): 71000694  subs w20, w20, #0x1
0x062a8e4 (0xfffffe00074fe4f4): 54000380  b.eq 0xfffffe00074fe564
0x062a8e8 (0xfffffe00074fe4f8): f9437308  ldr x8, [x24, #0x6e0]
0x062a8ec (0xfffffe00074fe4fc): b8776908  .word 0xb8776908
0x062a8f0 (0xfffffe00074fe500): d50331bf  .word 0xd50331bf
0x062a8f4 (0xfffffe00074fe504): b906fb68  str w8, [x27, #0x6f8]
0x062a8f8 (0xfffffe00074fe508): 3607ff08  tbz w8, #0, 0xfffffe00074fe4e8
0x062a8fc (0xfffffe00074fe50c): d0005c54  adrp x20, 0xfffffe0008088000
0x062a900 (0xfffffe00074fe510): aa1603eb  mov x11, x22
0x062a904 (0xfffffe00074fe514): b858c3ac  .word 0xb858c3ac
0x062a908 (0xfffffe00074fe518): f9403bed  ldr x13, [sp, #0x70]
0x062a90c (0xfffffe00074fe51c): 721f091f  tst/ands w8, ...
0x062a910 (0xfffffe00074fe520): 54000100  b.eq 0xfffffe00074fe540
0x062a914 (0xfffffe00074fe524): 52800018  movz w24, #0x0
0x062a918 (0xfffffe00074fe528): 52800009  movz w9, #0x0
0x062a91c (0xfffffe00074fe52c): 52800028  movz w8, #0x1
0x062a920 (0xfffffe00074fe530): 14000012  b 0xfffffe00074fe578 <_sweet_keys_init+0x624>
0x062a924 (0xfffffe00074fe534): 52800018  movz w24, #0x0
0x062a928 (0xfffffe00074fe538): 5280001b  movz w27, #0x0
0x062a92c (0xfffffe00074fe53c): 14000012  b 0xfffffe00074fe584 <_sweet_keys_init+0x630>
0x062a930 (0xfffffe00074fe540): f9437308  ldr x8, [x24, #0x6e0]
0x062a934 (0xfffffe00074fe544): 2a0d03e9  mov w9, w13
0x062a938 (0xfffffe00074fe548): b27d0529  .word 0xb27d0529
0x062a93c (0xfffffe00074fe54c): b8696908  .word 0xb8696908
0x062a940 (0xfffffe00074fe550): d50331bf  .word 0xd50331bf
0x062a944 (0xfffffe00074fe554): 12001d18  .word 0x12001d18
0x062a948 (0xfffffe00074fe558): 52800028  movz w8, #0x1
0x062a94c (0xfffffe00074fe55c): 52800029  movz w9, #0x1
0x062a950 (0xfffffe00074fe560): 14000006  b 0xfffffe00074fe578 <_sweet_keys_init+0x624>
0x062a954 (0xfffffe00074fe564): 52800018  movz w24, #0x0
0x062a958 (0xfffffe00074fe568): 52800008  movz w8, #0x0
0x062a95c (0xfffffe00074fe56c): d0005c54  adrp x20, 0xfffffe0008088000
0x062a960 (0xfffffe00074fe570): aa1603eb  mov x11, x22
0x062a964 (0xfffffe00074fe574): b858c3ac  .word 0xb858c3ac
0x062a968 (0xfffffe00074fe578): 0a09011b  .word 0x0a09011b
0x062a96c (0xfffffe00074fe57c): f0003508  adrp x8, 0xfffffe0007ba1000
0x062a970 (0xfffffe00074fe580): 794a5d17  ldrh w23, [x8, #0x52e]
0x062a974 (0xfffffe00074fe584): b85903b6  .word 0xb85903b6
0x062a978 (0xfffffe00074fe588): f0003508  adrp x8, 0xfffffe0007ba1000
0x062a97c (0xfffffe00074fe58c): 794a5908  ldrh w8, [x8, #0x52c]
0x062a980 (0xfffffe00074fe590): 12001d69  .word 0x12001d69
0x062a984 (0xfffffe00074fe594): 12001d8a  .word 0x12001d8a
0x062a988 (0xfffffe00074fe598): b946ea8b  ldr w11, [x20, #0x6e8]
0x062a98c (0xfffffe00074fe59c): 2a1b03ec  mov w12, w27
0x062a990 (0xfffffe00074fe5a0): a90633f8  stp x24, x12, [sp, #0x60]
0x062a994 (0xfffffe00074fe5a4): 2a1503ec  mov w12, w21
0x062a998 (0xfffffe00074fe5a8): 92401f4d  .word 0x92401f4d
0x062a99c (0xfffffe00074fe5ac): a90533ed  stp x13, x12, [sp, #0x50]
0x062a9a0 (0xfffffe00074fe5b0): 2a1c03ec  mov w12, w28
0x062a9a4 (0xfffffe00074fe5b4): 92401f2d  .word 0x92401f2d
0x062a9a8 (0xfffffe00074fe5b8): a90433ed  stp x13, x12, [sp, #0x40]
0x062a9ac (0xfffffe00074fe5bc): 2a1603ec  mov w12, w22
0x062a9b0 (0xfffffe00074fe5c0): a90333ea  stp x10, x12, [sp, #0x30]
0x062a9b4 (0xfffffe00074fe5c4): b85943b4  .word 0xb85943b4
0x062a9b8 (0xfffffe00074fe5c8): 2a1403ea  mov w10, w20
0x062a9bc (0xfffffe00074fe5cc): a9022be9  stp x9, x10, [sp, #0x20]
0x062a9c0 (0xfffffe00074fe5d0): a9015fe8  stp x8, x23, [sp, #0x10]
0x062a9c4 (0xfffffe00074fe5d4): 90ffdcc0  adrp x0, 0xfffffe0007096000
0x062a9c8 (0xfffffe00074fe5d8): 91364000  add x0, x0, #0xd90
0x062a9cc (0xfffffe00074fe5dc): a9004feb  stp x11, x19, [sp, #0x0]
0x062a9d0 (0xfffffe00074fe5e0): 97f97d29  bl 0xfffffe000735da84 <_printf>
0x062a9d4 (0xfffffe00074fe5e4): 121e1708  .word 0x121e1708
0x062a9d8 (0xfffffe00074fe5e8): 12000329  .word 0x12000329
0x062a9dc (0xfffffe00074fe5ec): 53047f2a  .word 0x53047f2a
0x062a9e0 (0xfffffe00074fe5f0): 7100411f  cmp w8, #0x10
0x062a9e4 (0xfffffe00074fe5f4): 1a8a0128  .word 0x1a8a0128
0x062a9e8 (0xfffffe00074fe5f8): 340000fb  cbz w27, 0xfffffe00074fe614
0x062a9ec (0xfffffe00074fe5fc): 340000d5  cbz w21, 0xfffffe00074fe614
0x062a9f0 (0xfffffe00074fe600): 340000bc  cbz w28, 0xfffffe00074fe614
0x062a9f4 (0xfffffe00074fe604): 3638009a  tbz w26, #7, 0xfffffe00074fe614
0x062a9f8 (0xfffffe00074fe608): 528000a9  movz w9, #0x5
0x062a9fc (0xfffffe00074fe60c): 0a090108  .word 0x0a090108
0x062aa00 (0xfffffe00074fe610): 340000e8  cbz w8, 0xfffffe00074fe62c
0x062aa04 (0xfffffe00074fe614): 90ffdcc0  adrp x0, 0xfffffe0007096000
0x062aa08 (0xfffffe00074fe618): 91381000  add x0, x0, #0xe04
0x062aa0c (0xfffffe00074fe61c): 97f97d1a  bl 0xfffffe000735da84 <_printf>
0x062aa10 (0xfffffe00074fe620): 529fffe8  movz w8, #0xffff
0x062aa14 (0xfffffe00074fe624): f0003509  adrp x9, 0xfffffe0007ba1000
0x062aa18 (0xfffffe00074fe628): 790a5d28  strh w8, [x9, #0x52e]
0x062aa1c (0xfffffe00074fe62c): 90ffdcc0  adrp x0, 0xfffffe0007096000
0x062aa20 (0xfffffe00074fe630): 91399000  add x0, x0, #0xe64
0x062aa24 (0xfffffe00074fe634): f0003513  adrp x19, 0xfffffe0007ba1000
0x062aa28 (0xfffffe00074fe638): 9114c273  add x19, x19, #0x530
0x062aa2c (0xfffffe00074fe63c): aa1303e1  mov x1, x19
0x062aa30 (0xfffffe00074fe640): 52800082  movz w2, #0x4
0x062aa34 (0xfffffe00074fe644): 9416ad8c  bl 0xfffffe0007aa9c74 <_PE_parse_boot_argn>
0x062aa38 (0xfffffe00074fe648): 90ffdcc0  adrp x0, 0xfffffe0007096000
0x062aa3c (0xfffffe00074fe64c): 9139c400  add x0, x0, #0xe71
0x062aa40 (0xfffffe00074fe650): f0003501  adrp x1, 0xfffffe0007ba1000
0x062aa44 (0xfffffe00074fe654): 9114d021  add x1, x1, #0x534
0x062aa48 (0xfffffe00074fe658): 52800082  movz w2, #0x4
0x062aa4c (0xfffffe00074fe65c): 9416ad86  bl 0xfffffe0007aa9c74 <_PE_parse_boot_argn>
0x062aa50 (0xfffffe00074fe660): 90ffdcc0  adrp x0, 0xfffffe0007096000
0x062aa54 (0xfffffe00074fe664): 913a0c00  add x0, x0, #0xe83
0x062aa58 (0xfffffe00074fe668): f0003501  adrp x1, 0xfffffe0007ba1000
0x062aa5c (0xfffffe00074fe66c): 9114e021  add x1, x1, #0x538
0x062aa60 (0xfffffe00074fe670): 52800082  movz w2, #0x4
0x062aa64 (0xfffffe00074fe674): 9416ad80  bl 0xfffffe0007aa9c74 <_PE_parse_boot_argn>
0x062aa68 (0xfffffe00074fe678): b9400268  ldr w8, [x19, #0x0]
0x062aa6c (0xfffffe00074fe67c): d0005c53  adrp x19, 0xfffffe0008088000
0x062aa70 (0xfffffe00074fe680): 34000788  cbz w8, 0xfffffe00074fe770
0x062aa74 (0xfffffe00074fe684): 52920000  movz w0, #0x9000
0x062aa78 (0xfffffe00074fe688): 72a07aa0  movk w0, #0x3d5, lsl #16
0x062aa7c (0xfffffe00074fe68c): 52820001  movz w1, #0x1000
0x062aa80 (0xfffffe00074fe690): 97fe9b1c  bl 0xfffffe00074a5300 <_ml_io_map>
0x062aa84 (0xfffffe00074fe694): f9037a60  str x0, [x19, #0x6f0]
0x062aa88 (0xfffffe00074fe698): b40003e0  cbz x0, 0xfffffe00074fe714
0x062aa8c (0xfffffe00074fe69c): b9400008  ldr w8, [x0, #0x0]
0x062aa90 (0xfffffe00074fe6a0): d50331bf  .word 0xd50331bf
0x062aa94 (0xfffffe00074fe6a4): 128047e9  movn w9, #0x23f
0x062aa98 (0xfffffe00074fe6a8): 0a090108  .word 0x0a090108
0x062aa9c (0xfffffe00074fe6ac): 32000508  .word 0x32000508
0x062aaa0 (0xfffffe00074fe6b0): d50332bf  .word 0xd50332bf
0x062aaa4 (0xfffffe00074fe6b4): f9437a69  ldr x9, [x19, #0x6f0]
0x062aaa8 (0xfffffe00074fe6b8): b9000128  str w8, [x9, #0x0]
0x062aaac (0xfffffe00074fe6bc): d503339f  .word 0xd503339f
0x062aab0 (0xfffffe00074fe6c0): 52800c80  movz w0, #0x64
0x062aab4 (0xfffffe00074fe6c4): 97f8d465  bl 0xfffffe0007333858 <_delay>
0x062aab8 (0xfffffe00074fe6c8): f9437a68  ldr x8, [x19, #0x6f0]
0x062aabc (0xfffffe00074fe6cc): b9400108  ldr w8, [x8, #0x0]
0x062aac0 (0xfffffe00074fe6d0): d50331bf  .word 0xd50331bf
0x062aac4 (0xfffffe00074fe6d4): f9437a69  ldr x9, [x19, #0x6f0]
0x062aac8 (0xfffffe00074fe6d8): b9400529  ldr w9, [x9, #0x4]
0x062aacc (0xfffffe00074fe6dc): d50331bf  .word 0xd50331bf
0x062aad0 (0xfffffe00074fe6e0): 12000129  .word 0x12000129
0x062aad4 (0xfffffe00074fe6e4): f000350a  adrp x10, 0xfffffe0007ba1000
0x062aad8 (0xfffffe00074fe6e8): b945314a  ldr w10, [x10, #0x530]
0x062aadc (0xfffffe00074fe6ec): f000350b  adrp x11, 0xfffffe0007ba1000
0x062aae0 (0xfffffe00074fe6f0): b945356b  ldr w11, [x11, #0x534]
0x062aae4 (0xfffffe00074fe6f4): f000350c  adrp x12, 0xfffffe0007ba1000
0x062aae8 (0xfffffe00074fe6f8): b945398c  ldr w12, [x12, #0x538]
0x062aaec (0xfffffe00074fe6fc): a901b3eb  stp x11, x12, [sp, #0x18]
0x062aaf0 (0xfffffe00074fe700): a900abe9  stp x9, x10, [sp, #0x8]
0x062aaf4 (0xfffffe00074fe704): f90003e8  str x8, [sp, #0x0]
0x062aaf8 (0xfffffe00074fe708): 90ffdcc0  adrp x0, 0xfffffe0007096000
0x062aafc (0xfffffe00074fe70c): 913a5800  add x0, x0, #0xe96
0x062ab00 (0xfffffe00074fe710): 97f97cdd  bl 0xfffffe000735da84 <_printf>
0x062ab04 (0xfffffe00074fe714): 2a160288  .word 0x2a160288
0x062ab08 (0xfffffe00074fe718): 37000088  tbnz w8, #0, 0xfffffe00074fe728
0x062ab0c (0xfffffe00074fe71c): 90ffdcc0  adrp x0, 0xfffffe0007096000
0x062ab10 (0xfffffe00074fe720): 913b7c00  add x0, x0, #0xedf
0x062ab14 (0xfffffe00074fe724): 97f97cd8  bl 0xfffffe000735da84 <_printf>
0x062ab18 (0xfffffe00074fe728): 10000300  adr x0, 0xfffffe00074fe788
0x062ab1c (0xfffffe00074fe72c): d503201f  nop
0x062ab20 (0xfffffe00074fe730): d101a3a2  sub x2, x29, #0x68
0x062ab24 (0xfffffe00074fe734): d2800001  movz x1, #0x0
0x062ab28 (0xfffffe00074fe738): 97fa4194  bl 0xfffffe000738ed88 <_kernel_thread_start>
0x062ab2c (0xfffffe00074fe73c): 34000200  cbz w0, 0xfffffe00074fe77c
0x062ab30 (0xfffffe00074fe740): f90003e0  str x0, [sp, #0x0]
0x062ab34 (0xfffffe00074fe744): 90ffdcc0  adrp x0, 0xfffffe0007096000
0x062ab38 (0xfffffe00074fe748): 913c7000  add x0, x0, #0xf1c
0x062ab3c (0xfffffe00074fe74c): 97f97cce  bl 0xfffffe000735da84 <_printf>
0x062ab40 (0xfffffe00074fe750): a94f7bfd  ldp x29, x30, [sp, #0xf0]
0x062ab44 (0xfffffe00074fe754): a94e4ff4  ldp x20, x19, [sp, #0xe0]
0x062ab48 (0xfffffe00074fe758): a94d57f6  ldp x22, x21, [sp, #0xd0]
0x062ab4c (0xfffffe00074fe75c): a94c5ff8  ldp x24, x23, [sp, #0xc0]
0x062ab50 (0xfffffe00074fe760): a94b67fa  ldp x26, x25, [sp, #0xb0]
0x062ab54 (0xfffffe00074fe764): a94a6ffc  ldp x28, x27, [sp, #0xa0]
0x062ab58 (0xfffffe00074fe768): 910403ff  add sp, sp, #0x100
0x062ab5c (0xfffffe00074fe76c): d65f03c0  ret
0x062ab60 (0xfffffe00074fe770): f9437a60  ldr x0, [x19, #0x6f0]
0x062ab64 (0xfffffe00074fe774): b5fff940  cbnz x0, 0xfffffe00074fe69c
0x062ab68 (0xfffffe00074fe778): 17ffffe7  b 0xfffffe00074fe714 <_sweet_keys_init+0x7c0>
0x062ab6c (0xfffffe00074fe77c): f85983a0  .word 0xf85983a0
0x062ab70 (0xfffffe00074fe780): 97fa3a58  bl 0xfffffe000738d0e0 <_thread_deallocate>
0x062ab74 (0xfffffe00074fe784): 17fffff3  b 0xfffffe00074fe750 <_sweet_keys_init+0x7fc>
```

### `_sweet_usb_probe` (`0x062e690`, VA `0xfffffe00075022a0`, size `0xbd4`)
```asm
0x062e690 (0xfffffe00075022a0): a9ba6ffc  stp x28, x27, [sp, #0x-60]
0x062e694 (0xfffffe00075022a4): a90167fa  stp x26, x25, [sp, #0x10]
0x062e698 (0xfffffe00075022a8): a9025ff8  stp x24, x23, [sp, #0x20]
0x062e69c (0xfffffe00075022ac): a90357f6  stp x22, x21, [sp, #0x30]
0x062e6a0 (0xfffffe00075022b0): a9044ff4  stp x20, x19, [sp, #0x40]
0x062e6a4 (0xfffffe00075022b4): a9057bfd  stp x29, x30, [sp, #0x50]
0x062e6a8 (0xfffffe00075022b8): 910143fd  add x29, sp, #0x50
0x062e6ac (0xfffffe00075022bc): d107c3ff  sub sp, sp, #0x1f0
0x062e6b0 (0xfffffe00075022c0): 90003a88  adrp x8, 0xfffffe0007c52000
0x062e6b4 (0xfffffe00075022c4): d503201f  nop
0x062e6b8 (0xfffffe00075022c8): f945b108  ldr x8, [x8, #0xb60]
0x062e6bc (0xfffffe00075022cc): f81a83a8  .word 0xf81a83a8
0x062e6c0 (0xfffffe00075022d0): 52800028  movz w8, #0x1
0x062e6c4 (0xfffffe00075022d4): b90037e8  str w8, [sp, #0x34]
0x062e6c8 (0xfffffe00075022d8): b0ffdca0  adrp x0, 0xfffffe0007097000
0x062e6cc (0xfffffe00075022dc): 912f1800  add x0, x0, #0xbc6
0x062e6d0 (0xfffffe00075022e0): 9100d3e1  add x1, sp, #0x34
0x062e6d4 (0xfffffe00075022e4): 52800082  movz w2, #0x4
0x062e6d8 (0xfffffe00075022e8): 94169e63  bl 0xfffffe0007aa9c74 <_PE_parse_boot_argn>
0x062e6dc (0xfffffe00075022ec): b94037e8  ldr w8, [sp, #0x34]
0x062e6e0 (0xfffffe00075022f0): 340028a8  cbz w8, 0xfffffe0007502804
0x062e6e4 (0xfffffe00075022f4): f90027ff  str x31, [sp, #0x48]
0x062e6e8 (0xfffffe00075022f8): 10005be0  adr x0, 0xfffffe0007502e74
0x062e6ec (0xfffffe00075022fc): d503201f  nop
0x062e6f0 (0xfffffe0007502300): 910123e2  add x2, sp, #0x48
0x062e6f4 (0xfffffe0007502304): d2800001  movz x1, #0x0
0x062e6f8 (0xfffffe0007502308): 97fa32a0  bl 0xfffffe000738ed88 <_kernel_thread_start>
0x062e6fc (0xfffffe000750230c): 35000060  cbnz w0, 0xfffffe0007502318
0x062e700 (0xfffffe0007502310): f94027e0  ldr x0, [sp, #0x48]
0x062e704 (0xfffffe0007502314): 97fa2b73  bl 0xfffffe000738d0e0 <_thread_deallocate>
0x062e708 (0xfffffe0007502318): 52a00200  movz w0, #0x10, lsl #16
0x062e70c (0xfffffe000750231c): 52a00121  movz w1, #0x9, lsl #16
0x062e710 (0xfffffe0007502320): 97fe8bf8  bl 0xfffffe00074a5300 <_ml_io_map>
0x062e714 (0xfffffe0007502324): b4000480  cbz x0, 0xfffffe00075023b4
0x062e718 (0xfffffe0007502328): aa0003f3  mov x19, x0
0x062e71c (0xfffffe000750232c): 529e0088  movz w8, #0xf004
0x062e720 (0xfffffe0007502330): b8686818  .word 0xb8686818
0x062e724 (0xfffffe0007502334): d50331bf  .word 0xd50331bf
0x062e728 (0xfffffe0007502338): b0ffdcb6  adrp x22, 0xfffffe0007097000
0x062e72c (0xfffffe000750233c): 913086d6  add x22, x22, #0xc21
0x062e730 (0xfffffe0007502340): 90ffdb37  adrp x23, 0xfffffe0007066000
0x062e734 (0xfffffe0007502344): 910302f7  add x23, x23, #0xc0
0x062e738 (0xfffffe0007502348): 7100031f  cmp w24, #0x0
0x062e73c (0xfffffe000750234c): 9a96a2e8  .word 0x9a96a2e8
0x062e740 (0xfffffe0007502350): a90023f8  stp x24, x8, [sp, #0x0]
0x062e744 (0xfffffe0007502354): b0ffdca0  adrp x0, 0xfffffe0007097000
0x062e748 (0xfffffe0007502358): 912fe400  add x0, x0, #0xbf9
0x062e74c (0xfffffe000750235c): 97f96dca  bl 0xfffffe000735da84 <_printf>
0x062e750 (0xfffffe0007502360): b94037e8  ldr w8, [sp, #0x34]
0x062e754 (0xfffffe0007502364): 37f80598  tbnz w24, #31, 0xfffffe0007502414
0x062e758 (0xfffffe0007502368): 7100091f  cmp w8, #0x2
0x062e75c (0xfffffe000750236c): 5400054b  b.lt 0xfffffe0007502414
0x062e760 (0xfffffe0007502370): 121f7b08  .word 0x121f7b08
0x062e764 (0xfffffe0007502374): d50332bf  .word 0xd50332bf
0x062e768 (0xfffffe0007502378): 529e0094  movz w20, #0xf004
0x062e76c (0xfffffe000750237c): b8346a68  .word 0xb8346a68
0x062e770 (0xfffffe0007502380): d503339f  .word 0xd503339f
0x062e774 (0xfffffe0007502384): 12800135  movn w21, #0x9
0x062e778 (0xfffffe0007502388): 5289c2d8  movz w24, #0x4e16
0x062e77c (0xfffffe000750238c): b8746a68  .word 0xb8746a68
0x062e780 (0xfffffe0007502390): d50331bf  .word 0xd50331bf
0x062e784 (0xfffffe0007502394): 37f801e8  tbnz w8, #31, 0xfffffe00075023d0
0x062e788 (0xfffffe0007502398): 52800140  movz w0, #0xa
0x062e78c (0xfffffe000750239c): 97f8c52f  bl 0xfffffe0007333858 <_delay>
0x062e790 (0xfffffe00075023a0): 11002ab5  add w21, w21, #0xa
0x062e794 (0xfffffe00075023a4): 6b1802bf  cmp w21, w24
0x062e798 (0xfffffe00075023a8): 54ffff23  b.cc 0xfffffe000750238c
0x062e79c (0xfffffe00075023ac): 5289c408  movz w8, #0x4e20
0x062e7a0 (0xfffffe00075023b0): 14000009  b 0xfffffe00075023d4 <_sweet_usb_probe+0x134>
0x062e7a4 (0xfffffe00075023b4): b0ffdca8  adrp x8, 0xfffffe0007097000
0x062e7a8 (0xfffffe00075023b8): 912f3d08  add x8, x8, #0xbcf
0x062e7ac (0xfffffe00075023bc): f00034e9  adrp x9, 0xfffffe0007ba1000
0x062e7b0 (0xfffffe00075023c0): f902a128  str x8, [x9, #0x540]
0x062e7b4 (0xfffffe00075023c4): b0ffdca0  adrp x0, 0xfffffe0007097000
0x062e7b8 (0xfffffe00075023c8): 912f7800  add x0, x0, #0xbde
0x062e7bc (0xfffffe00075023cc): 1400010d  b 0xfffffe0007502800 <_sweet_usb_probe+0x560>
0x062e7c0 (0xfffffe00075023d0): 11002aa8  add w8, w21, #0xa
0x062e7c4 (0xfffffe00075023d4): 529e0089  movz w9, #0xf004
0x062e7c8 (0xfffffe00075023d8): b8696a78  .word 0xb8696a78
0x062e7cc (0xfffffe00075023dc): d50331bf  .word 0xd50331bf
0x062e7d0 (0xfffffe00075023e0): a90023f8  stp x24, x8, [sp, #0x0]
0x062e7d4 (0xfffffe00075023e4): b0ffdca0  adrp x0, 0xfffffe0007097000
0x062e7d8 (0xfffffe00075023e8): 91309000  add x0, x0, #0xc24
0x062e7dc (0xfffffe00075023ec): 97f96da6  bl 0xfffffe000735da84 <_printf>
0x062e7e0 (0xfffffe00075023f0): b0ffdca8  adrp x8, 0xfffffe0007097000
0x062e7e4 (0xfffffe00075023f4): 91315108  add x8, x8, #0xc54
0x062e7e8 (0xfffffe00075023f8): b0ffdca9  adrp x9, 0xfffffe0007097000
0x062e7ec (0xfffffe00075023fc): 9131ad29  add x9, x9, #0xc6b
0x062e7f0 (0xfffffe0007502400): 7100031f  cmp w24, #0x0
0x062e7f4 (0xfffffe0007502404): 9a88a128  .word 0x9a88a128
0x062e7f8 (0xfffffe0007502408): f00034e9  adrp x9, 0xfffffe0007ba1000
0x062e7fc (0xfffffe000750240c): f902a128  str x8, [x9, #0x540]
0x062e800 (0xfffffe0007502410): b94037e8  ldr w8, [sp, #0x34]
0x062e804 (0xfffffe0007502414): 36f80398  tbz w24, #31, 0xfffffe0007502484
0x062e808 (0xfffffe0007502418): 7100091f  cmp w8, #0x2
0x062e80c (0xfffffe000750241c): 5400034b  b.lt 0xfffffe0007502484
0x062e810 (0xfffffe0007502420): d2800014  movz x20, #0x0
0x062e814 (0xfffffe0007502424): b0ffe8b5  adrp x21, 0xfffffe0007217000
0x062e818 (0xfffffe0007502428): 911262b5  add x21, x21, #0x498
0x062e81c (0xfffffe000750242c): 14000004  b 0xfffffe000750243c <_sweet_usb_probe+0x19c>
0x062e820 (0xfffffe0007502430): 91000694  add x20, x20, #0x1
0x062e824 (0xfffffe0007502434): f1001e9f  cmp x20, #0x7
0x062e828 (0xfffffe0007502438): 54000260  b.eq 0xfffffe0007502484
0x062e82c (0xfffffe000750243c): 8b1412a8  .word 0x8b1412a8
0x062e830 (0xfffffe0007502440): b9400919  ldr w25, [x8, #0x8]
0x062e834 (0xfffffe0007502444): b8796a68  .word 0xb8796a68
0x062e838 (0xfffffe0007502448): d50331bf  .word 0xd50331bf
0x062e83c (0xfffffe000750244c): 36ffff28  tbz w8, #31, 0xfffffe0007502430
0x062e840 (0xfffffe0007502450): 32000108  .word 0x32000108
0x062e844 (0xfffffe0007502454): d50332bf  .word 0xd50332bf
0x062e848 (0xfffffe0007502458): b8396a68  .word 0xb8396a68
0x062e84c (0xfffffe000750245c): d503339f  .word 0xd503339f
0x062e850 (0xfffffe0007502460): 5280191a  movz w26, #0xc8
0x062e854 (0xfffffe0007502464): b8796a68  .word 0xb8796a68
0x062e858 (0xfffffe0007502468): d50331bf  .word 0xd50331bf
0x062e85c (0xfffffe000750246c): 36fffe28  tbz w8, #31, 0xfffffe0007502430
0x062e860 (0xfffffe0007502470): 52800140  movz w0, #0xa
0x062e864 (0xfffffe0007502474): 97f8c4f9  bl 0xfffffe0007333858 <_delay>
0x062e868 (0xfffffe0007502478): 7100075a  subs w26, w26, #0x1
0x062e86c (0xfffffe000750247c): 54ffff41  b.ne 0xfffffe0007502464
0x062e870 (0xfffffe0007502480): 17ffffec  b 0xfffffe0007502430 <_sweet_usb_probe+0x190>
0x062e874 (0xfffffe0007502484): 529e0188  movz w8, #0xf00c
0x062e878 (0xfffffe0007502488): b8686a79  .word 0xb8686a79
0x062e87c (0xfffffe000750248c): d50331bf  .word 0xd50331bf
0x062e880 (0xfffffe0007502490): 7100033f  cmp w25, #0x0
0x062e884 (0xfffffe0007502494): 9a97a2c8  .word 0x9a97a2c8
0x062e888 (0xfffffe0007502498): b0ffdca9  adrp x9, 0xfffffe0007097000
0x062e88c (0xfffffe000750249c): 913da929  add x9, x9, #0xf6a
0x062e890 (0xfffffe00075024a0): a900a3f9  stp x25, x8, [sp, #0x8]
0x062e894 (0xfffffe00075024a4): f90003e9  str x9, [sp, #0x0]
0x062e898 (0xfffffe00075024a8): b0ffdcb4  adrp x20, 0xfffffe0007097000
0x062e89c (0xfffffe00075024ac): 91322a94  add x20, x20, #0xc8a
0x062e8a0 (0xfffffe00075024b0): aa1403e0  mov x0, x20
0x062e8a4 (0xfffffe00075024b4): 97f96d74  bl 0xfffffe000735da84 <_printf>
0x062e8a8 (0xfffffe00075024b8): 529e0208  movz w8, #0xf010
0x062e8ac (0xfffffe00075024bc): b8686a68  .word 0xb8686a68
0x062e8b0 (0xfffffe00075024c0): d50331bf  .word 0xd50331bf
0x062e8b4 (0xfffffe00075024c4): 7100011f  cmp w8, #0x0
0x062e8b8 (0xfffffe00075024c8): 9a97a2c9  .word 0x9a97a2c9
0x062e8bc (0xfffffe00075024cc): a900a7e8  stp x8, x9, [sp, #0x8]
0x062e8c0 (0xfffffe00075024d0): b0ffdca9  adrp x9, 0xfffffe0007097000
0x062e8c4 (0xfffffe00075024d4): 913dc529  add x9, x9, #0xf71
0x062e8c8 (0xfffffe00075024d8): f90003e9  str x9, [sp, #0x0]
0x062e8cc (0xfffffe00075024dc): aa1403e0  mov x0, x20
0x062e8d0 (0xfffffe00075024e0): 97f96d69  bl 0xfffffe000735da84 <_printf>
0x062e8d4 (0xfffffe00075024e4): 529e0288  movz w8, #0xf014
0x062e8d8 (0xfffffe00075024e8): b8686a68  .word 0xb8686a68
0x062e8dc (0xfffffe00075024ec): d50331bf  .word 0xd50331bf
0x062e8e0 (0xfffffe00075024f0): 7100011f  cmp w8, #0x0
0x062e8e4 (0xfffffe00075024f4): 9a97a2c9  .word 0x9a97a2c9
0x062e8e8 (0xfffffe00075024f8): a900a7e8  stp x8, x9, [sp, #0x8]
0x062e8ec (0xfffffe00075024fc): b0ffdca9  adrp x9, 0xfffffe0007097000
0x062e8f0 (0xfffffe0007502500): 913ddd29  add x9, x9, #0xf77
0x062e8f4 (0xfffffe0007502504): f90003e9  str x9, [sp, #0x0]
0x062e8f8 (0xfffffe0007502508): aa1403e0  mov x0, x20
0x062e8fc (0xfffffe000750250c): 97f96d5e  bl 0xfffffe000735da84 <_printf>
0x062e900 (0xfffffe0007502510): 528a0588  movz w8, #0x502c
0x062e904 (0xfffffe0007502514): b8686a7a  .word 0xb8686a7a
0x062e908 (0xfffffe0007502518): d50331bf  .word 0xd50331bf
0x062e90c (0xfffffe000750251c): 7100035f  cmp w26, #0x0
0x062e910 (0xfffffe0007502520): 9a97a2c8  .word 0x9a97a2c8
0x062e914 (0xfffffe0007502524): a900a3fa  stp x26, x8, [sp, #0x8]
0x062e918 (0xfffffe0007502528): b0ffdca8  adrp x8, 0xfffffe0007097000
0x062e91c (0xfffffe000750252c): 913df108  add x8, x8, #0xf7c
0x062e920 (0xfffffe0007502530): f90003e8  str x8, [sp, #0x0]
0x062e924 (0xfffffe0007502534): aa1403e0  mov x0, x20
0x062e928 (0xfffffe0007502538): 97f96d53  bl 0xfffffe000735da84 <_printf>
0x062e92c (0xfffffe000750253c): 52840388  movz w8, #0x201c
0x062e930 (0xfffffe0007502540): 72a00108  movk w8, #0x8, lsl #16
0x062e934 (0xfffffe0007502544): b8686a68  .word 0xb8686a68
0x062e938 (0xfffffe0007502548): d50331bf  .word 0xd50331bf
0x062e93c (0xfffffe000750254c): 7100011f  cmp w8, #0x0
0x062e940 (0xfffffe0007502550): 9a97a2c9  .word 0x9a97a2c9
0x062e944 (0xfffffe0007502554): a900a7e8  stp x8, x9, [sp, #0x8]
0x062e948 (0xfffffe0007502558): b0ffdca9  adrp x9, 0xfffffe0007097000
0x062e94c (0xfffffe000750255c): 913e2129  add x9, x9, #0xf88
0x062e950 (0xfffffe0007502560): f90003e9  str x9, [sp, #0x0]
0x062e954 (0xfffffe0007502564): aa1403e0  mov x0, x20
0x062e958 (0xfffffe0007502568): 97f96d47  bl 0xfffffe000735da84 <_printf>
0x062e95c (0xfffffe000750256c): 52940088  movz w8, #0xa004
0x062e960 (0xfffffe0007502570): 72a000c8  movk w8, #0x6, lsl #16
0x062e964 (0xfffffe0007502574): b8686a75  .word 0xb8686a75
0x062e968 (0xfffffe0007502578): d50331bf  .word 0xd50331bf
0x062e96c (0xfffffe000750257c): 710002bf  cmp w21, #0x0
0x062e970 (0xfffffe0007502580): 9a97a2c8  .word 0x9a97a2c8
0x062e974 (0xfffffe0007502584): a900a3f5  stp x21, x8, [sp, #0x8]
0x062e978 (0xfffffe0007502588): b0ffdca8  adrp x8, 0xfffffe0007097000
0x062e97c (0xfffffe000750258c): 913e4908  add x8, x8, #0xf92
0x062e980 (0xfffffe0007502590): f90003e8  str x8, [sp, #0x0]
0x062e984 (0xfffffe0007502594): aa1403e0  mov x0, x20
0x062e988 (0xfffffe0007502598): 97f96d3b  bl 0xfffffe000735da84 <_printf>
0x062e98c (0xfffffe000750259c): 52980108  movz w8, #0xc008
0x062e990 (0xfffffe00075025a0): 72a00108  movk w8, #0x8, lsl #16
0x062e994 (0xfffffe00075025a4): b8686a68  .word 0xb8686a68
0x062e998 (0xfffffe00075025a8): d50331bf  .word 0xd50331bf
0x062e99c (0xfffffe00075025ac): 7100011f  cmp w8, #0x0
0x062e9a0 (0xfffffe00075025b0): 9a97a2c9  .word 0x9a97a2c9
0x062e9a4 (0xfffffe00075025b4): a900a7e8  stp x8, x9, [sp, #0x8]
0x062e9a8 (0xfffffe00075025b8): b0ffdca9  adrp x9, 0xfffffe0007097000
0x062e9ac (0xfffffe00075025bc): 913e6929  add x9, x9, #0xf9a
0x062e9b0 (0xfffffe00075025c0): f90003e9  str x9, [sp, #0x0]
0x062e9b4 (0xfffffe00075025c4): aa1403e0  mov x0, x20
0x062e9b8 (0xfffffe00075025c8): 97f96d2f  bl 0xfffffe000735da84 <_printf>
0x062e9bc (0xfffffe00075025cc): 36f80f98  tbz w24, #31, 0xfffffe00075027bc
0x062e9c0 (0xfffffe00075025d0): 2a1a0328  .word 0x2a1a0328
0x062e9c4 (0xfffffe00075025d4): 37f80f48  tbnz w8, #31, 0xfffffe00075027bc
0x062e9c8 (0xfffffe00075025d8): 52a14c00  movz w0, #0xa60, lsl #16
0x062e9cc (0xfffffe00075025dc): 529a0001  movz w1, #0xd000
0x062e9d0 (0xfffffe00075025e0): 97fe8b48  bl 0xfffffe00074a5300 <_ml_io_map>
0x062e9d4 (0xfffffe00075025e4): d0005c28  adrp x8, 0xfffffe0008088000
0x062e9d8 (0xfffffe00075025e8): f9050100  str x0, [x8, #0xa00]
0x062e9dc (0xfffffe00075025ec): b94037e8  ldr w8, [sp, #0x34]
0x062e9e0 (0xfffffe00075025f0): b0ffdca9  adrp x9, 0xfffffe0007097000
0x062e9e4 (0xfffffe00075025f4): 91351929  add x9, x9, #0xd46
0x062e9e8 (0xfffffe00075025f8): b0ffdcaa  adrp x10, 0xfffffe0007097000
0x062e9ec (0xfffffe00075025fc): 9134954a  add x10, x10, #0xd25
0x062e9f0 (0xfffffe0007502600): 7100051f  cmp w8, #0x1
0x062e9f4 (0xfffffe0007502604): 9a89c148  .word 0x9a89c148
0x062e9f8 (0xfffffe0007502608): f00034f4  adrp x20, 0xfffffe0007ba1000
0x062e9fc (0xfffffe000750260c): f902a288  str x8, [x20, #0x540]
0x062ea00 (0xfffffe0007502610): b4000ee0  cbz x0, 0xfffffe00075027ec
0x062ea04 (0xfffffe0007502614): aa0003f3  mov x19, x0
0x062ea08 (0xfffffe0007502618): 52982408  movz w8, #0xc120
0x062ea0c (0xfffffe000750261c): b8686808  .word 0xb8686808
0x062ea10 (0xfffffe0007502620): d50331bf  .word 0xd50331bf
0x062ea14 (0xfffffe0007502624): 52982209  movz w9, #0xc110
0x062ea18 (0xfffffe0007502628): b8696809  .word 0xb8696809
0x062ea1c (0xfffffe000750262c): d50331bf  .word 0xd50331bf
0x062ea20 (0xfffffe0007502630): 5298230a  movz w10, #0xc118
0x062ea24 (0xfffffe0007502634): b86a680a  .word 0xb86a680a
0x062ea28 (0xfffffe0007502638): d50331bf  .word 0xd50331bf
0x062ea2c (0xfffffe000750263c): 5298400b  movz w11, #0xc200
0x062ea30 (0xfffffe0007502640): b86b680b  .word 0xb86b680b
0x062ea34 (0xfffffe0007502644): d50331bf  .word 0xd50331bf
0x062ea38 (0xfffffe0007502648): a9012fea  stp x10, x11, [sp, #0x10]
0x062ea3c (0xfffffe000750264c): a90027e8  stp x8, x9, [sp, #0x0]
0x062ea40 (0xfffffe0007502650): b0ffdca0  adrp x0, 0xfffffe0007097000
0x062ea44 (0xfffffe0007502654): 9135ec00  add x0, x0, #0xd7b
0x062ea48 (0xfffffe0007502658): 97f96d0b  bl 0xfffffe000735da84 <_printf>
0x062ea4c (0xfffffe000750265c): 5298e008  movz w8, #0xc700
0x062ea50 (0xfffffe0007502660): b8686a68  .word 0xb8686a68
0x062ea54 (0xfffffe0007502664): d50331bf  .word 0xd50331bf
0x062ea58 (0xfffffe0007502668): 5298e089  movz w9, #0xc704
0x062ea5c (0xfffffe000750266c): b8696a69  .word 0xb8696a69
0x062ea60 (0xfffffe0007502670): d50331bf  .word 0xd50331bf
0x062ea64 (0xfffffe0007502674): 5298e10a  movz w10, #0xc708
0x062ea68 (0xfffffe0007502678): b86a6a6a  .word 0xb86a6a6a
0x062ea6c (0xfffffe000750267c): d50331bf  .word 0xd50331bf
0x062ea70 (0xfffffe0007502680): 5298e18b  movz w11, #0xc70c
0x062ea74 (0xfffffe0007502684): b86b6a6b  .word 0xb86b6a6b
0x062ea78 (0xfffffe0007502688): d50331bf  .word 0xd50331bf
0x062ea7c (0xfffffe000750268c): 5298e40c  movz w12, #0xc720
0x062ea80 (0xfffffe0007502690): b86c6a6c  .word 0xb86c6a6c
0x062ea84 (0xfffffe0007502694): d50331bf  .word 0xd50331bf
0x062ea88 (0xfffffe0007502698): a901b3eb  stp x11, x12, [sp, #0x18]
0x062ea8c (0xfffffe000750269c): a900abe9  stp x9, x10, [sp, #0x8]
0x062ea90 (0xfffffe00075026a0): f90003e8  str x8, [sp, #0x0]
0x062ea94 (0xfffffe00075026a4): b0ffdca0  adrp x0, 0xfffffe0007097000
0x062ea98 (0xfffffe00075026a8): 91371800  add x0, x0, #0xdc6
0x062ea9c (0xfffffe00075026ac): 97f96cf6  bl 0xfffffe000735da84 <_printf>
0x062eaa0 (0xfffffe00075026b0): 52988088  movz w8, #0xc404
0x062eaa4 (0xfffffe00075026b4): b8686a68  .word 0xb8686a68
0x062eaa8 (0xfffffe00075026b8): d50331bf  .word 0xd50331bf
0x062eaac (0xfffffe00075026bc): 52988009  movz w9, #0xc400
0x062eab0 (0xfffffe00075026c0): b8696a69  .word 0xb8696a69
0x062eab4 (0xfffffe00075026c4): d50331bf  .word 0xd50331bf
0x062eab8 (0xfffffe00075026c8): 5298810a  movz w10, #0xc408
0x062eabc (0xfffffe00075026cc): b86a6a6a  .word 0xb86a6a6a
0x062eac0 (0xfffffe00075026d0): d50331bf  .word 0xd50331bf
0x062eac4 (0xfffffe00075026d4): 5298818b  movz w11, #0xc40c
0x062eac8 (0xfffffe00075026d8): b86b6a6b  .word 0xb86b6a6b
0x062eacc (0xfffffe00075026dc): d50331bf  .word 0xd50331bf
0x062ead0 (0xfffffe00075026e0): 5298280c  movz w12, #0xc140
0x062ead4 (0xfffffe00075026e4): b86c6a6c  .word 0xb86c6a6c
0x062ead8 (0xfffffe00075026e8): d50331bf  .word 0xd50331bf
0x062eadc (0xfffffe00075026ec): a901b3eb  stp x11, x12, [sp, #0x18]
0x062eae0 (0xfffffe00075026f0): a900abe9  stp x9, x10, [sp, #0x8]
0x062eae4 (0xfffffe00075026f4): f90003e8  str x8, [sp, #0x0]
0x062eae8 (0xfffffe00075026f8): b0ffdca0  adrp x0, 0xfffffe0007097000
0x062eaec (0xfffffe00075026fc): 91386400  add x0, x0, #0xe19
0x062eaf0 (0xfffffe0007502700): 97f96ce1  bl 0xfffffe000735da84 <_printf>
0x062eaf4 (0xfffffe0007502704): b94037e8  ldr w8, [sp, #0x34]
0x062eaf8 (0xfffffe0007502708): 7100091f  cmp w8, #0x2
0x062eafc (0xfffffe000750270c): 540002eb  b.lt 0xfffffe0007502768
0x062eb00 (0xfffffe0007502710): d0005c36  adrp x22, 0xfffffe0008088000
0x062eb04 (0xfffffe0007502714): 912862d6  add x22, x22, #0xa18
0x062eb08 (0xfffffe0007502718): f90002d3  str x19, [x22, #0x0]
0x062eb0c (0xfffffe000750271c): 90ffe428  adrp x8, 0xfffffe0007186000
0x062eb10 (0xfffffe0007502720): d503201f  nop
0x062eb14 (0xfffffe0007502724): f9414500  ldr x0, [x8, #0x288]
0x062eb18 (0xfffffe0007502728): 52880001  movz w1, #0x4000
0x062eb1c (0xfffffe000750272c): 5287ffe2  movz w2, #0x3fff
0x062eb20 (0xfffffe0007502730): 52800003  movz w3, #0x0
0x062eb24 (0xfffffe0007502734): 52800004  movz w4, #0x0
0x062eb28 (0xfffffe0007502738): 52900805  movz w5, #0x8040
0x062eb2c (0xfffffe000750273c): 72a00205  movk w5, #0x10, lsl #16
0x062eb30 (0xfffffe0007502740): 52800066  movz w6, #0x3
0x062eb34 (0xfffffe0007502744): 97fbdcea  bl 0xfffffe00073f9aec <_kmem_alloc_contig_guard>
0x062eb38 (0xfffffe0007502748): f90006c1  str x1, [x22, #0x8]
0x062eb3c (0xfffffe000750274c): 34000780  cbz w0, 0xfffffe000750283c
0x062eb40 (0xfffffe0007502750): b0ffdca0  adrp x0, 0xfffffe0007097000
0x062eb44 (0xfffffe0007502754): 913e8400  add x0, x0, #0xfa1
0x062eb48 (0xfffffe0007502758): 97f96ccb  bl 0xfffffe000735da84 <_printf>
0x062eb4c (0xfffffe000750275c): b0ffdca8  adrp x8, 0xfffffe0007097000
0x062eb50 (0xfffffe0007502760): 913eed08  add x8, x8, #0xfbb
0x062eb54 (0xfffffe0007502764): f902a288  str x8, [x20, #0x540]
0x062eb58 (0xfffffe0007502768): 37f80495  tbnz w21, #31, 0xfffffe00075027f8
0x062eb5c (0xfffffe000750276c): 52840000  movz w0, #0x2000
0x062eb60 (0xfffffe0007502770): 72a111c0  movk w0, #0x88e, lsl #16
0x062eb64 (0xfffffe0007502774): 52808001  movz w1, #0x400
0x062eb68 (0xfffffe0007502778): 97fe8ae2  bl 0xfffffe00074a5300 <_ml_io_map>
0x062eb6c (0xfffffe000750277c): b4000440  cbz x0, 0xfffffe0007502804
0x062eb70 (0xfffffe0007502780): d0005c28  adrp x8, 0xfffffe0008088000
0x062eb74 (0xfffffe0007502784): f9050500  str x0, [x8, #0xa08]
0x062eb78 (0xfffffe0007502788): b941a008  ldr w8, [x0, #0x1a0]
0x062eb7c (0xfffffe000750278c): d50331bf  .word 0xd50331bf
0x062eb80 (0xfffffe0007502790): b9421009  ldr w9, [x0, #0x210]
0x062eb84 (0xfffffe0007502794): d50331bf  .word 0xd50331bf
0x062eb88 (0xfffffe0007502798): b942400a  ldr w10, [x0, #0x240]
0x062eb8c (0xfffffe000750279c): d50331bf  .word 0xd50331bf
0x062eb90 (0xfffffe00075027a0): b942540b  ldr w11, [x0, #0x254]
0x062eb94 (0xfffffe00075027a4): d50331bf  .word 0xd50331bf
0x062eb98 (0xfffffe00075027a8): a9012fea  stp x10, x11, [sp, #0x10]
0x062eb9c (0xfffffe00075027ac): a90027e8  stp x8, x9, [sp, #0x0]
0x062eba0 (0xfffffe00075027b0): b0ffdca0  adrp x0, 0xfffffe0007097000
0x062eba4 (0xfffffe00075027b4): 913a9000  add x0, x0, #0xea4
0x062eba8 (0xfffffe00075027b8): 14000012  b 0xfffffe0007502800 <_sweet_usb_probe+0x560>
0x062ebac (0xfffffe00075027bc): b0ffdca0  adrp x0, 0xfffffe0007097000
0x062ebb0 (0xfffffe00075027c0): 9132c400  add x0, x0, #0xcb1
0x062ebb4 (0xfffffe00075027c4): 97f96cb0  bl 0xfffffe000735da84 <_printf>
0x062ebb8 (0xfffffe00075027c8): b0ffdca8  adrp x8, 0xfffffe0007097000
0x062ebbc (0xfffffe00075027cc): 91344108  add x8, x8, #0xd10
0x062ebc0 (0xfffffe00075027d0): b0ffdca9  adrp x9, 0xfffffe0007097000
0x062ebc4 (0xfffffe00075027d4): 9133b929  add x9, x9, #0xcee
0x062ebc8 (0xfffffe00075027d8): 7100031f  cmp w24, #0x0
0x062ebcc (0xfffffe00075027dc): 9a88b128  .word 0x9a88b128
0x062ebd0 (0xfffffe00075027e0): f00034e9  adrp x9, 0xfffffe0007ba1000
0x062ebd4 (0xfffffe00075027e4): f902a128  str x8, [x9, #0x540]
0x062ebd8 (0xfffffe00075027e8): 14000007  b 0xfffffe0007502804 <_sweet_usb_probe+0x564>
0x062ebdc (0xfffffe00075027ec): b0ffdca0  adrp x0, 0xfffffe0007097000
0x062ebe0 (0xfffffe00075027f0): 91357c00  add x0, x0, #0xd5f
0x062ebe4 (0xfffffe00075027f4): 14000003  b 0xfffffe0007502800 <_sweet_usb_probe+0x560>
0x062ebe8 (0xfffffe00075027f8): b0ffdca0  adrp x0, 0xfffffe0007097000
0x062ebec (0xfffffe00075027fc): 9139c800  add x0, x0, #0xe72
0x062ebf0 (0xfffffe0007502800): 97f96ca1  bl 0xfffffe000735da84 <_printf>
0x062ebf4 (0xfffffe0007502804): f85a83a8  .word 0xf85a83a8
0x062ebf8 (0xfffffe0007502808): 90003a89  adrp x9, 0xfffffe0007c52000
0x062ebfc (0xfffffe000750280c): d503201f  nop
0x062ec00 (0xfffffe0007502810): f945b129  ldr x9, [x9, #0xb60]
0x062ec04 (0xfffffe0007502814): eb08013f  cmp x9, x8
0x062ec08 (0xfffffe0007502818): 540032c1  b.ne 0xfffffe0007502e70
0x062ec0c (0xfffffe000750281c): 9107c3ff  add sp, sp, #0x1f0
0x062ec10 (0xfffffe0007502820): a9457bfd  ldp x29, x30, [sp, #0x50]
0x062ec14 (0xfffffe0007502824): a9444ff4  ldp x20, x19, [sp, #0x40]
0x062ec18 (0xfffffe0007502828): a94357f6  ldp x22, x21, [sp, #0x30]
0x062ec1c (0xfffffe000750282c): a9425ff8  ldp x24, x23, [sp, #0x20]
0x062ec20 (0xfffffe0007502830): a94167fa  ldp x26, x25, [sp, #0x10]
0x062ec24 (0xfffffe0007502834): a8c66ffc  ldp x28, x27, [sp, #0x60]
0x062ec28 (0xfffffe0007502838): d65f03c0  ret
0x062ec2c (0xfffffe000750283c): b0ffe428  adrp x8, 0xfffffe0007187000
0x062ec30 (0xfffffe0007502840): d503201f  nop
0x062ec34 (0xfffffe0007502844): f9448500  ldr x0, [x8, #0x908]
0x062ec38 (0xfffffe0007502848): 97fe0a27  bl 0xfffffe00074850e4 <_pmap_find_phys>
0x062ec3c (0xfffffe000750284c): 34fff8e0  cbz w0, 0xfffffe0007502768
0x062ec40 (0xfffffe0007502850): 910123f3  add x19, sp, #0x48
0x062ec44 (0xfffffe0007502854): f9001fff  str x31, [sp, #0x38]
0x062ec48 (0xfffffe0007502858): d3727c08  .word 0xd3727c08
0x062ec4c (0xfffffe000750285c): d0005c37  adrp x23, 0xfffffe0008088000
0x062ec50 (0xfffffe0007502860): 9128a2f7  add x23, x23, #0xa28
0x062ec54 (0xfffffe0007502864): f90002e8  str x8, [x23, #0x0]
0x062ec58 (0xfffffe0007502868): d0ffdca0  adrp x0, 0xfffffe0007098000
0x062ec5c (0xfffffe000750286c): 9104b800  add x0, x0, #0x12e
0x062ec60 (0xfffffe0007502870): d2800001  movz x1, #0x0
0x062ec64 (0xfffffe0007502874): 97f92acc  bl 0xfffffe000734d3a4 <_lck_grp_alloc_init>
0x062ec68 (0xfffffe0007502878): d0005c28  adrp x8, 0xfffffe0008088000
0x062ec6c (0xfffffe000750287c): f905bd00  str x0, [x8, #0xb78]
0x062ec70 (0xfffffe0007502880): d2800001  movz x1, #0x0
0x062ec74 (0xfffffe0007502884): 97f92d25  bl 0xfffffe000734dd18 <_lck_mtx_alloc_init>
0x062ec78 (0xfffffe0007502888): f90016e0  str x0, [x23, #0x28]
0x062ec7c (0xfffffe000750288c): 910123e8  add x8, sp, #0x48
0x062ec80 (0xfffffe0007502890): 91002108  add x8, x8, #0x8
0x062ec84 (0xfffffe0007502894): 6f00e400  .word 0x6f00e400
0x062ec88 (0xfffffe0007502898): ad080100  stp x0, x0, [x8, #0x80]
0x062ec8c (0xfffffe000750289c): ad090100  stp x0, x0, [x8, #0x90]
0x062ec90 (0xfffffe00075028a0): 3d805100  .word 0x3d805100
0x062ec94 (0xfffffe00075028a4): ad0283e0  stp x0, x0, [sp, #0x28]
0x062ec98 (0xfffffe00075028a8): ad0383e0  stp x0, x0, [sp, #0x38]
0x062ec9c (0xfffffe00075028ac): ad0483e0  stp x0, x0, [sp, #0x48]
0x062eca0 (0xfffffe00075028b0): 3c8b03e0  .word 0x3c8b03e0
0x062eca4 (0xfffffe00075028b4): 3c878260  .word 0x3c878260
0x062eca8 (0xfffffe00075028b8): 3c888260  .word 0x3c888260
0x062ecac (0xfffffe00075028bc): 3c898260  .word 0x3c898260
0x062ecb0 (0xfffffe00075028c0): 3c8a8260  .word 0x3c8a8260
0x062ecb4 (0xfffffe00075028c4): 3c8b8260  .word 0x3c8b8260
0x062ecb8 (0xfffffe00075028c8): 3c8c8260  .word 0x3c8c8260
0x062ecbc (0xfffffe00075028cc): 3c8d8260  .word 0x3c8d8260
0x062ecc0 (0xfffffe00075028d0): 3c8e8260  .word 0x3c8e8260
0x062ecc4 (0xfffffe00075028d4): 3c8f8260  .word 0x3c8f8260
0x062ecc8 (0xfffffe00075028d8): b0ffd848  adrp x8, 0xfffffe000700b000
0x062eccc (0xfffffe00075028dc): fd461900  .word 0xfd461900
0x062ecd0 (0xfffffe00075028e0): fd0027e0  .word 0xfd0027e0
0x062ecd4 (0xfffffe00075028e4): 52800028  movz w8, #0x1
0x062ecd8 (0xfffffe00075028e8): b90053e8  str w8, [sp, #0x50]
0x062ecdc (0xfffffe00075028ec): d0ffdca8  adrp x8, 0xfffffe0007098000
0x062ece0 (0xfffffe00075028f0): 9104e108  add x8, x8, #0x138
0x062ece4 (0xfffffe00075028f4): f9002fe8  str x8, [sp, #0x58]
0x062ece8 (0xfffffe00075028f8): 528001a8  movz w8, #0xd
0x062ecec (0xfffffe00075028fc): b90063e8  str w8, [sp, #0x60]
0x062ecf0 (0xfffffe0007502900): d0ffdca8  adrp x8, 0xfffffe0007098000
0x062ecf4 (0xfffffe0007502904): 91051908  add x8, x8, #0x146
0x062ecf8 (0xfffffe0007502908): f90037e8  str x8, [sp, #0x68]
0x062ecfc (0xfffffe000750290c): 90ffd848  adrp x8, 0xfffffe000700a000
0x062ed00 (0xfffffe0007502910): fd416900  .word 0xfd416900
0x062ed04 (0xfffffe0007502914): fc0743e0  .word 0xfc0743e0
0x062ed08 (0xfffffe0007502918): 1000a908  adr x8, 0xfffffe0007503e38
0x062ed0c (0xfffffe000750291c): d503201f  nop
0x062ed10 (0xfffffe0007502920): f90043e8  str x8, [sp, #0x80]
0x062ed14 (0xfffffe0007502924): 104fa2a8  adr x8, 0xfffffe00075a1d78
0x062ed18 (0xfffffe0007502928): d503201f  nop
0x062ed1c (0xfffffe000750292c): 104f81c9  adr x9, 0xfffffe00075a1964
0x062ed20 (0xfffffe0007502930): d503201f  nop
0x062ed24 (0xfffffe0007502934): a90da668  stp x8, x9, [x19, #0xd8]
0x062ed28 (0xfffffe0007502938): 104f7b68  adr x8, 0xfffffe00075a18a4
0x062ed2c (0xfffffe000750293c): d503201f  nop
0x062ed30 (0xfffffe0007502940): 104fc529  adr x9, 0xfffffe00075a21e4
0x062ed34 (0xfffffe0007502944): d503201f  nop
0x062ed38 (0xfffffe0007502948): a90ea668  stp x8, x9, [x19, #0xe8]
0x062ed3c (0xfffffe000750294c): 104fb908  adr x8, 0xfffffe00075a206c
0x062ed40 (0xfffffe0007502950): d503201f  nop
0x062ed44 (0xfffffe0007502954): f9009e68  str x8, [x19, #0x138]
0x062ed48 (0xfffffe0007502958): 1000ad68  adr x8, 0xfffffe0007503f04
0x062ed4c (0xfffffe000750295c): d503201f  nop
0x062ed50 (0xfffffe0007502960): f9008668  str x8, [x19, #0x108]
0x062ed54 (0xfffffe0007502964): 1000b6c8  adr x8, 0xfffffe000750403c
0x062ed58 (0xfffffe0007502968): d503201f  nop
0x062ed5c (0xfffffe000750296c): f9008e68  str x8, [x19, #0x118]
0x062ed60 (0xfffffe0007502970): b0003508  adrp x8, 0xfffffe0007ba3000
0x062ed64 (0xfffffe0007502974): 912e4108  add x8, x8, #0xb90
0x062ed68 (0xfffffe0007502978): f9009668  str x8, [x19, #0x128]
0x062ed6c (0xfffffe000750297c): 528000c8  movz w8, #0x6
0x062ed70 (0xfffffe0007502980): b9017be8  str w8, [sp, #0x178]
0x062ed74 (0xfffffe0007502984): 910082e1  add x1, x23, #0x20
0x062ed78 (0xfffffe0007502988): 910123e0  add x0, sp, #0x48
0x062ed7c (0xfffffe000750298c): 9403479a  bl 0xfffffe00075d47f4 <_ifnet_allocate_extended>
0x062ed80 (0xfffffe0007502990): 340000e0  cbz w0, 0xfffffe00075029ac
0x062ed84 (0xfffffe0007502994): d0ffdca0  adrp x0, 0xfffffe0007098000
0x062ed88 (0xfffffe0007502998): 91052400  add x0, x0, #0x149
0x062ed8c (0xfffffe000750299c): 97f96c3a  bl 0xfffffe000735da84 <_printf>
0x062ed90 (0xfffffe00075029a0): d0005c28  adrp x8, 0xfffffe0008088000
0x062ed94 (0xfffffe00075029a4): f905251f  str x31, [x8, #0xa48]
0x062ed98 (0xfffffe00075029a8): 1400005b  b 0xfffffe0007502b14 <_sweet_usb_probe+0x874>
0x062ed9c (0xfffffe00075029ac): d0005c37  adrp x23, 0xfffffe0008088000
0x062eda0 (0xfffffe00075029b0): f94526e0  ldr x0, [x23, #0xa48]
0x062eda4 (0xfffffe00075029b4): 528000c1  movz w1, #0x6
0x062eda8 (0xfffffe00075029b8): 94034cd5  bl 0xfffffe00075d5d0c <_ifnet_set_addrlen>
0x062edac (0xfffffe00075029bc): f94526e0  ldr x0, [x23, #0xa48]
0x062edb0 (0xfffffe00075029c0): 528001c1  movz w1, #0xe
0x062edb4 (0xfffffe00075029c4): 94034cdc  bl 0xfffffe00075d5d34 <_ifnet_set_hdrlen>
0x062edb8 (0xfffffe00075029c8): f94526e0  ldr x0, [x23, #0xa48]
0x062edbc (0xfffffe00075029cc): 5280bb81  movz w1, #0x5dc
0x062edc0 (0xfffffe00075029d0): 94034cc2  bl 0xfffffe00075d5cd8 <_ifnet_set_mtu>
0x062edc4 (0xfffffe00075029d4): f94526e0  ldr x0, [x23, #0xa48]
0x062edc8 (0xfffffe00075029d8): 52870001  movz w1, #0x3800
0x062edcc (0xfffffe00075029dc): 72a39381  movk w1, #0x1c9c, lsl #16
0x062edd0 (0xfffffe00075029e0): 94034ce9  bl 0xfffffe00075d5d84 <_ifnet_set_baudrate>
0x062edd4 (0xfffffe00075029e4): f94526e0  ldr x0, [x23, #0xa48]
0x062edd8 (0xfffffe00075029e8): 52910041  movz w1, #0x8802
0x062eddc (0xfffffe00075029ec): 529fffe2  movz w2, #0xffff
0x062ede0 (0xfffffe00075029f0): 940349da  bl 0xfffffe00075d5158 <_ifnet_set_flags>
0x062ede4 (0xfffffe00075029f4): f94526e0  ldr x0, [x23, #0xa48]
0x062ede8 (0xfffffe00075029f8): d2800001  movz x1, #0x0
0x062edec (0xfffffe00075029fc): 94025c66  bl 0xfffffe0007599b94 <_ifnet_attach>
0x062edf0 (0xfffffe0007502a00): 340000c0  cbz w0, 0xfffffe0007502a18
0x062edf4 (0xfffffe0007502a04): d0ffdca0  adrp x0, 0xfffffe0007098000
0x062edf8 (0xfffffe0007502a08): 9105ac00  add x0, x0, #0x16b
0x062edfc (0xfffffe0007502a0c): 97f96c1e  bl 0xfffffe000735da84 <_printf>
0x062ee00 (0xfffffe0007502a10): f90526ff  str x31, [x23, #0xa48]
0x062ee04 (0xfffffe0007502a14): 14000040  b 0xfffffe0007502b14 <_sweet_usb_probe+0x874>
0x062ee08 (0xfffffe0007502a18): f94526e0  ldr x0, [x23, #0xa48]
0x062ee0c (0xfffffe0007502a1c): b0ffd841  adrp x1, 0xfffffe000700b000
0x062ee10 (0xfffffe0007502a20): 91310021  add x1, x1, #0xc40
0x062ee14 (0xfffffe0007502a24): 528000c2  movz w2, #0x6
0x062ee18 (0xfffffe0007502a28): 94035186  bl 0xfffffe00075d7040 <_ifnet_set_lladdr>
0x062ee1c (0xfffffe0007502a2c): f94526e1  ldr x1, [x23, #0xa48]
0x062ee20 (0xfffffe0007502a30): 52800040  movz w0, #0x2
0x062ee24 (0xfffffe0007502a34): 940358f7  bl 0xfffffe00075d8e10 <_proto_plumb>
0x062ee28 (0xfffffe0007502a38): aa0003f3  mov x19, x0
0x062ee2c (0xfffffe0007502a3c): f90023ff  str x31, [sp, #0x40]
0x062ee30 (0xfffffe0007502a40): 350004e0  cbnz w0, 0xfffffe0007502adc
0x062ee34 (0xfffffe0007502a44): 910103e5  add x5, sp, #0x40
0x062ee38 (0xfffffe0007502a48): 52800040  movz w0, #0x2
0x062ee3c (0xfffffe0007502a4c): 52800041  movz w1, #0x2
0x062ee40 (0xfffffe0007502a50): 52800002  movz w2, #0x0
0x062ee44 (0xfffffe0007502a54): d2800003  movz x3, #0x0
0x062ee48 (0xfffffe0007502a58): d2800004  movz x4, #0x0
0x062ee4c (0xfffffe0007502a5c): 940e667d  bl 0xfffffe000789c450 <_sock_socket_internal>
0x062ee50 (0xfffffe0007502a60): aa0003f3  mov x19, x0
0x062ee54 (0xfffffe0007502a64): 350003c0  cbnz w0, 0xfffffe0007502adc
0x062ee58 (0xfffffe0007502a68): d10283a8  sub x8, x29, #0xa0
0x062ee5c (0xfffffe0007502a6c): 6f00e400  .word 0x6f00e400
0x062ee60 (0xfffffe0007502a70): ad010100  stp x0, x0, [x8, #0x10]
0x062ee64 (0xfffffe0007502a74): ad000100  stp x0, x0, [x8, #0x0]
0x062ee68 (0xfffffe0007502a78): d0ffdca2  adrp x2, 0xfffffe0007098000
0x062ee6c (0xfffffe0007502a7c): 91062c42  add x2, x2, #0x18b
0x062ee70 (0xfffffe0007502a80): d10283a0  sub x0, x29, #0xa0
0x062ee74 (0xfffffe0007502a84): 52800201  movz w1, #0x10
0x062ee78 (0xfffffe0007502a88): 940d0e2d  bl 0xfffffe000784633c <_snprintf>
0x062ee7c (0xfffffe0007502a8c): 52804208  movz w8, #0x210
0x062ee80 (0xfffffe0007502a90): 781703a8  .word 0x781703a8
0x062ee84 (0xfffffe0007502a94): 52951809  movz w9, #0xa8c0
0x062ee88 (0xfffffe0007502a98): 72a040e9  movk w9, #0x207, lsl #16
0x062ee8c (0xfffffe0007502a9c): b81743a9  .word 0xb81743a9
0x062ee90 (0xfffffe0007502aa0): 781903a8  .word 0x781903a8
0x062ee94 (0xfffffe0007502aa4): 12bfe009  movn w9, #0xff00
0x062ee98 (0xfffffe0007502aa8): b81943a9  .word 0xb81943a9
0x062ee9c (0xfffffe0007502aac): 781803a8  .word 0x781803a8
0x062eea0 (0xfffffe0007502ab0): 52951808  movz w8, #0xa8c0
0x062eea4 (0xfffffe0007502ab4): 72bfe0e8  movk w8, #0xff07, lsl #16
0x062eea8 (0xfffffe0007502ab8): b81843a8  .word 0xb81843a8
0x062eeac (0xfffffe0007502abc): f94023e0  ldr x0, [sp, #0x40]
0x062eeb0 (0xfffffe0007502ac0): d10283a2  sub x2, x29, #0xa0
0x062eeb4 (0xfffffe0007502ac4): 528d2341  movz w1, #0x691a
0x062eeb8 (0xfffffe0007502ac8): 72b00801  movk w1, #0x8040, lsl #16
0x062eebc (0xfffffe0007502acc): 940e63b7  bl 0xfffffe000789b9a8 <_sock_ioctl>
0x062eec0 (0xfffffe0007502ad0): aa0003f3  mov x19, x0
0x062eec4 (0xfffffe0007502ad4): f94023e0  ldr x0, [sp, #0x40]
0x062eec8 (0xfffffe0007502ad8): 940e66a4  bl 0xfffffe000789c568 <_sock_close>
0x062eecc (0xfffffe0007502adc): f94526e0  ldr x0, [x23, #0xa48]
0x062eed0 (0xfffffe0007502ae0): 52800821  movz w1, #0x41
0x062eed4 (0xfffffe0007502ae4): 52800822  movz w2, #0x41
0x062eed8 (0xfffffe0007502ae8): 9403499c  bl 0xfffffe00075d5158 <_ifnet_set_flags>
0x062eedc (0xfffffe0007502aec): d0ffdca8  adrp x8, 0xfffffe0007098000
0x062eee0 (0xfffffe0007502af0): 9106e908  add x8, x8, #0x1ba
0x062eee4 (0xfffffe0007502af4): d0ffdca9  adrp x9, 0xfffffe0007098000
0x062eee8 (0xfffffe0007502af8): 91072529  add x9, x9, #0x1c9
0x062eeec (0xfffffe0007502afc): 7100027f  cmp w19, #0x0
0x062eef0 (0xfffffe0007502b00): 9a880128  .word 0x9a880128
0x062eef4 (0xfffffe0007502b04): a9004fe8  stp x8, x19, [sp, #0x0]
0x062eef8 (0xfffffe0007502b08): d0ffdca0  adrp x0, 0xfffffe0007098000
0x062eefc (0xfffffe0007502b0c): 91063c00  add x0, x0, #0x18f
0x062ef00 (0xfffffe0007502b10): 97f96bdd  bl 0xfffffe000735da84 <_printf>
0x062ef04 (0xfffffe0007502b14): 52800017  movz w23, #0x0
0x062ef08 (0xfffffe0007502b18): d0005c33  adrp x19, 0xfffffe0008088000
0x062ef0c (0xfffffe0007502b1c): f9450e68  ldr x8, [x19, #0xa18]
0x062ef10 (0xfffffe0007502b20): 5298e098  movz w24, #0xc704
0x062ef14 (0xfffffe0007502b24): 52a80009  movz w9, #0x4000, lsl #16
0x062ef18 (0xfffffe0007502b28): b8386909  .word 0xb8386909
0x062ef1c (0xfffffe0007502b2c): d5033f9f  .word 0xd5033f9f
0x062ef20 (0xfffffe0007502b30): f9450e68  ldr x8, [x19, #0xa18]
0x062ef24 (0xfffffe0007502b34): b8786908  .word 0xb8786908
0x062ef28 (0xfffffe0007502b38): d50331bf  .word 0xd50331bf
0x062ef2c (0xfffffe0007502b3c): 36f000e8  tbz w8, #30, 0xfffffe0007502b58
0x062ef30 (0xfffffe0007502b40): 52807d00  movz w0, #0x3e8
0x062ef34 (0xfffffe0007502b44): 97f8c345  bl 0xfffffe0007333858 <_delay>
0x062ef38 (0xfffffe0007502b48): 110006f7  add w23, w23, #0x1
0x062ef3c (0xfffffe0007502b4c): 7107d2ff  cmp w23, #0x1f4
0x062ef40 (0xfffffe0007502b50): 54ffff01  b.ne 0xfffffe0007502b30
0x062ef44 (0xfffffe0007502b54): 52803e97  movz w23, #0x1f4
0x062ef48 (0xfffffe0007502b58): f9450e68  ldr x8, [x19, #0xa18]
0x062ef4c (0xfffffe0007502b5c): 5298e098  movz w24, #0xc704
0x062ef50 (0xfffffe0007502b60): b8786908  .word 0xb8786908
0x062ef54 (0xfffffe0007502b64): d50331bf  .word 0xd50331bf
0x062ef58 (0xfffffe0007502b68): d0ffdca9  adrp x9, 0xfffffe0007098000
0x062ef5c (0xfffffe0007502b6c): 91002129  add x9, x9, #0x8
0x062ef60 (0xfffffe0007502b70): d0ffdc8a  adrp x10, 0xfffffe0007094000
0x062ef64 (0xfffffe0007502b74): 911ee14a  add x10, x10, #0x7b8
0x062ef68 (0xfffffe0007502b78): 7202011f  tst/ands w8, ...
0x062ef6c (0xfffffe0007502b7c): 9a890148  .word 0x9a890148
0x062ef70 (0xfffffe0007502b80): f9450e69  ldr x9, [x19, #0xa18]
0x062ef74 (0xfffffe0007502b84): 5298220a  movz w10, #0xc110
0x062ef78 (0xfffffe0007502b88): b86a6929  .word 0xb86a6929
0x062ef7c (0xfffffe0007502b8c): d50331bf  .word 0xd50331bf
0x062ef80 (0xfffffe0007502b90): f9450e6a  ldr x10, [x19, #0xa18]
0x062ef84 (0xfffffe0007502b94): 5298e00b  movz w11, #0xc700
0x062ef88 (0xfffffe0007502b98): b86b694a  .word 0xb86b694a
0x062ef8c (0xfffffe0007502b9c): d50331bf  .word 0xd50331bf
0x062ef90 (0xfffffe0007502ba0): a9012be9  stp x9, x10, [sp, #0x10]
0x062ef94 (0xfffffe0007502ba4): a9005fe8  stp x8, x23, [sp, #0x0]
0x062ef98 (0xfffffe0007502ba8): b0ffdca0  adrp x0, 0xfffffe0007097000
0x062ef9c (0xfffffe0007502bac): 913f2400  add x0, x0, #0xfc9
0x062efa0 (0xfffffe0007502bb0): 97f96bb5  bl 0xfffffe000735da84 <_printf>
0x062efa4 (0xfffffe0007502bb4): f9450e68  ldr x8, [x19, #0xa18]
0x062efa8 (0xfffffe0007502bb8): b8786908  .word 0xb8786908
0x062efac (0xfffffe0007502bbc): d50331bf  .word 0xd50331bf
0x062efb0 (0xfffffe0007502bc0): 37f7dd48  tbnz w8, #30, 0xfffffe0007502768
0x062efb4 (0xfffffe0007502bc4): f9400ac8  ldr x8, [x22, #0x10]
0x062efb8 (0xfffffe0007502bc8): f94002c9  ldr x9, [x22, #0x0]
0x062efbc (0xfffffe0007502bcc): 5298800a  movz w10, #0xc400
0x062efc0 (0xfffffe0007502bd0): b82a6928  .word 0xb82a6928
0x062efc4 (0xfffffe0007502bd4): d5033f9f  .word 0xd5033f9f
0x062efc8 (0xfffffe0007502bd8): b94016c8  ldr w8, [x22, #0x14]
0x062efcc (0xfffffe0007502bdc): f94002c9  ldr x9, [x22, #0x0]
0x062efd0 (0xfffffe0007502be0): 5298808a  movz w10, #0xc404
0x062efd4 (0xfffffe0007502be4): b82a6928  .word 0xb82a6928
0x062efd8 (0xfffffe0007502be8): d5033f9f  .word 0xd5033f9f
0x062efdc (0xfffffe0007502bec): f94002c8  ldr x8, [x22, #0x0]
0x062efe0 (0xfffffe0007502bf0): 52988109  movz w9, #0xc408
0x062efe4 (0xfffffe0007502bf4): 5282000a  movz w10, #0x1000
0x062efe8 (0xfffffe0007502bf8): 72b0000a  movk w10, #0x8000, lsl #16
0x062efec (0xfffffe0007502bfc): b829690a  .word 0xb829690a
0x062eff0 (0xfffffe0007502c00): d5033f9f  .word 0xd5033f9f
0x062eff4 (0xfffffe0007502c04): f94002c8  ldr x8, [x22, #0x0]
0x062eff8 (0xfffffe0007502c08): 52988189  movz w9, #0xc40c
0x062effc (0xfffffe0007502c0c): b8696908  .word 0xb8696908
0x062f000 (0xfffffe0007502c10): d50331bf  .word 0xd50331bf
0x062f004 (0xfffffe0007502c14): 12003d08  .word 0x12003d08
0x062f008 (0xfffffe0007502c18): f94002ca  ldr x10, [x22, #0x0]
0x062f00c (0xfffffe0007502c1c): b8296948  .word 0xb8296948
0x062f010 (0xfffffe0007502c20): d5033f9f  .word 0xd5033f9f
0x062f014 (0xfffffe0007502c24): b9001adf  str w31, [x22, #0x18]
0x062f018 (0xfffffe0007502c28): f94002c8  ldr x8, [x22, #0x0]
0x062f01c (0xfffffe0007502c2c): 5298e009  movz w9, #0xc700
0x062f020 (0xfffffe0007502c30): b8696908  .word 0xb8696908
0x062f024 (0xfffffe0007502c34): d50331bf  .word 0xd50331bf
0x062f028 (0xfffffe0007502c38): 12165508  .word 0x12165508
0x062f02c (0xfffffe0007502c3c): f94002ca  ldr x10, [x22, #0x0]
0x062f030 (0xfffffe0007502c40): b8296948  .word 0xb8296948
0x062f034 (0xfffffe0007502c44): d5033f9f  .word 0xd5033f9f
0x062f038 (0xfffffe0007502c48): f94002c8  ldr x8, [x22, #0x0]
0x062f03c (0xfffffe0007502c4c): 5298e109  movz w9, #0xc708
0x062f040 (0xfffffe0007502c50): 528000ea  movz w10, #0x7
0x062f044 (0xfffffe0007502c54): b829690a  .word 0xb829690a
0x062f048 (0xfffffe0007502c58): d5033f9f  .word 0xd5033f9f
0x062f04c (0xfffffe0007502c5c): 52800000  movz w0, #0x0
0x062f050 (0xfffffe0007502c60): 52800121  movz w1, #0x9
0x062f054 (0xfffffe0007502c64): 52800002  movz w2, #0x0
0x062f058 (0xfffffe0007502c68): 52800003  movz w3, #0x0
0x062f05c (0xfffffe0007502c6c): 940000c9  bl 0xfffffe0007502f90 <_ud_epcmd>
0x062f060 (0xfffffe0007502c70): 35000300  cbnz w0, 0xfffffe0007502cd0
0x062f064 (0xfffffe0007502c74): 52800021  movz w1, #0x1
0x062f068 (0xfffffe0007502c78): 52820002  movz w2, #0x1000
0x062f06c (0xfffffe0007502c7c): 5280a003  movz w3, #0x500
0x062f070 (0xfffffe0007502c80): 940000c4  bl 0xfffffe0007502f90 <_ud_epcmd>
0x062f074 (0xfffffe0007502c84): 35000260  cbnz w0, 0xfffffe0007502cd0
0x062f078 (0xfffffe0007502c88): 52800041  movz w1, #0x2
0x062f07c (0xfffffe0007502c8c): 52800022  movz w2, #0x1
0x062f080 (0xfffffe0007502c90): 52800003  movz w3, #0x0
0x062f084 (0xfffffe0007502c94): 940000bf  bl 0xfffffe0007502f90 <_ud_epcmd>
0x062f088 (0xfffffe0007502c98): 350001c0  cbnz w0, 0xfffffe0007502cd0
0x062f08c (0xfffffe0007502c9c): 52800020  movz w0, #0x1
0x062f090 (0xfffffe0007502ca0): 52800021  movz w1, #0x1
0x062f094 (0xfffffe0007502ca4): 52820002  movz w2, #0x1000
0x062f098 (0xfffffe0007502ca8): 5280a003  movz w3, #0x500
0x062f09c (0xfffffe0007502cac): 72a04003  movk w3, #0x200, lsl #16
0x062f0a0 (0xfffffe0007502cb0): 940000b8  bl 0xfffffe0007502f90 <_ud_epcmd>
0x062f0a4 (0xfffffe0007502cb4): 350000e0  cbnz w0, 0xfffffe0007502cd0
0x062f0a8 (0xfffffe0007502cb8): 52800020  movz w0, #0x1
0x062f0ac (0xfffffe0007502cbc): 52800041  movz w1, #0x2
0x062f0b0 (0xfffffe0007502cc0): 52800022  movz w2, #0x1
0x062f0b4 (0xfffffe0007502cc4): 52800003  movz w3, #0x0
0x062f0b8 (0xfffffe0007502cc8): 940000b2  bl 0xfffffe0007502f90 <_ud_epcmd>
0x062f0bc (0xfffffe0007502ccc): 340000a0  cbz w0, 0xfffffe0007502ce0
0x062f0c0 (0xfffffe0007502cd0): d0ffdca0  adrp x0, 0xfffffe0007098000
0x062f0c4 (0xfffffe0007502cd4): 91003800  add x0, x0, #0xe
0x062f0c8 (0xfffffe0007502cd8): 97f96b6b  bl 0xfffffe000735da84 <_printf>
0x062f0cc (0xfffffe0007502cdc): 17fffea3  b 0xfffffe0007502768 <_sweet_usb_probe+0x4c8>
0x062f0d0 (0xfffffe0007502ce0): aa1303f7  mov x23, x19
0x062f0d4 (0xfffffe0007502ce4): f9450e68  ldr x8, [x19, #0xa18]
0x062f0d8 (0xfffffe0007502ce8): 5298e409  movz w9, #0xc720
0x062f0dc (0xfffffe0007502cec): 5280006a  movz w10, #0x3
0x062f0e0 (0xfffffe0007502cf0): b829690a  .word 0xb829690a
0x062f0e4 (0xfffffe0007502cf4): d5033f9f  .word 0xd5033f9f
0x062f0e8 (0xfffffe0007502cf8): 940000e4  bl 0xfffffe0007503088 <_ud_start_setup>
0x062f0ec (0xfffffe0007502cfc): 52910000  movz w0, #0x8800
0x062f0f0 (0xfffffe0007502d00): 72a14de0  movk w0, #0xa6f, lsl #16
0x062f0f4 (0xfffffe0007502d04): 52802001  movz w1, #0x100
0x062f0f8 (0xfffffe0007502d08): 97fe897e  bl 0xfffffe00074a5300 <_ml_io_map>
0x062f0fc (0xfffffe0007502d0c): b4000360  cbz x0, 0xfffffe0007502d78
0x062f100 (0xfffffe0007502d10): aa0003f3  mov x19, x0
0x062f104 (0xfffffe0007502d14): b9401018  ldr w24, [x0, #0x10]
0x062f108 (0xfffffe0007502d18): d50331bf  .word 0xd50331bf
0x062f10c (0xfffffe0007502d1c): b9403019  ldr w25, [x0, #0x30]
0x062f110 (0xfffffe0007502d20): d50331bf  .word 0xd50331bf
0x062f114 (0xfffffe0007502d24): b9400808  ldr w8, [x0, #0x8]
0x062f118 (0xfffffe0007502d28): d50331bf  .word 0xd50331bf
0x062f11c (0xfffffe0007502d2c): a900a3f9  stp x25, x8, [sp, #0x8]
0x062f120 (0xfffffe0007502d30): f90003f8  str x24, [sp, #0x0]
0x062f124 (0xfffffe0007502d34): d0ffdca0  adrp x0, 0xfffffe0007098000
0x062f128 (0xfffffe0007502d38): 9100c800  add x0, x0, #0x32
0x062f12c (0xfffffe0007502d3c): 97f96b52  bl 0xfffffe000735da84 <_printf>
0x062f130 (0xfffffe0007502d40): 52a20208  movz w8, #0x1010, lsl #16
0x062f134 (0xfffffe0007502d44): 2a080308  .word 0x2a080308
0x062f138 (0xfffffe0007502d48): b9001268  str w8, [x19, #0x10]
0x062f13c (0xfffffe0007502d4c): 32080328  .word 0x32080328
0x062f140 (0xfffffe0007502d50): b9003268  str w8, [x19, #0x30]
0x062f144 (0xfffffe0007502d54): d5033f9f  .word 0xd5033f9f
0x062f148 (0xfffffe0007502d58): b9401268  ldr w8, [x19, #0x10]
0x062f14c (0xfffffe0007502d5c): d50331bf  .word 0xd50331bf
0x062f150 (0xfffffe0007502d60): b9403269  ldr w9, [x19, #0x30]
0x062f154 (0xfffffe0007502d64): d50331bf  .word 0xd50331bf
0x062f158 (0xfffffe0007502d68): a90027e8  stp x8, x9, [sp, #0x0]
0x062f15c (0xfffffe0007502d6c): d0ffdca0  adrp x0, 0xfffffe0007098000
0x062f160 (0xfffffe0007502d70): 91020000  add x0, x0, #0x80
0x062f164 (0xfffffe0007502d74): 97f96b44  bl 0xfffffe000735da84 <_printf>
0x062f168 (0xfffffe0007502d78): 52800013  movz w19, #0x0
0x062f16c (0xfffffe0007502d7c): f9450ee8  ldr x8, [x23, #0xa18]
0x062f170 (0xfffffe0007502d80): 5298e089  movz w9, #0xc704
0x062f174 (0xfffffe0007502d84): b8696908  .word 0xb8696908
0x062f178 (0xfffffe0007502d88): d50331bf  .word 0xd50331bf
0x062f17c (0xfffffe0007502d8c): 32010108  .word 0x32010108
0x062f180 (0xfffffe0007502d90): f9450eea  ldr x10, [x23, #0xa18]
0x062f184 (0xfffffe0007502d94): b8296948  .word 0xb8296948
0x062f188 (0xfffffe0007502d98): d5033f9f  .word 0xd5033f9f
0x062f18c (0xfffffe0007502d9c): 5298e198  movz w24, #0xc70c
0x062f190 (0xfffffe0007502da0): f9450ee8  ldr x8, [x23, #0xa18]
0x062f194 (0xfffffe0007502da4): b8786908  .word 0xb8786908
0x062f198 (0xfffffe0007502da8): d50331bf  .word 0xd50331bf
0x062f19c (0xfffffe0007502dac): 36b000e8  tbz w8, #22, 0xfffffe0007502dc8
0x062f1a0 (0xfffffe0007502db0): 52807d00  movz w0, #0x3e8
0x062f1a4 (0xfffffe0007502db4): 97f8c2a9  bl 0xfffffe0007333858 <_delay>
0x062f1a8 (0xfffffe0007502db8): 11000673  add w19, w19, #0x1
0x062f1ac (0xfffffe0007502dbc): 7107d27f  cmp w19, #0x1f4
0x062f1b0 (0xfffffe0007502dc0): 54ffff01  b.ne 0xfffffe0007502da0
0x062f1b4 (0xfffffe0007502dc4): 52803e93  movz w19, #0x1f4
0x062f1b8 (0xfffffe0007502dc8): f94002c8  ldr x8, [x22, #0x0]
0x062f1bc (0xfffffe0007502dcc): 5298e189  movz w9, #0xc70c
0x062f1c0 (0xfffffe0007502dd0): b8696908  .word 0xb8696908
0x062f1c4 (0xfffffe0007502dd4): d50331bf  .word 0xd50331bf
0x062f1c8 (0xfffffe0007502dd8): f9400ac9  ldr x9, [x22, #0x10]
0x062f1cc (0xfffffe0007502ddc): a900a7f3  stp x19, x9, [sp, #0x8]
0x062f1d0 (0xfffffe0007502de0): f90003e8  str x8, [sp, #0x0]
0x062f1d4 (0xfffffe0007502de4): d0ffdca0  adrp x0, 0xfffffe0007098000
0x062f1d8 (0xfffffe0007502de8): 91031000  add x0, x0, #0xc4
0x062f1dc (0xfffffe0007502dec): 97f96b26  bl 0xfffffe000735da84 <_printf>
0x062f1e0 (0xfffffe0007502df0): d0ffdca8  adrp x8, 0xfffffe0007098000
0x062f1e4 (0xfffffe0007502df4): 91040508  add x8, x8, #0x101
0x062f1e8 (0xfffffe0007502df8): f902a288  str x8, [x20, #0x540]
0x062f1ec (0xfffffe0007502dfc): 100018a0  adr x0, 0xfffffe0007503110
0x062f1f0 (0xfffffe0007502e00): d503201f  nop
0x062f1f4 (0xfffffe0007502e04): 9100e3e2  add x2, sp, #0x38
0x062f1f8 (0xfffffe0007502e08): d2800001  movz x1, #0x0
0x062f1fc (0xfffffe0007502e0c): 97fa2fdf  bl 0xfffffe000738ed88 <_kernel_thread_start>
0x062f200 (0xfffffe0007502e10): 35000060  cbnz w0, 0xfffffe0007502e1c
0x062f204 (0xfffffe0007502e14): f9401fe0  ldr x0, [sp, #0x38]
0x062f208 (0xfffffe0007502e18): 97fa28b2  bl 0xfffffe000738d0e0 <_thread_deallocate>
0x062f20c (0xfffffe0007502e1c): 52800028  movz w8, #0x1
0x062f210 (0xfffffe0007502e20): b9004be8  str w8, [sp, #0x48]
0x062f214 (0xfffffe0007502e24): d0ffdca0  adrp x0, 0xfffffe0007098000
0x062f218 (0xfffffe0007502e28): 91048800  add x0, x0, #0x122
0x062f21c (0xfffffe0007502e2c): 910123e1  add x1, sp, #0x48
0x062f220 (0xfffffe0007502e30): 52800082  movz w2, #0x4
0x062f224 (0xfffffe0007502e34): 94169b90  bl 0xfffffe0007aa9c74 <_PE_parse_boot_argn>
0x062f228 (0xfffffe0007502e38): b9404be8  ldr w8, [sp, #0x48]
0x062f22c (0xfffffe0007502e3c): 34ffc968  cbz w8, 0xfffffe0007502768
0x062f230 (0xfffffe0007502e40): d0005c28  adrp x8, 0xfffffe0008088000
0x062f234 (0xfffffe0007502e44): f9452508  ldr x8, [x8, #0xa48]
0x062f238 (0xfffffe0007502e48): b4ffc908  cbz x8, 0xfffffe0007502768
0x062f23c (0xfffffe0007502e4c): 10007620  adr x0, 0xfffffe0007503d10
0x062f240 (0xfffffe0007502e50): d503201f  nop
0x062f244 (0xfffffe0007502e54): 9100e3e2  add x2, sp, #0x38
0x062f248 (0xfffffe0007502e58): d2800001  movz x1, #0x0
0x062f24c (0xfffffe0007502e5c): 97fa2fcb  bl 0xfffffe000738ed88 <_kernel_thread_start>
0x062f250 (0xfffffe0007502e60): 35ffc840  cbnz w0, 0xfffffe0007502768
0x062f254 (0xfffffe0007502e64): f9401fe0  ldr x0, [sp, #0x38]
0x062f258 (0xfffffe0007502e68): 97fa289e  bl 0xfffffe000738d0e0 <_thread_deallocate>
0x062f25c (0xfffffe0007502e6c): 17fffe3f  b 0xfffffe0007502768 <_sweet_usb_probe+0x4c8>
0x062f260 (0xfffffe0007502e70): 9412a5d3  bl 0xfffffe00079ac5bc <___stack_chk_fail>
```

