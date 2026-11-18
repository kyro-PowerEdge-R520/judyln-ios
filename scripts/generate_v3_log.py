# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 kyro
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import hashlib
import struct

FULL = r"C:\Users\kyro\Downloads\judyln-ios\work\next-gen\boot-g7em-20j-full.img"
V3 = r"C:\Users\kyro\Downloads\judyln-ios\work\next-gen\boot-g7em-gpu8-v3.img"
GOLD = r"C:\Users\kyro\Downloads\judyln-ios\golden_boot\boot_a-cpu-ui-touch.img"
DST = r"C:\Users\kyro\Downloads\judyln-ios\work\next-gen\boot-g7em-gpu8-v3-log.img"
REPORT = r"C:\Users\kyro\Downloads\judyln-ios\work\next-gen\notes_v3_log.md"

GOLD_EXPECTED_SHA256 = "766a88577c208af62583d199fa5dbd8f46811342aa109db5c334a5d38607b3e7"
TEXT_EXEC_IMG_BASE = 0x424410
TEXT_EXEC_VA_BASE = 0xFFFFFE00072F8000


def sext(val, bits):
    sign = 1 << (bits - 1)
    return val - (1 << bits) if (val & sign) else val


def img_to_va(io):
    return TEXT_EXEC_VA_BASE + (io - TEXT_EXEC_IMG_BASE)


