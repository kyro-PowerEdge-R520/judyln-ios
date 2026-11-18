# UI Fast Boot Analysis & Patch Notes (`boot-g7em-ui-fast.img`)

## 1. Image Summary & Integrity Verification

- **Source (`golden_boot\boot_a-cpu-ui-touch.img`)**: `18112512` bytes, SHA-256: `766a88577c208af62583d199fa5dbd8f46811342aa109db5c334a5d38607b3e7` (verified read-only & untouched), header ID: `08b9b1eeecef061d53f2551691bed4a195ad78b2`
- **Output (`work\next-gen\boot-g7em-ui-fast.img`)**: `18112512` bytes, SHA-256: `b3c935a4e35ac1fafe2401a614c7d9b230efc87daa43cfcb641a236cfdf17162`, header ID: `8204a522b6a954e6061a3be25a11c01143500bdb`
- **Total patched instructions**: `11` `bl _IOLog` calls replaced with `nop` (`0xd503201f`).

## 2. `sweetfb_noconsole` & `SweetSurface` / `AppleCLCD` First Frame Swap Findings

### Framebuffer Console Hiding Condition
- `AppleCLCD::present` (`0x0bac804`, VA `0xfffffe0007a80414`) reads `[this + 0x104]` (`0x0bac838`). On the first frame swap, it calls `PE_parse_boot_argn("sweetfb_noconsole", ...)` at `0x0bac84c`..`0x0bac85c` and stores `1` to `[0xfffffe0007c154c8]` (`0x0bac878`).
- `_console_ring_try_empty` (`0x059be54..0x059be64`) and `__cnputs` (`0x059c1c4..0x059c1d4`) read `[0xfffffe0007c154c8]`. Once non-zero, both skip framebuffer console rendering unless `_panic_active()` returns non-zero.
- Before `AppleCLCD::present()` runs for the first time, `[0xfffffe0007c154c8]` starts at `0`, so synchronous `SWEET AKS:` and `IOK ` `IOLog` prints still scroll on the CPU framebuffer during early boot and `backboardd` startup.

### First Frame Swap Gate Check (`SweetSurface` & `AppleCLCD`)
- `SweetSurface` (`0x0ba8f80..0x0bab9e0`) and `SweetSurfaceRef` (`0x0ba957c..0x0bab978`) only wrap `OSObject` memory-backed IOSurface state (`kernelAddress`, `IOSurfaceRootUserClient::addRef` at `0x0ba9e74`, `returnSurface` at `0x0baa1b8`); there are no hardware locks, GPU dependencies, or swap gates.
- `AppleCLCD::start` (`0x0bac06c`) sets a `sweetfb_hz` (60 Hz) `IOTimerEventSource` vsync timer (`0x0bac2c4`), `AppleCLCD::vsyncFired` (`0x0bac484`) calls `AppleCLCD::present()` (`0x0bac6fc`), and `AppleCLCD::swap()` (`0x0bacf08`) immediately presents the swapped surface.
- Thus, nothing in `SweetSurface` or `AppleCLCD` blocks the first frame swap; muting the repetitive `SWEET AKS:` and `IOK ` prints removes CPU framebuffer scrolling overhead before `AppleCLCD::present()` latches `sweetfb_noconsole=1`.

## 3. `__TEXT_EXEC` Cross-References & Surrounding Disassembly

