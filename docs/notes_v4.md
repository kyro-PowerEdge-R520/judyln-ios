# Boot Image v4 Build & Inspection Report (`boot-g7em-gpu8-v4.img`)

- Output: `work\next-gen\boot-g7em-gpu8-v4.img` (18128896 bytes, SHA-256: `8a675f4c8dcd124e9c25d870bac688a062ec7f4203de480d1adad27f3ddbce29`)
- Boot header SHA-1 ID (`0x240..0x254`): `32b56c3522d40d75d18295b7c4ec06ba3dec3555`
- Golden image verified untouched: `766a88577c208af62583d199fa5dbd8f46811342aa109db5c334a5d38607b3e7`

## Applied Patches
- `0x0c8df28` (`0xfffffe0007b61b18`): `0x97fddae1` -> `0xd503201f` (Mute repetitive matching log ('matching_size'))
- `0x0c8df48` (`0xfffffe0007b61b38`): `0x97fddad9` -> `0xd503201f` (Mute repetitive matching log ('matching_size'))
- `0x0c8df68` (`0xfffffe0007b61b58`): `0x97fddad1` -> `0xd503201f` (Mute repetitive matching log ('matching_size'))
- `0x0c8df88` (`0xfffffe0007b61b78`): `0x97fddac9` -> `0xd503201f` (Mute repetitive matching log ('matching_size'))
- `0x0b557e4` (`0xfffffe0007a293d4`): `0x97fe6277` -> `0xd503201f` (Mute repetitive matching log ('matching'))
- `0x0b55818` (`0xfffffe0007a29408`): `0x97fe626a` -> `0xd503201f` (Mute repetitive matching log ('matching'))
- `0x0c8e734` (`0xfffffe0007b62324`): `0x97fdd8de` -> `0xd503201f` (Mute repetitive matching log ('matching'))
- `0x0c91d5c` (`0xfffffe0007b6594c`): `0x97fdcb54` -> `0xd503201f` (Mute repetitive matching log ('matching'))
- `0x0c91d7c` (`0xfffffe0007b6596c`): `0x97fdcb4c` -> `0xd503201f` (Mute repetitive matching log ('matching'))
- `0x0c91dec` (`0xfffffe0007b659dc`): `0x97fdcb30` -> `0xd503201f` (Mute repetitive matching log ('matching'))
- `0x0b55ce0` (`0xfffffe0007a298d0`): `0x97fe6138` -> `0xd503201f` (Mute repetitive matching log ('matching1'))
- `0x0b55d0c` (`0xfffffe0007a298fc`): `0x97fe612d` -> `0xd503201f` (Mute repetitive matching log ('matching1'))
- `0x0c93894` (`0xfffffe0007b67484`): `0x97f96a4b` -> `0xd503201f` (Mute repetitive matching log ('SWEET CPU: cpu=%u NOT registered (IOKit matching timeout)\n'))

## g7gpu Init Block (`0x0633ab4..0x0633b50`)
```
  0x0633ab4 (0xfffffe00075076a4): b9400268  ldr w8, [x19, #0x0]
  0x0633ab8 (0xfffffe00075076a8): 340004a8  cbz w8, 0xfffffe000750773c
  0x0633abc (0xfffffe00075076ac): a9017fff  0xa9017fff
  0x0633ac0 (0xfffffe00075076b0): f90007ff  str x31, [x31, #0x8]
  0x0633ac4 (0xfffffe00075076b4): b90007ff  str w31, [x31, #0x4]
  0x0633ac8 (0xfffffe00075076b8): b0ffdc81  adrp x1, 0xfffffe0007098000
  0x0633acc (0xfffffe00075076bc): 9125f021  add x1, x1, #0x97c
  0x0633ad0 (0xfffffe00075076c0): 910043e2  add x2, x31, #0x10
  0x0633ad4 (0xfffffe00075076c4): d2800000  movz x0, #0x0, lsl #0
  0x0633ad8 (0xfffffe00075076c8): 94168786  bl 0xfffffe0007aa94e0
  0x0633adc (0xfffffe00075076cc): 7100041f  0x7100041f
  0x0633ae0 (0xfffffe00075076d0): 54000261  b.1 0xfffffe000750771c
  0x0633ae4 (0xfffffe00075076d4): f9400be0  ldr x0, [x31, #0x10]
  0x0633ae8 (0xfffffe00075076d8): b0ffdc81  adrp x1, 0xfffffe0007098000
  0x0633aec (0xfffffe00075076dc): 91263c21  add x1, x1, #0x98f
  0x0633af0 (0xfffffe00075076e0): 910023e2  add x2, x31, #0x8
  0x0633af4 (0xfffffe00075076e4): 910013e3  add x3, x31, #0x4
  0x0633af8 (0xfffffe00075076e8): 94168868  bl 0xfffffe0007aa9888
  0x0633afc (0xfffffe00075076ec): 7100041f  0x7100041f
  0x0633b00 (0xfffffe00075076f0): 54000161  b.1 0xfffffe000750771c
  0x0633b04 (0xfffffe00075076f4): b94007e8  ldr w8, [x31, #0x4]
  0x0633b08 (0xfffffe00075076f8): 7100411f  0x7100411f
  0x0633b0c (0xfffffe00075076fc): 54000101  b.1 0xfffffe000750771c
  0x0633b10 (0xfffffe0007507700): f94007e8  ldr x8, [x31, #0x8]
  0x0633b14 (0xfffffe0007507704): f9400109  ldr x9, [x8, #0x0]
  0x0633b18 (0xfffffe0007507708): d0005c0a  adrp x10, 0xfffffe0008089000
  0x0633b1c (0xfffffe000750770c): 9117014a  add x10, x10, #0x5c0
  0x0633b20 (0xfffffe0007507710): f9000149  str x9, [x10, #0x0]
  0x0633b24 (0xfffffe0007507714): f9400508  ldr x8, [x8, #0x8]
  0x0633b28 (0xfffffe0007507718): f9000548  str x8, [x10, #0x8]
  0x0633b2c (0xfffffe000750771c): 10000180  0x10000180
  0x0633b30 (0xfffffe0007507720): d503201f  0xd503201f
  0x0633b34 (0xfffffe0007507724): 910063e2  add x2, x31, #0x18
  0x0633b38 (0xfffffe0007507728): d2800001  movz x1, #0x0, lsl #0
  0x0633b3c (0xfffffe000750772c): 97fa1d97  bl 0xfffffe000738ed88
  0x0633b40 (0xfffffe0007507730): 35000060  cbnz w0, 0xfffffe000750773c
  0x0633b44 (0xfffffe0007507734): f9400fe0  ldr x0, [x31, #0x18]
  0x0633b48 (0xfffffe0007507738): 97fa166a  bl 0xfffffe000738d0e0
  0x0633b4c (0xfffffe000750773c): a9437bfd  0xa9437bfd
```

