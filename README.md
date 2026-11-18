# judyln-ios

Original helper scripts, binary analysis/patching utilities, device configs, and technical notes for experimenting with XNU/iOS bring-up on the LG G7 ThinQ (`LMG710EM` / `judyln`, Qualcomm SDM845).

> **Note:** This repository contains **only** original scripts, non-proprietary device configuration files, and documentation. Proprietary firmware blobs, boot images, IPSWs, KDZs, and device partition dumps are strictly excluded.

## Repository Structure

- `scripts/` — Original Python and shell utilities (`extract_and_sparse.py`, `make_sparse.py`, `patch_gpt.py`, boot image patchers/auditors, and `pull-firmware.sh`).
- `scripts/work/` — Diagnostic and ADT/console analysis helper scripts.
- `scripts/third_party/` — Upstream build helper scripts retaining their original copyright and license headers.
- `configs/` — Non-proprietary `judyln` device configuration fragments (`device.conf`, `soc.args`, `judyln.conf`, `judyln.config`, `judyln_defconfig`).
- `docs/` — Technical write-ups, partition/GPT notes, USB/UI diagnostics, and SMMU bring-up reports.

## Upstream Repositories & Credits

This work builds on and references the following upstream open-source projects:

- **HakiOS (`hakios-xnu-kernel`):** [oosexgang/hakios-xnu-kernel](https://github.com/oosexgang/hakios-xnu-kernel)
- **ios-sweet (`SWEETXNU`):** [dipa-studio/ios-sweet](https://github.com/dipa-studio/ios-sweet)
- **Apple OSS Distributions (`xnu`):** [apple-oss-distributions/xnu](https://github.com/apple-oss-distributions/xnu)

See [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) for upstream attributions and license information.

## License

Original scripts and utilities in this repository are licensed under the **GNU General Public License v3.0 or later** (`GPL-3.0-or-later`). See [`LICENSE`](LICENSE) for the full text.
<img width="3072" height="4096" alt="20261115_192106_233" src="https://github.com/user-attachments/assets/a0f4ba87-4af2-4c7a-a95a-00bdbb740869" />
https://cdn.discordapp.com/attachments/1570571177179480206/1571728618822836286/f15c853a417242c2b9ac10939a106282.mov?ex=6aff1598&is=6afdc418&hm=6b34ad60a3742fd2dbd27a423afa8b09e39f154cca7c8c2dcd8b335cb105e329&