### `sweetfb_noconsole` (1 xrefs)
- img `0x0bac84c` (`0xfffffe0007a8045c`, `<__ZN9AppleCLCD7presentEPKhj+0x48>`) -> string `0x27cd71`
```asm
0x0bac83c (0xfffffe0007a8044c): 35000208  cbnz w8, 0xfffffe0007a8048c
0x0bac840 (0xfffffe0007a80450): b81a43bf  .word 0xb81a43bf
0x0bac844 (0xfffffe0007a80454): 52800028  movz w8, #0x1
0x0bac848 (0xfffffe0007a80458): 39041268  strb w8, [x19, #0x104]
0x0bac84c (0xfffffe0007a8045c): 90ffb680  adrp x0, 0xfffffe0007150000  <-- xref
0x0bac850 (0xfffffe0007a80460): 91262400  add x0, x0, #0x989
0x0bac854 (0xfffffe0007a80464): d10173a1  sub x1, x29, #0x5c
0x0bac858 (0xfffffe0007a80468): 52800082  movz w2, #0x4
0x0bac85c (0xfffffe0007a8046c): 9400a602  bl 0xfffffe0007aa9c74 <_PE_parse_boot_argn>
0x0bac860 (0xfffffe0007a80470): 340000e0  cbz w0, 0xfffffe0007a8048c
0x0bac864 (0xfffffe0007a80474): b85a43a8  .word 0xb85a43a8
0x0bac868 (0xfffffe0007a80478): 340000a8  cbz w8, 0xfffffe0007a8048c
0x0bac86c (0xfffffe0007a8047c): b0000ca8  adrp x8, 0xfffffe0007c15000
0x0bac870 (0xfffffe0007a80480): d503201f  nop
0x0bac874 (0xfffffe0007a80484): 52800029  movz w9, #0x1
0x0bac878 (0xfffffe0007a80488): b904c909  str w9, [x8, #0x4c8]
0x0bac87c (0xfffffe0007a8048c): d280001b  movz x27, #0x0
0x0bac880 (0xfffffe0007a80490): 910192a8  add x8, x21, #0x64
0x0bac884 (0xfffffe0007a80494): a9384fa8  stp x8, x19, [x29, #0x-80]
0x0bac888 (0xfffffe0007a80498): f81983b5  .word 0xf81983b5
```

