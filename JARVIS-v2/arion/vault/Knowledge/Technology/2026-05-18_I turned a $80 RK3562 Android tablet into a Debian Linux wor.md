---
title: "I turned a $80 RK3562 Android tablet into a Debian Linux workstation"
source: https://github.com/tech4bot/rk3562deb
date: 2026-05-18
tags:
  - news
  - auto-learning
  - auto-injected
---

# I turned a $80 RK3562 Android tablet into a Debian Linux workstation

Current public build (pre-release, May 14, 2026):
- Release page: tech4bot/rk3562deb prerelease-14052026
- Direct image download: rk3562-debian.img.xz
- Video demo: YouTube
Run full Debian 12 Bookworm on your Doogee U10 tablet — no bootloader unlock required. Boot from SD card, remove it to return to stock Android. No changes to internal storage.
Reverse engineered from scratch — no BSP, no vendor documentation, no official support. Built with the help of Claude, Codex, and Antigravity (Google Gemini), using Firefly RK3562 open-source repositories as a starting point.
rkdebian is a build system that produces a complete, bootable Debian 12 Bookworm image for the Doogee U10 Android tablet, powered by the Rockchip RK3562 SoC.
The resulting image is written to an SD card. Insert it and power on — the tablet boots Debian. Remove the SD card and it boots Android from internal eMMC as normal.
| Component | Details |
|---|---|
| SoC | Rockchip RK3562 (4× Cortex-A53 @ 2.0 GHz) |
| NPU | 1× Rockchip NPU core (active for RKLLM inference) |
| RAM | 4 GB LPDDR4 |
| Storage | 128 GB eMMC (Android) + SD card (Debian) |
| Display | 10.1" DSI panel, 1280×800 |
| PMIC | RK817 |
| Feature | Status |
|---|---|
| Display / Panel | ✅ Full |
| Touchscreen | ✅ Full (gsl3673, 10-point multitouch) |
| Wi-Fi | ✅ Full (Seekwave EA6621Q) |
| Bluetooth | ✅ Full |
| Speaker / Audio output | ✅ Full |
| Microphone | ✅ Full |
| 3D Acceleration | |
| NPU (RKLLM / rknn-llm) | ✅ Active (RK3562 supports one NPU core, num_npu_core=1 ) |
| Accelerometer | ✅ Full (SC7A20 / DA223) |
| Flashlight (rear LED) | ✅ Full (native Phosh top-menu torch toggle + brightness control via rk-flashlightctl ) |
| Power button behavior | ✅ Full (short press sleeps on release, long press >=3s opens shutdown dialog) |
| Lockscreen orientation memory | ✅ Full (lock screen keeps last tablet orientation, including landscape) |
| Cameras | s5k5e8 + rear s5k4h5yb pipelines functional; color tuning still needs calibration) |
| Battery / Charging | ✅ Full (RK817 PMIC) |
| SD card boot | ✅ Full |
| USB OTG | ✅ Full |
| App | Notes |
|---|---|
| Firefox ESR | Preinstalled web browser |
| Chromium | Preinstalled web browser (installed when available on mirror) |
| FreeTube | Installed via Flatpak from Flathub by default (disable with RKDEBIAN_PREINSTALL_FREETUBE=0 for smaller images) |
| Drawing | Touch-friendly paint app (installed when available on mirror) |
| Snapshot | Camera app (installed when available on mirror) |
| Dolphin | File manager |
| Plasma Discover | App store / software center |
| Okular | Document/PDF viewer |
| Gedit | Text editor |
| Pavucontrol | Audio controls |
| Terminal | kgx preferred, gnome-terminal fallback |
| Flatpak + Flathub | Enabled by default for app installs |
This tablet image supports local LLM inference on the RK3562 NPU using Rockchip's RKLLM stack.
- airockchip/rknn-llm — runtime, RKLLM toolkit, demo app (
llm_demo
) - airockchip/rknn-toolkit2 — RKNN conversion/toolchain dependency used by RKLLM workflows
- Target platform:
rk3562
- Quantization:
W8A8
- NPU cores:
num_npu_core=1
(RK3562 supports one NPU core) - Optimization level:
0
(chosen for compatibility/stability on this board)
Example conversion command (host PC):
python3 convert_qwen_rk3562.py \
--model-dir ./models/Qwen3-0.6B \
--target-platform rk3562 \
--quantized-dtype W8A8 \
--optimization-level 0 \
--num-npu-core 1 \
--output ./out/Qwen3-0.6B_W8A8_RK3562_opt0.rkllm
Measured on April 6, 2026 on <tablet-ip>
with:
- prompt:
Output exactly 300 English words about arithmetic speed testing do not include punctuation and do not stop early
MAX_NEW_TOKENS=64
,MAX_CONTEXT_LEN=1024
- runner:
~/npu-test/xcompile/demo_Linux_aarch64/run_llm_rk3562.sh
Commands used:
# Qwen3-0.6B (first run includes fix_freq)
USE_FIX_FREQ=1 RKLLM_LOG_LEVEL=1 PROMPT="Output exactly 300 English words about arithmetic speed testing do not include punctuation and do not stop early" \
./run_llm_rk3562.sh ~/npu-test/models/Qwen3-0.6B_W8A8_RK3562_opt0.rkllm 64 1024
# Qwen2.5-1.5B
USE_FIX_FREQ=0 RKLLM_LOG_LEVEL=1 PROMPT="Output exactly 300 English words about arithmetic speed testing do not include punctuation and do not stop early" \
./run_llm_rk3562.sh ~/npu-test/models/Qwen2.5-1.5B-Instruct_W8A8_RK3562.rkllm 64 1024
Warm-run average (runs 2-3):
| Model | Init Time (ms) | Prefill (tok/s) | Generate (tok/s) |
|---|---|---|---|
Qwen3-0.6B_W8A8_RK3562_opt0 |
1788.70 |
57.62 |
4.92 |
Qwen2.5-1.5B-Instruct_W8A8_RK3562 |
4800.76 |
42.78 |
2.18 |
Result: Qwen3-0.6B
is significantly faster on this RK3562 tablet for local NPU inference.
- Battery may report
0%
after the tablet has been powered off for a couple of hours. rk-battery-gauge-fix.service
fixes this on boot.- If the tablet did not fully power off, reboot once; on the next boot the battery level should be corrected.
- Front (
s5k5e8
) and rear (s5k4h5yb
) camera preview/capture are functional, but colors are still slightly off and require additional ISP calibr

---
*Synthesized by AutonomousLearner*
