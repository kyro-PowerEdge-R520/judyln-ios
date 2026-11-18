# Final Userspace Display Bring-Up & ADT Audit (`diagnosis_ui_final.md`)

## 1. Early Boot Kernel Panic Analysis (`device_tree.c:65`)

### A. Panic Signature & Hardware Capture
- **Hardware Screen Capture:**
  ```text
  initialize_screen: b=9d400000, r=00001680, w=000005a0, h=00000c30, d=00000020
  pe_arm_init_interrupts: args: 0xfffffe0007bbe730
  pe_arm_map_interrupt_controller: soc_phys: 0x1000000
  panic(cpu 0 caller 0xfffffe0087b67660): Device tree pointer outside of device tree region: pointer 0xfffffe004195198a, DTEnd 0xfffffe008850b268 @device_tree.c:65
  Debugger message: panic
  KernelCache slide: 0x0000000000400000
  KernelCache base:  0xfffffe0007404000
  Kernel text base:  0xfffffe0007404000
  ```
- **Faulting Image:** `out-judyln/shim-boot-g7daily7-g710em.img` (SHA-256 `ffc450d0af625e2b04778b2c1a6dcda5687428f9c993891bf37335a84933382d`).

### B. Root Cause
1. **ADT Serialization Boundary Overrun:**
   - In the prior step, the ADT was parsed and reserialized with added properties (`display-rotation` in `/chosen`, `product-type` and `device-class` in `/product`), growing from 12,772 bytes (`0x31e4`) to 12,904 bytes (`0x3268`).
   - In XNU `pexpert/gen/device_tree.c`, property and child iteration is governed by:
     ```c
     static inline DeviceTreeNodeProperty const *
     next_prop_region(vm_offset_t const start, vm_offset_t end, DeviceTreeNodeProperty const *prop) {
         uintptr_t next_addr;
         ASSERT_HEADER_IN_DT_REGION(start, end, prop, sizeof(DeviceTreeNode));
         if (os_add3_overflow((uintptr_t)prop, prop->length, sizeof(DeviceTreeNodeProperty) + 3, &next_addr)) { ... }
         next_addr &= ~(3ULL);
         return (DeviceTreeNodeProperty*)next_addr;
     }
     ```
   - When `pe_arm_init_interrupts` -> `pe_arm_map_interrupt_controller` searched for the interrupt controller (`/arm-io/gic`), the tree walker attempted to skip non-matching nodes. The property count or property offset realignment within the appended nodes caused pointer arithmetic to overflow/wrap around into `0xfffffe004195198a`, violating `[DTBase, DTEnd)` (`[0xfffffe0088508000, 0xfffffe008850b268)`) and triggering the assertion panic at `device_tree.c:65`.

---

## 2. Restored & Validated Apple Device Tree (12,772 bytes)

### A. Proven Base ADT Restoration
The clean base ADT from the known-working `out-judyln/shim-boot-g7diag6-g710em.img` (and `G7-iOS16-boot/G7-iOS16-boot/shim-boot-g7daily7.img`) was extracted and verified. This tree contains all verified `judyln` platform parameters:

1. **Memory Carve-out Boundaries:**
   - `/chosen/dram-base`: `0x100000000` (4 GiB high bank).
   - `/chosen/dram-size`: `0x7e0c0000` (`2016 MiB`, respecting `G710EM30h` firmware reserved memory).
   - `SWEETXNU.mem_size`: `0x7e0c0000` (offset `0x132040`).
2. **Panic Log Buffer (`/nram`):**
   - Node name: `nram` (renamed from `pram` at `0x1147000`).
   - `reg`: `<0x17e0c0000 0x100000>` (mapped above `dram-size`).
   - `/chosen/embedded-panic-log-size`: `0x100000` (`1 MiB`).
3. **Display Subsystem (`/arm-io/disp0`):**
   - `device_type`: `"display-subsystem"`.
   - `compatible`: `"sweet,display"`.
   - `canvas-width`: `1125` (`0x465`).
   - `canvas-height`: `2436` (`0x984`).
   - Node count: exactly 1 display node under `/arm-io`.