### `SweetSurface` (6 xrefs)
- img `0x0ba8f88` (`0xfffffe0007a7cb98`, `<__ZN12SweetSurface9MetaClassC1Ev+0x8>`) -> string `0x27c77c`
```asm
0x0ba8f78 (0xfffffe0007a7cb88): a8c17bfd  ldp x29, x30, [sp, #0x10]
0x0ba8f7c (0xfffffe0007a7cb8c): d65f03c0  ret
0x0ba8f80 (0xfffffe0007a7cb90): a9bf7bfd  stp x29, x30, [sp, #0x-10]
0x0ba8f84 (0xfffffe0007a7cb94): 910003fd  add x29, sp, #0x0
0x0ba8f88 (0xfffffe0007a7cb98): 90ffb6a1  adrp x1, 0xfffffe0007150000  <-- xref
0x0ba8f8c (0xfffffe0007a7cb9c): 910e5021  add x1, x1, #0x394
0x0ba8f90 (0xfffffe0007a7cba0): d0000ea2  adrp x2, 0xfffffe0007c52000
0x0ba8f94 (0xfffffe0007a7cba4): 911e8042  add x2, x2, #0x7a0
0x0ba8f98 (0xfffffe0007a7cba8): 52804703  movz w3, #0x238
0x0ba8f9c (0xfffffe0007a7cbac): 97fba7cc  bl 0xfffffe0007966adc <__ZN11OSMetaClassC2EPKcPKS_j>
0x0ba8fa0 (0xfffffe0007a7cbb0): d0ffc188  adrp x8, 0xfffffe00072ae000
0x0ba8fa4 (0xfffffe0007a7cbb4): 91302108  add x8, x8, #0xc08
0x0ba8fa8 (0xfffffe0007a7cbb8): f9000008  str x8, [x0, #0x0]
0x0ba8fac (0xfffffe0007a7cbbc): a8c17bfd  ldp x29, x30, [sp, #0x10]
0x0ba8fb0 (0xfffffe0007a7cbc0): d65f03c0  ret
0x0ba8fb4 (0xfffffe0007a7cbc4): a9bf7bfd  stp x29, x30, [sp, #0x-10]
0x0ba8fb8 (0xfffffe0007a7cbc8): 910003fd  add x29, sp, #0x0
0x0ba8fbc (0xfffffe0007a7cbcc): 97fbb06f  bl 0xfffffe0007968d88 <__ZN8OSObjectC2EPK11OSMetaClass>
0x0ba8fc0 (0xfffffe0007a7cbd0): d0ffc188  adrp x8, 0xfffffe00072ae000
0x0ba8fc4 (0xfffffe0007a7cbd4): 912ae108  add x8, x8, #0xab8
```
- img `0x0ba9054` (`0xfffffe0007a7cc64`, `<__ZN12SweetSurface9MetaClassC2Ev+0x8>`) -> string `0x27c77c`
```asm
0x0ba9044 (0xfffffe0007a7cc54): 9100a000  add x0, x0, #0x28
0x0ba9048 (0xfffffe0007a7cc58): d65f03c0  ret
0x0ba904c (0xfffffe0007a7cc5c): a9bf7bfd  stp x29, x30, [sp, #0x-10]
0x0ba9050 (0xfffffe0007a7cc60): 910003fd  add x29, sp, #0x0
0x0ba9054 (0xfffffe0007a7cc64): 90ffb6a1  adrp x1, 0xfffffe0007150000  <-- xref
0x0ba9058 (0xfffffe0007a7cc68): 910e5021  add x1, x1, #0x394
0x0ba905c (0xfffffe0007a7cc6c): d0000ea2  adrp x2, 0xfffffe0007c52000
0x0ba9060 (0xfffffe0007a7cc70): 911e8042  add x2, x2, #0x7a0
0x0ba9064 (0xfffffe0007a7cc74): 52804703  movz w3, #0x238
0x0ba9068 (0xfffffe0007a7cc78): 97fba799  bl 0xfffffe0007966adc <__ZN11OSMetaClassC2EPKcPKS_j>
0x0ba906c (0xfffffe0007a7cc7c): d0ffc188  adrp x8, 0xfffffe00072ae000
0x0ba9070 (0xfffffe0007a7cc80): 91302108  add x8, x8, #0xc08
0x0ba9074 (0xfffffe0007a7cc84): f9000008  str x8, [x0, #0x0]
0x0ba9078 (0xfffffe0007a7cc88): a8c17bfd  ldp x29, x30, [sp, #0x10]
0x0ba907c (0xfffffe0007a7cc8c): d65f03c0  ret
0x0ba9080 (0xfffffe0007a7cc90): a9be4ff4  stp x20, x19, [sp, #0x-20]
0x0ba9084 (0xfffffe0007a7cc94): a9017bfd  stp x29, x30, [sp, #0x10]
0x0ba9088 (0xfffffe0007a7cc98): 910043fd  add x29, sp, #0x10
0x0ba908c (0xfffffe0007a7cc9c): b0ffc2c0  adrp x0, 0xfffffe00072d5000
0x0ba9090 (0xfffffe0007a7cca0): 91088000  add x0, x0, #0x220
```
- img `0x0ba9584` (`0xfffffe0007a7d194`, `<__ZN15SweetSurfaceRef9MetaClassC1Ev+0x8>`) -> string `0x27c7e3`
```asm
0x0ba9574 (0xfffffe0007a7d184): 910083ff  add sp, sp, #0x20
0x0ba9578 (0xfffffe0007a7d188): d65f03c0  ret
0x0ba957c (0xfffffe0007a7d18c): a9bf7bfd  stp x29, x30, [sp, #0x-10]
0x0ba9580 (0xfffffe0007a7d190): 910003fd  add x29, sp, #0x0
0x0ba9584 (0xfffffe0007a7d194): f0ffb681  adrp x1, 0xfffffe0007150000  <-- xref
0x0ba9588 (0xfffffe0007a7d198): 910fec21  add x1, x1, #0x3fb
0x0ba958c (0xfffffe0007a7d19c): b0000ea2  adrp x2, 0xfffffe0007c52000
0x0ba9590 (0xfffffe0007a7d1a0): 911e8042  add x2, x2, #0x7a0
0x0ba9594 (0xfffffe0007a7d1a4): 52800603  movz w3, #0x30
0x0ba9598 (0xfffffe0007a7d1a8): 97fba64d  bl 0xfffffe0007966adc <__ZN11OSMetaClassC2EPKcPKS_j>
0x0ba959c (0xfffffe0007a7d1ac): b0ffc188  adrp x8, 0xfffffe00072ae000
0x0ba95a0 (0xfffffe0007a7d1b0): 9139c108  add x8, x8, #0xe70
0x0ba95a4 (0xfffffe0007a7d1b4): f9000008  str x8, [x0, #0x0]
0x0ba95a8 (0xfffffe0007a7d1b8): a8c17bfd  ldp x29, x30, [sp, #0x10]
0x0ba95ac (0xfffffe0007a7d1bc): d65f03c0  ret
0x0ba95b0 (0xfffffe0007a7d1c0): a9bf7bfd  stp x29, x30, [sp, #0x-10]
0x0ba95b4 (0xfffffe0007a7d1c4): 910003fd  add x29, sp, #0x0
0x0ba95b8 (0xfffffe0007a7d1c8): 97fbaef0  bl 0xfffffe0007968d88 <__ZN8OSObjectC2EPK11OSMetaClass>
0x0ba95bc (0xfffffe0007a7d1cc): b0ffc188  adrp x8, 0xfffffe00072ae000
0x0ba95c0 (0xfffffe0007a7d1d0): 91348108  add x8, x8, #0xd20
```
- img `0x0ba9650` (`0xfffffe0007a7d260`, `<__ZN15SweetSurfaceRef9MetaClassC2Ev+0x8>`) -> string `0x27c7e3`
```asm
0x0ba9640 (0xfffffe0007a7d250): 91014000  add x0, x0, #0x50
0x0ba9644 (0xfffffe0007a7d254): d65f03c0  ret
0x0ba9648 (0xfffffe0007a7d258): a9bf7bfd  stp x29, x30, [sp, #0x-10]
0x0ba964c (0xfffffe0007a7d25c): 910003fd  add x29, sp, #0x0
0x0ba9650 (0xfffffe0007a7d260): f0ffb681  adrp x1, 0xfffffe0007150000  <-- xref
0x0ba9654 (0xfffffe0007a7d264): 910fec21  add x1, x1, #0x3fb
0x0ba9658 (0xfffffe0007a7d268): b0000ea2  adrp x2, 0xfffffe0007c52000
0x0ba965c (0xfffffe0007a7d26c): 911e8042  add x2, x2, #0x7a0
0x0ba9660 (0xfffffe0007a7d270): 52800603  movz w3, #0x30
0x0ba9664 (0xfffffe0007a7d274): 97fba61a  bl 0xfffffe0007966adc <__ZN11OSMetaClassC2EPKcPKS_j>
0x0ba9668 (0xfffffe0007a7d278): b0ffc188  adrp x8, 0xfffffe00072ae000
0x0ba966c (0xfffffe0007a7d27c): 9139c108  add x8, x8, #0xe70
0x0ba9670 (0xfffffe0007a7d280): f9000008  str x8, [x0, #0x0]
0x0ba9674 (0xfffffe0007a7d284): a8c17bfd  ldp x29, x30, [sp, #0x10]
0x0ba9678 (0xfffffe0007a7d288): d65f03c0  ret
0x0ba967c (0xfffffe0007a7d28c): a9be4ff4  stp x20, x19, [sp, #0x-20]
0x0ba9680 (0xfffffe0007a7d290): a9017bfd  stp x29, x30, [sp, #0x10]
0x0ba9684 (0xfffffe0007a7d294): 910043fd  add x29, sp, #0x10
0x0ba9688 (0xfffffe0007a7d298): 90ffc2c0  adrp x0, 0xfffffe00072d5000
0x0ba968c (0xfffffe0007a7d29c): 91098000  add x0, x0, #0x260
```
- img `0x0bab9f4` (`0xfffffe0007a7f604`, `<__GLOBAL__sub_I_SweetSurface.cpp+0x14>`) -> string `0x27c77c`
```asm
0x0bab9e4 (0xfffffe0007a7f5f4): a9017bfd  stp x29, x30, [sp, #0x10]
0x0bab9e8 (0xfffffe0007a7f5f8): 910043fd  add x29, sp, #0x10
0x0bab9ec (0xfffffe0007a7f5fc): d0000ee0  adrp x0, 0xfffffe0007c5d000
0x0bab9f0 (0xfffffe0007a7f600): 9100a000  add x0, x0, #0x28
0x0bab9f4 (0xfffffe0007a7f604): b0ffb681  adrp x1, 0xfffffe0007150000  <-- xref
0x0bab9f8 (0xfffffe0007a7f608): 910e5021  add x1, x1, #0x394
0x0bab9fc (0xfffffe0007a7f60c): f0000e93  adrp x19, 0xfffffe0007c52000
0x0baba00 (0xfffffe0007a7f610): 911e8273  add x19, x19, #0x7a0
0x0baba04 (0xfffffe0007a7f614): aa1303e2  mov x2, x19
0x0baba08 (0xfffffe0007a7f618): 52804703  movz w3, #0x238
0x0baba0c (0xfffffe0007a7f61c): 97fb9d30  bl 0xfffffe0007966adc <__ZN11OSMetaClassC2EPKcPKS_j>
0x0baba10 (0xfffffe0007a7f620): f0ffc168  adrp x8, 0xfffffe00072ae000
0x0baba14 (0xfffffe0007a7f624): 91302108  add x8, x8, #0xc08
0x0baba18 (0xfffffe0007a7f628): f9000008  str x8, [x0, #0x0]
0x0baba1c (0xfffffe0007a7f62c): d0000ee0  adrp x0, 0xfffffe0007c5d000
0x0baba20 (0xfffffe0007a7f630): 91014000  add x0, x0, #0x50
0x0baba24 (0xfffffe0007a7f634): b0ffb681  adrp x1, 0xfffffe0007150000
0x0baba28 (0xfffffe0007a7f638): 910fec21  add x1, x1, #0x3fb
0x0baba2c (0xfffffe0007a7f63c): aa1303e2  mov x2, x19
0x0baba30 (0xfffffe0007a7f640): 52800603  movz w3, #0x30
```
- img `0x0baba24` (`0xfffffe0007a7f634`, `<__GLOBAL__sub_I_SweetSurface.cpp+0x44>`) -> string `0x27c7e3`
```asm
0x0baba14 (0xfffffe0007a7f624): 91302108  add x8, x8, #0xc08
0x0baba18 (0xfffffe0007a7f628): f9000008  str x8, [x0, #0x0]
0x0baba1c (0xfffffe0007a7f62c): d0000ee0  adrp x0, 0xfffffe0007c5d000
0x0baba20 (0xfffffe0007a7f630): 91014000  add x0, x0, #0x50
0x0baba24 (0xfffffe0007a7f634): b0ffb681  adrp x1, 0xfffffe0007150000  <-- xref
0x0baba28 (0xfffffe0007a7f638): 910fec21  add x1, x1, #0x3fb
0x0baba2c (0xfffffe0007a7f63c): aa1303e2  mov x2, x19
0x0baba30 (0xfffffe0007a7f640): 52800603  movz w3, #0x30
0x0baba34 (0xfffffe0007a7f644): 97fb9d26  bl 0xfffffe0007966adc <__ZN11OSMetaClassC2EPKcPKS_j>
0x0baba38 (0xfffffe0007a7f648): f0ffc168  adrp x8, 0xfffffe00072ae000
0x0baba3c (0xfffffe0007a7f64c): 9139c108  add x8, x8, #0xe70
0x0baba40 (0xfffffe0007a7f650): f9000008  str x8, [x0, #0x0]
0x0baba44 (0xfffffe0007a7f654): d0000ee0  adrp x0, 0xfffffe0007c5d000
0x0baba48 (0xfffffe0007a7f658): 9101e000  add x0, x0, #0x78
0x0baba4c (0xfffffe0007a7f65c): b0ffb681  adrp x1, 0xfffffe0007150000
0x0baba50 (0xfffffe0007a7f660): 91108021  add x1, x1, #0x420
0x0baba54 (0xfffffe0007a7f664): 90000ea2  adrp x2, 0xfffffe0007c53000
0x0baba58 (0xfffffe0007a7f668): 9113a042  add x2, x2, #0x4e8
0x0baba5c (0xfffffe0007a7f66c): 52801103  movz w3, #0x88
0x0baba60 (0xfffffe0007a7f670): 97fb9d1b  bl 0xfffffe0007966adc <__ZN11OSMetaClassC2EPKcPKS_j>
```