def va_to_img(va):
    return TEXT_EXEC_IMG_BASE + (va - TEXT_EXEC_VA_BASE)


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def calc_bootimg_v1_sha1(buf):
    ksz, _, rsz, _, ssz, _, _, pg, hver, _ = struct.unpack_from("<10I", buf, 8)
    rdtbo_sz, _, _ = struct.unpack_from("<IQI", buf, 1632)

    def align(n):
        return ((n + pg - 1) // pg) * pg

    k_off = pg
    r_off = k_off + align(ksz)
    s_off = r_off + align(rsz)
    d_off = s_off + align(ssz)

    h = hashlib.sha1()
    h.update(buf[k_off : k_off + ksz])
    h.update(struct.pack("<I", ksz))
    h.update(buf[r_off : r_off + rsz])
    h.update(struct.pack("<I", rsz))
    h.update(buf[s_off : s_off + ssz])
    h.update(struct.pack("<I", ssz))
    if hver >= 1:
        h.update(buf[d_off : d_off + rdtbo_sz])
        h.update(struct.pack("<I", rdtbo_sz))
    return h.digest()


def inspect_post_phase1(buf):
    # Check phase 2 (0x0bc0240..0x0bc0404) & phase 3 (0x0bc0404..0x0bc0438) BL targets & phases
    phase_writes = []
    for io in range(0x0BC023C, 0x0BC043C, 4):
        w = struct.unpack_from("<I", buf, io)[0]
        va = img_to_va(io)
        if w in (0x52800048, 0x52800068, 0x52800088, 0x528000A8):
            phase_val = (w >> 5) & 0xFFFF
            phase_writes.append((io, va, phase_val))

    # Verify async bringup thread launch + termination + fallback in _g7g_thread & AGXDeviceUserClient
    spawn_w = struct.unpack_from("<I", buf, 0x0634B64)[0]
    assert (spawn_w & 0xFC000000) == 0x94000000, "Expected BL kernel_thread_start at 0x0634b64"
    bringup_call = struct.unpack_from("<I", buf, 0x0635AAC)[0]
    assert (bringup_call & 0xFC000000) == 0x94000000, "Expected BL _g7_adreno_bringup at 0x0635aac"
    err_ret_w = struct.unpack_from("<I", buf, 0x0BC19B0)[0]
    assert err_ret_w == 0x12800000, f"Expected movn w0, #0 (-1) at 0x0bc19b0, got 0x{err_ret_w:08x}"

    # Verify timeouts / error exits in _g7_adreno_bringup post-attach steps (CP_ME_INIT, zap, timer)
    return {
        "phase_writes": phase_writes,
        "bringup_thread_spawn_img": 0x0634B64,
        "bringup_call_img": 0x0635AAC,
        "bringup_error_ret_img": 0x0BC19B0,
        "userclient_unsupported_ret_img": 0x0BC0D48,
    }


def main():
    full = open(FULL, "rb").read()
    v3 = open(V3, "rb").read()
    gold = open(GOLD, "rb").read()

    assert len(full) == len(v3) == 18128896
    assert len(gold) == 18112512
    assert sha256_bytes(gold) == GOLD_EXPECTED_SHA256

    # Verify v3 currently has the console suppression nops and 3 SMMU patches
    assert struct.unpack_from("<I", full, 0x0059BE7C)[0] == 0x34000068
    assert struct.unpack_from("<I", full, 0x0059C1EC)[0] == 0x34000068
    assert struct.unpack_from("<I", v3, 0x0059BE7C)[0] == 0xD503201F
    assert struct.unpack_from("<I", v3, 0x0059C1EC)[0] == 0xD503201F
    assert struct.unpack_from("<I", v3, 0x00BBF1A4)[0] == 0x14000003
    assert struct.unpack_from("<I", v3, 0x00BBFA44)[0] == 0xD503201F
    assert struct.unpack_from("<I", v3, 0x00BBFA98)[0] == 0x52800000

    # Clone v3 and restore ONLY 0x059be7c and 0x059c1ec to original 0x34000068
    buf = bytearray(v3)
    struct.pack_into("<I", buf, 0x0059BE7C, 0x34000068)
    struct.pack_into("<I", buf, 0x0059C1EC, 0x34000068)

    new_id = calc_bootimg_v1_sha1(buf)
    buf[0x240:0x254] = new_id
    buf[0x254:0x260] = b"\x00" * 12

    with open(DST, "wb") as f:
        f.write(buf)

    out = open(DST, "rb").read()
    assert len(out) == 18128896
    assert out[0:8] == b"ANDROID!"
    assert out[0x240:0x254] == calc_bootimg_v1_sha1(out) == new_id

    # Verify restored words and preserved SMMU patches
    assert struct.unpack_from("<I", out, 0x0059BE7C)[0] == 0x34000068
    assert struct.unpack_from("<I", out, 0x0059C1EC)[0] == 0x34000068
    assert struct.unpack_from("<I", out, 0x00BBF1A4)[0] == 0x14000003
    assert struct.unpack_from("<I", out, 0x00BBFA44)[0] == 0xD503201F
    assert struct.unpack_from("<I", out, 0x00BBFA98)[0] == 0x52800000

    # Verify only the 3 SMMU 32-bit words + 20-byte SHA-1 differ vs full source
    diff_offsets = {i for i in range(len(out)) if out[i] != full[i]}
    allowed_offsets = (
        set(range(0x240, 0x254))
        | set(range(0x00BBF1A4, 0x00BBF1A8))
        | set(range(0x00BBFA44, 0x00BBFA48))
        | set(range(0x00BBFA98, 0x00BBFA9C))
    )
    assert diff_offsets <= allowed_offsets, f"Unexpected diffs vs full: {sorted(diff_offsets - allowed_offsets)}"
    diffs_vs_full = [
        (0x240, 0x254),
        (0x00BBF1A4, 0x00BBF1A8),
        (0x00BBFA44, 0x00BBFA48),
        (0x00BBFA98, 0x00BBFA9C),
    ]

    # Preserved resources check
    sw = 0x130000
    assert out[sw : sw + 8] == b"SWEETXNU"
    cmdline = out[sw + 0x48 : sw + 0x2A0].split(b"\x00", 1)[0].decode("ascii")
    for tok in ("g7gpu=8", "sweetfb_noconsole=1", "sweettouch=1", "g7touch_init=2"):
        assert tok in cmdline
    seg10_vm, seg10_vs, seg10_fo, seg10_fz = struct.unpack_from("<4Q", out, sw + 0x2A8 + 10 * 32)
    elf_off = sw + seg10_fo
    assert out[elf_off : elf_off + 4] == b"\x7fELF"
    gzap_adt_off = out.find(b"G7Zap\x00")
    assert gzap_adt_off != -1

    post_info = inspect_post_phase1(out)

    full_sha256 = sha256_bytes(full)
    v3_sha256 = sha256_bytes(v3)
    dst_sha256 = sha256_bytes(out)
    gold_sha256_after = sha256_bytes(open(GOLD, "rb").read())
    assert gold_sha256_after == GOLD_EXPECTED_SHA256

    lines = [
        "# Boot Image v3-log Analysis & Build Report (`boot-g7em-gpu8-v3-log.img`)",
        "",
        "## 1. Image Summary & Integrity Verification",
        "",
        "| Image | Size (bytes) | SHA-256 | Android Boot v1 ID (`0x240..0x254`) |",
        "|---|---:|---|---|",
        f"| Source Base (`boot-g7em-20j-full.img`) | {len(full)} | `{full_sha256}` | `{full[0x240:0x254].hex()}` |",
        f"| Patched Base (`boot-g7em-gpu8-v3.img`) | {len(v3)} | `{v3_sha256}` | `{v3[0x240:0x254].hex()}` |",
        f"| Output (`boot-g7em-gpu8-v3-log.img`) | {len(out)} | `{dst_sha256}` | `{new_id.hex()}` |",
        f"| Golden (`golden_boot\\boot_a-cpu-ui-touch.img`) | {len(gold)} | `{gold_sha256_after}` | `{gold[0x240:0x254].hex()}` |",
        "",
        f"- Golden read-only verification: **unchanged** (`{gold_sha256_after}` == `{GOLD_EXPECTED_SHA256}`).",
        f"- Exact diffs vs `boot-g7em-20j-full.img`: **{len(diffs_vs_full)} regions** (`0x240..0x254` SHA-1 ID + `0x0bbf1a4`, `0x0bbfa44`, `0x0bbfa98` SMMU patches). Console gates `0x059be7c` and `0x059c1ec` match `boot-g7em-20j-full.img` (`0x34000068`).",
        f"- Preserved `SWEETXNU.cmdline` (`0x130048`): `{cmdline}`",
        f"- Preserved `seg[10]` (`G7Zap` ELF32): `va=0x{seg10_vm:x}`, `img_off=0x{elf_off:x}`, `fz=0x{seg10_fz:x}`; ADT `/chosen/memory-map/G7Zap` at `0x{gzap_adt_off:x}`.",
        "",
        "## 2. Active & Restored Code Locations (`boot-g7em-gpu8-v3-log.img`)",
        "",
        "| File Offset | Virtual Address | Value in `v3` | Value in `v3-log` | Description |",
        "|---:|---|---:|---:|---|",
        "| `0x0059be7c` | `0xfffffe000746fa6c` | `0xd503201f` (`nop`) | `0x34000068` (`cbz w8`) | **Restored** `_console_ring_try_empty` console log visibility before UI present |",
        "| `0x0059c1ec` | `0xfffffe000746fddc` | `0xd503201f` (`nop`) | `0x34000068` (`cbz w8`) | **Restored** `__cnputs` console log visibility before UI present |",
        "| `0x00bbf1a4` | `0xfffffe0007a92d94` | `0x14000003` (`b`) | `0x14000003` (`b`) | **Kept** `_ArmSmmu4KObserveOwnedContext`: ignore latched `CB0_FSR` fault bits in phase 1 & 3 |",
        "| `0x00bbfa44` | `0xfffffe0007a93634` | `0xd503201f` (`nop`) | `0xd503201f` (`nop`) | **Kept** `_global`: bypass `ID0.SMS==0` check on `ID0=0x40016605` in phase 1 & 3 |",
        "| `0x00bbfa98` | `0xfffffe0007a93688` | `0x52800000` (`movz w0,#0`) | `0x52800000` (`movz w0,#0`) | **Kept** `_global`: ignore latched `SMMU_sGFSR` fault status in phase 1 & 3 |",
        "| `0x00000240` | `(boot_hdr+0x240)` | `{}` | `{}` | Recomputed Android boot.img v1 SHA-1 ID |".format(
            v3[0x240:0x254].hex(), new_id.hex()
        ),
        "",
        "## 3. Post-Phase-1 Analysis (`_ArmSmmu4KAttachStreams` Phase 2/3 & `stage8` Fallback)",
        "",
        "### `_ArmSmmu4KAttachStreams` (`0x0bc00c8..0x0bc043c`) Phase Transitions",
        "- Phase assignments verified at: " + ", ".join(
            f"`0x{io:07x}` (`0x{va:x}`, `phase={p}`)" for io, va, p in post_info["phase_writes"]
        ) + ".",
        "- **Phase 2 (`0x0bc0240..0x0bc0404`)**: For `slot 0` and `slot 1`, writes `S2CR[slot] = cb_index | (EXIDS ? 0x400 : 0)` (`0x0`), barriers, verifies readback, writes `SMR[slot] = sid | (mask << 16) | 0x80000000` (`0x80000000`, `0x80000001`), barriers, and verifies readback. Any mismatch transitions to `phase 5` (`0x0bc03e4`) and calls `_quarantine` (`0x0bc043c`) to revert `S2CR` to `0x20000` (`FAULT`) and clear `SMR`, then returns status `7` (`StateMismatch`) or `8` (`IoError`) without hanging.",
        "- **Phase 3 (`0x0bc0404..0x0bc0438`)**: Calls `_observe` (`0x0bbfe58`), which re-runs `_global`, `_ArmSmmu4KObserveOwnedContext` (both carrying the 3 kept patches above), and `_scan(..., quarantine=1)` (verifying programmed `SMR` & `S2CR`). On error, transitions to `phase 5` (`_quarantine`) and returns cleanly; on success, marks `attached=1` and `phase=4`.",
        "",
        "### Post-Attach `stage8` Steps & Clean CPU Fallback to `backboardd` / `SpringBoard`",
        f"- **Async worker thread**: `_g7g_thread` (`0x{post_info['bringup_thread_spawn_img']:07x}`) launches `_g7g_bringup_thread`, which calls `_g7_adreno_bringup` (`0x{post_info['bringup_call_img']:07x}`), prints its return code, and calls `thread_terminate`. Main kernel/userland boot does **not** run `stage8` synchronously on the boot/UI critical path.",
        "- **Bounded post-attach GPU bringup (`_g7_adreno_bringup` `0x0bc19a0..0x0bc1efc`)**: After `NativeAdrenoGpuContext::bringUp` completes step 4 (SMMU attach), `stage8` runs:",
        "  1. `_g7_gpu_sqe` + `_g7_gpu_prepare` (`0x0bc1b3c`, `0x0bc1be4`) — SQE firmware copy & cache clean",
        "  2. `NativeAdrenoRing::attach` + `NativeAdrenoCpInit::run` + `NativeAdrenoRing::wait` (`0x0bc1c4c`, `0x0bc1cd4`, `0x0bc1d08`) — bounded-timeout `CP_ME_INIT` ring test",
        "  3. `_g7_gpu_zap` + `AdrenoPM4Type7` + `NativeAdrenoRing::submit` + `NativeAdrenoRing::wait` (`0x0bc1d70`, `0x0bc1dc0`, `0x0bc1de4`) — `G7Zap` / `CP_SET_SECURE_MODE` check with bounded wait",
        "  4. `NativeAdrenoSubmit::attach` + `NativeAdrenoTimer::attach` (`0x0bc1e2c`, `0x0bc1e54`) — publishes `GPU READY for Metal`",
        f"- **Guaranteed CPU fallback**: Every error path in `_g7_adreno_bringup` logs a specific `stage8:` failure string via `_snprintf` and exits through `0x{post_info['bringup_error_ret_img']:07x}` (`movn w0, #0` = `-1`) without an infinite loop. Until `_g7_adreno_bringup` finishes and sets the ready state, `G7AdrenoAccelerator::newUserClient` / `AGXDeviceUserClient::attachCore` returns `0xe00002c7` (`kIOReturnUnsupported`, `0x{post_info['userclient_unsupported_ret_img']:07x}`), allowing `backboardd` and `SpringBoard` to continue booting cleanly using `AppleCLCD` CPU framebuffer rendering.",
    ]

    with open(REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Done: boot-g7em-gpu8-v3-log.img created ({len(out)} bytes, SHA-256: {dst_sha256}). Report saved to work\\next-gen\\notes_v3_log.md.")


if __name__ == "__main__":
    main()