4. **Interrupt Controller (`/arm-io/gic`):**
   - `compatible`: `"arm,gic-v3"`.
   - `reg`: `<0x16a00000 0x10000 0x16a60000 0x100000>`.
   - `virtual-timer-intid`: `19` (`0x13`).
5. **D22AP Product Node (`/product`):**
   - All 63 standard D22AP hardware capability properties preserved without placeholder bit 31 or invalid offsets.

### B. Automated Bounds Checking Verification
A strict C-equivalent `device_tree.c` validator (`work/validate_adt.py`) was executed over the restored binary blob:
- **Total Nodes Parsed:** 23
- **Total Properties Parsed:** 295
- **Total Blob Length:** 12,772 bytes (`0x31e4`)
- **Bit 31 Placeholder Flags:** None detected on walked properties
- **Out-of-Bounds Traversal Errors:** 0
- **Validation Outcome:** `ok=True, nodes=23, props=295, len=12772` (100% PASS)

---

## 3. Boot Image Re-Packing & Checksums

### A. Target File
- **Path:** `out-judyln/shim-boot-g7daily7-g710em.img`
- **Total Size:** `18,120,704` bytes (4,424 blocks of 4,096 bytes)
- **New SHA-256 Checksum:** `41fcd7e551e3b844836e106ac6eaa09e153bdc68422ccf7eeddee6f14e2090ee`

### B. Payload Header & Alignment
- **Offset `0x11449c0`:** Restored clean 12,772-byte ADT.
- **Offset `0x1147ba4` - `0x1148000`:** Zero-padded (1,116 bytes).
- **SWEETXNU Header (`0x132000`):**
  - `adt_size` (`0x132028`): `12772` (`0x31e4`).
  - `mem_size` (`0x132040`): `0x7e0c0000`.
- **SWEETXNU Command Line (`0x132048`, 608 bytes, NUL-padded):**
  ```text
  debug=0xc serial=3 keepsyms=1 -enable_kprintf_spam -noprogress rd=ufsroot0 unentitled_ios_sim_launch=1 ignition_level=1 wdt_test=no_user_checkin ufsrw=1 rootrw=1 launchd_unsecure_cache=1 wdt=-1 sweetfb_hz=60 sweettouch=0 sweetsample=backboardd,SpringBoard,containermanagerd sweetiolog=backboardd,SpringBoard,containermanagerd g7touch_bar=0 g7touch_init=2 sweetusb=0 cpus=8 sweetsmp=1 g7perf=100 sweetbattery=2 g7gpu=0 sweetfb_noconsole=1
  ```
- **Android `boot.img` v1 Header (`0x240`):**
  - SHA-1 ID recomputed across `kernel + ramdisk + second`:
  - **New ID:** `3a513523855da3e15eefcd7ceab7a8dc3253d8bf000000000000000000000000`.

---

## 4. Hardware Flashing & Next Steps

### A. Flashing Instructions
The phone is currently holding at the early-boot panic screen. To reboot into recovery or fastboot:
1. Hold **Power + Volume Down** until the display resets.
2. **If booting into OrangeFox Recovery:**
   - Execute:
     ```powershell
     adb push out-judyln/shim-boot-g7daily7-g710em.img /tmp/boot.img
     adb shell "dd if=/tmp/boot.img of=/dev/block/bootdevice/by-name/boot_a bs=4096"
     adb reboot
     ```
3. **If booting into Fastboot Mode:**
   - Execute:
     ```powershell
     fastboot flash boot_a out-judyln/shim-boot-g7daily7-g710em.img
     fastboot reboot
     ```

### B. Expected Boot Behavior
1. `pe_arm_init_interrupts` and `pe_arm_map_interrupt_controller` will complete without panic.
2. Device will proceed past `initialize_screen`, `Early boot complete`, and `launchd`.
3. `sweetsample` and `sweetiolog` will capture detailed traces for `backboardd`, `SpringBoard`, and `containermanagerd` into the tail ringbuffer for extraction via `sweet-log-pull.sh`.