### Framebuffer Console Flag Writers & Readers
```asm
0x059be4c (0xfffffe000746fa5c): aa1603e1  mov x1, x22  ; <_console_ring_try_empty+0x1c4>
0x059be50 (0xfffffe000746fa60): 940232b7  bl 0xfffffe00074fc53c <_sweet_log_append>  ; <_console_ring_try_empty+0x1c8>
0x059be54 (0xfffffe000746fa64): d0003d28  adrp x8, 0xfffffe0007c15000  ; <_console_ring_try_empty+0x1cc>
0x059be58 (0xfffffe000746fa68): b944c908  ldr w8, [x8, #0x4c8]  ; <_console_ring_try_empty+0x1d0>
0x059be5c (0xfffffe000746fa6c): 34000068  cbz w8, 0xfffffe000746fa78  ; <_console_ring_try_empty+0x1d4>
0x059be60 (0xfffffe000746fa70): 97fb2a8d  bl 0xfffffe000733a4a4 <_panic_active>  ; <_console_ring_try_empty+0x1d8>
0x059be64 (0xfffffe000746fa74): 34000520  cbz w0, 0xfffffe000746fb18  ; <_console_ring_try_empty+0x1dc>
0x059be68 (0xfffffe000746fa78): f0003f08  adrp x8, 0xfffffe0007c52000  ; <_console_ring_try_empty+0x1e0>
0x059be6c (0xfffffe000746fa7c): d503201f  nop  ; <_console_ring_try_empty+0x1e4>
0x059c1bc (0xfffffe000746fdcc): aa0003f4  mov x20, x0  ; <__cnputs+0x28>
0x059c1c0 (0xfffffe000746fdd0): 940231db  bl 0xfffffe00074fc53c <_sweet_log_append>  ; <__cnputs+0x2c>
0x059c1c4 (0xfffffe000746fdd4): d0003d28  adrp x8, 0xfffffe0007c15000  ; <__cnputs+0x30>
0x059c1c8 (0xfffffe000746fdd8): b944c908  ldr w8, [x8, #0x4c8]  ; <__cnputs+0x34>
0x059c1cc (0xfffffe000746fddc): 34000068  cbz w8, 0xfffffe000746fde8  ; <__cnputs+0x38>
0x059c1d0 (0xfffffe000746fde0): 97fb29b1  bl 0xfffffe000733a4a4 <_panic_active>  ; <__cnputs+0x3c>
0x059c1d4 (0xfffffe000746fde4): 34000520  cbz w0, 0xfffffe000746fe88  ; <__cnputs+0x40>
0x059c1d8 (0xfffffe000746fde8): f0003f08  adrp x8, 0xfffffe0007c52000  ; <__cnputs+0x44>
0x059c1dc (0xfffffe000746fdec): d503201f  nop  ; <__cnputs+0x48>
0x0bac834 (0xfffffe0007a80444): b81943a8  .word 0xb81943a8  ; <__ZN9AppleCLCD7presentEPKhj+0x30>
0x0bac838 (0xfffffe0007a80448): 39441008  ldrb w8, [x0, #0x104]  ; <__ZN9AppleCLCD7presentEPKhj+0x34>
0x0bac83c (0xfffffe0007a8044c): 35000208  cbnz w8, 0xfffffe0007a8048c  ; <__ZN9AppleCLCD7presentEPKhj+0x38>
0x0bac840 (0xfffffe0007a80450): b81a43bf  .word 0xb81a43bf  ; <__ZN9AppleCLCD7presentEPKhj+0x3c>
0x0bac844 (0xfffffe0007a80454): 52800028  movz w8, #0x1  ; <__ZN9AppleCLCD7presentEPKhj+0x40>
0x0bac848 (0xfffffe0007a80458): 39041268  strb w8, [x19, #0x104]  ; <__ZN9AppleCLCD7presentEPKhj+0x44>
0x0bac84c (0xfffffe0007a8045c): 90ffb680  adrp x0, 0xfffffe0007150000  ; <__ZN9AppleCLCD7presentEPKhj+0x48>
0x0bac850 (0xfffffe0007a80460): 91262400  add x0, x0, #0x989  ; <__ZN9AppleCLCD7presentEPKhj+0x4c>
0x0bac854 (0xfffffe0007a80464): d10173a1  sub x1, x29, #0x5c  ; <__ZN9AppleCLCD7presentEPKhj+0x50>
0x0bac858 (0xfffffe0007a80468): 52800082  movz w2, #0x4  ; <__ZN9AppleCLCD7presentEPKhj+0x54>
0x0bac85c (0xfffffe0007a8046c): 9400a602  bl 0xfffffe0007aa9c74 <_PE_parse_boot_argn>  ; <__ZN9AppleCLCD7presentEPKhj+0x58>
0x0bac860 (0xfffffe0007a80470): 340000e0  cbz w0, 0xfffffe0007a8048c  ; <__ZN9AppleCLCD7presentEPKhj+0x5c>
0x0bac864 (0xfffffe0007a80474): b85a43a8  .word 0xb85a43a8  ; <__ZN9AppleCLCD7presentEPKhj+0x60>
0x0bac868 (0xfffffe0007a80478): 340000a8  cbz w8, 0xfffffe0007a8048c  ; <__ZN9AppleCLCD7presentEPKhj+0x64>
0x0bac86c (0xfffffe0007a8047c): b0000ca8  adrp x8, 0xfffffe0007c15000  ; <__ZN9AppleCLCD7presentEPKhj+0x68>
0x0bac870 (0xfffffe0007a80480): d503201f  nop  ; <__ZN9AppleCLCD7presentEPKhj+0x6c>
0x0bac874 (0xfffffe0007a80484): 52800029  movz w9, #0x1  ; <__ZN9AppleCLCD7presentEPKhj+0x70>
0x0bac878 (0xfffffe0007a80488): b904c909  str w9, [x8, #0x4c8]  ; <__ZN9AppleCLCD7presentEPKhj+0x74>
0x0bac87c (0xfffffe0007a8048c): d280001b  movz x27, #0x0  ; <__ZN9AppleCLCD7presentEPKhj+0x78>
0x0bac880 (0xfffffe0007a80490): 910192a8  add x8, x21, #0x64  ; <__ZN9AppleCLCD7presentEPKhj+0x7c>
```