## `_g7g_bringup_thread` Post-Bringup (`0x0634cf0..0x0634d90`)
```
  0x0634cf0 (0xfffffe00075088e0): 52801409  movz w9, #0xa0, lsl #0
  0x0634cf4 (0xfffffe00075088e4): 72b00509  movk w9, #0x8028, lsl #16
  0x0634cf8 (0xfffffe00075088e8): b9002909  str w9, [x8, #0x28]
  0x0634cfc (0xfffffe00075088ec): d503339f  0xd503339f
  0x0634d00 (0xfffffe00075088f0): f9418b68  ldr x8, [x27, #0x310]
  0x0634d04 (0xfffffe00075088f4): d50332bf  0xd50332bf
  0x0634d08 (0xfffffe00075088f8): 8b080288  0x8b080288
  0x0634d0c (0xfffffe00075088fc): d1164108  0xd1164108
  0x0634d10 (0xfffffe0007508900): 52880a49  movz w9, #0x4052, lsl #0
  0x0634d14 (0xfffffe0007508904): b9000109  str w9, [x8, #0x0]
  0x0634d18 (0xfffffe0007508908): d503339f  0xd503339f
  0x0634d1c (0xfffffe000750890c): f9418b68  ldr x8, [x27, #0x310]
  0x0634d20 (0xfffffe0007508910): d50332bf  0xd50332bf
  0x0634d24 (0xfffffe0007508914): 8b080288  0x8b080288
  0x0634d28 (0xfffffe0007508918): 52804009  movz w9, #0x200, lsl #0
  0x0634d2c (0xfffffe000750891c): 72a0c069  movk w9, #0x603, lsl #16
  0x0634d30 (0xfffffe0007508920): b81c4109  0xb81c4109
  0x0634d34 (0xfffffe0007508924): d503339f  0xd503339f
  0x0634d38 (0xfffffe0007508928): f9418b68  ldr x8, [x27, #0x310]
  0x0634d3c (0xfffffe000750892c): d50332bf  0xd50332bf
  0x0634d40 (0xfffffe0007508930): 8b080288  0x8b080288
  0x0634d44 (0xfffffe0007508934): d1091108  0xd1091108
  0x0634d48 (0xfffffe0007508938): b900011f  str w31, [x8, #0x0]
  0x0634d4c (0xfffffe000750893c): d503339f  0xd503339f
  0x0634d50 (0xfffffe0007508940): f9418b68  ldr x8, [x27, #0x310]
  0x0634d54 (0xfffffe0007508944): d50332bf  0xd50332bf
  0x0634d58 (0xfffffe0007508948): 5288000c  movz w12, #0x4000, lsl #0
  0x0634d5c (0xfffffe000750894c): 72a0002c  movk w12, #0x1, lsl #16
  0x0634d60 (0xfffffe0007508950): 8b080188  0x8b080188
  0x0634d64 (0xfffffe0007508954): d13f1108  0xd13f1108
  0x0634d68 (0xfffffe0007508958): 52800029  movz w9, #0x1, lsl #0
  0x0634d6c (0xfffffe000750895c): b9000109  str w9, [x8, #0x0]
  0x0634d70 (0xfffffe0007508960): d503339f  0xd503339f
  0x0634d74 (0xfffffe0007508964): f9418b68  ldr x8, [x27, #0x310]
  0x0634d78 (0xfffffe0007508968): d50332bf  0xd50332bf
  0x0634d7c (0xfffffe000750896c): 8b080188  0x8b080188
  0x0634d80 (0xfffffe0007508970): 9281ffea  movn x10, #0xfff, lsl #0
  0x0634d84 (0xfffffe0007508974): b82a6909  0xb82a6909
  0x0634d88 (0xfffffe0007508978): d503339f  0xd503339f
  0x0634d8c (0xfffffe000750897c): f9418b68  ldr x8, [x27, #0x310]
```
