# keybagd stage: boot-args revert and keybag audit

## 1. boot.img patch (`out-judyln/shim-boot-g7daily7-g710em.img`)
- Removed `ufscache=1 ufswait=1` from `SWEETXNU.cmdline` (`0x132048`, 608 bytes, NUL-padded).
- Kept: `g7gpu=0`, `sweetfb_noconsole=1`, `mem_size`/`dram-size` = `0x7e0c0000`, ADT `b'nram\x00'` at `0x1147000`.
- New cmdline:
  `debug=0xc serial=3 keepsyms=1 -enable_kprintf_spam -noprogress rd=ufsroot0 unentitled_ios_sim_launch=1 ignition_level=1 wdt_test=no_user_checkin ufsrw=1 rootrw=1 launchd_unsecure_cache=1 wdt=-1 sweetfb_noconsole=1 sweetfb_hz=60 sweettouch=0 sweetsample=backboardd,SpringBoard g7touch_bar=0 g7touch_init=2 sweetusb=0 cpus=8 sweetsmp=1 g7perf=100 sweetbattery=2 g7gpu=0`
- v1 SHA-1 `id` at `0x240`: `b438fc08…` -> `91f860d7b64cf3a05264b25bc7a8c78660bb4634` (+12 zero bytes).
- Image SHA-256: `0bf18b587cc7b891dabe67cbeee6882bef99280923a9c8ff0e6932b48764956d`. Flashed to `boot_a`; readback SHA-256 matches.

## 2. `0069-sweet-ufs-faster.patch` side effects
- `ufscache=1`: outgoing UTRD/UCD/PRDT and write bounce buffers are only cleaned, not invalidated; after a command only `ucd.resp` is invalidated and write bounce buffers are skipped. That is coherent as written, but it is new on this target.
- `ufswait=1`: after a 50 us spin, the command thread sleeps in 200 us steps while it still holds slot 0 and the bounce buffer.
- Reverted to the original `daily7` behavior as requested.

## 3. Live SWEETLOG of the last boot (`work/sweet-console3.txt`): keybagd did not hang
- `exec keybagd` was logged at `16:00:41.018`. keybagd then logged `MKB_INIT: System Keybag loaded`, `DONE MKB_INIT`, and launchd moved on to `usermanagerd` (`16:02:24.14`) and `dirs_cleaner` (`16:02:24.35`).
- AppleKeyStore calls returned success: `sel 0 -> 0x0`, `sel 14 -> 0x0` x2.
- The log ends during `dirs_cleaner`, with hardware key presses (VolDown, Power) that rebooted the device into recovery.
- The ~100 s gap appears in launchd wall-clock time (`16:00:41` -> `16:02:24`). The same jump appears in the earlier capture (`16:00:42` -> `16:02:11`).

## 4. `/private/var/keybags/` on live `userdata` (`sda26`): not deleted
- Read from the HFSX catalog (extent 4, leaf block 1763353) and from the latest active journal transaction (block 1763352):
  - `systembag.kb` (227 B): created by `mkiosroot.sh`. It is the plain-plist bag that keybagd loads, so deleting it would break `MKB_INIT`.
  - `persona.kb` (1439 B) and `usersession.kb` (945 B): fully allocated, written by usermanagerd and keybagd on an earlier boot. The last boot reads them without error.
  - `backup/`: empty directory (valence 0).
- No partially written or orphaned keybag files were found.
- Deletion was also not possible safely:
  - The recovery kernel has no `hfsplus` filesystem (`/proc/filesystems`).
  - The volume is mounted-dirty with a non-empty journal (`start=0x727c00`, `end=0x770c00`; 5 transactions touching catalog blocks 1763352/1763356). Any raw catalog edit would be overwritten by the next XNU journal replay.

## 5. Next capture
- Let the device run at least 5 minutes without pressing keys. Then pull SWEETLOG (`tools/sweet-log-pull.sh`) and look for `launchd_cache_loader`, `exec backboardd`, `SWEET FB: ... notifications` and `SMP backboardd` samples.