## 4. Muted `SWEET AKS:` and `IOK ` Log Sites (`boot-g7em-ui-fast.img`)

| Category | File Offset | Virtual Address | Original `bl _IOLog` | Patched Word | Function |
|---|---:|---|---:|---:|---|
| `SWEET AKS` | `0x0ba8354` | `0xfffffe0007a7bf64` | `0x97fd1793` | `0xd503201f` (`nop`) | `__ZN13AppleKeyStore5startEP9IOService+0x5c` |
| `SWEET AKS` | `0x0ba8678` | `0xfffffe0007a7c288` | `0x97fd16ca` | `0xd503201f` (`nop`) | `__ZN23AppleKeyStoreUserClient14externalMethodEjP25IOExternalMethodArgumentsP24IOExternalMethodDispatchP8OSObjectPv+0xf4` |
| `IOK` | `0x0b557c4` | `0xfffffe0007a293d4` | `0x97fe6277` | `0xd503201f` (`nop`) | `_internal_io_service_get_matching_services+0x180` |
| `IOK` | `0x0b557f8` | `0xfffffe0007a29408` | `0x97fe626a` | `0xd503201f` (`nop`) | `_internal_io_service_get_matching_services+0x1b4` |
| `IOK` | `0x0b55cc0` | `0xfffffe0007a298d0` | `0x97fe6138` | `0xd503201f` (`nop`) | `__ZL40internal_io_service_get_matching_serviceP8ipc_portPKcjPP8OSObject+0x158` |
| `IOK` | `0x0b55cec` | `0xfffffe0007a298fc` | `0x97fe612d` | `0xd503201f` (`nop`) | `__ZL40internal_io_service_get_matching_serviceP8ipc_portPKcjPP8OSObject+0x184` |
| `IOK` | `0x0b55fc4` | `0xfffffe0007a29bd4` | `0x97fe6077` | `0xd503201f` (`nop`) | `__ZL36internal_io_service_add_notificationP8ipc_portPcPKcmS0_PvmbPP8OSObject+0x15c` |
| `IOK` | `0x0b55ff0` | `0xfffffe0007a29c00` | `0x97fe606c` | `0xd503201f` (`nop`) | `__ZL36internal_io_service_add_notificationP8ipc_portPcPKcmS0_PvmbPP8OSObject+0x188` |
| `IOK` | `0x0b56db0` | `0xfffffe0007a2a9c0` | `0x97fe5cfc` | `0xd503201f` (`nop`) | `_is_io_registry_entry_from_path+0xac` |
| `IOK` | `0x0b5874c` | `0xfffffe0007a2c35c` | `0x97fe5695` | `0xd503201f` (`nop`) | `_is_io_registry_entry_get_child_iterator+0x128` |
| `IOK` | `0x0b58cac` | `0xfffffe0007a2c8bc` | `0x97fe553d` | `0xd503201f` (`nop`) | `_is_io_service_open_extended+0x100` |
| Header SHA-1 | `0x0000240` | `(hdr+0x240)` | `08b9b1eeecef061d53f2551691bed4a195ad78b2` | `8204a522b6a954e6061a3be25a11c01143500bdb` | Recomputed Android boot header ID |
