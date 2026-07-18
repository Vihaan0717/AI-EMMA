---
title: "Launch HN: General Instinct (YC P26) – Frontier models on edge devices"
source: https://news.ycombinator.com/item?id=48414869
date: 2026-06-06
tags:
  - news
  - auto-learning
  - auto-injected
---

# Launch HN: General Instinct (YC P26) – Frontier models on edge devices

Hey HN, Guanming and Bill here from General Instinct (
https://general-instinct.com/).
After years of working in robotics, we kept running into the same problem: the best models never fit the hardware we actually had available.
The models that performed best were usually designed around datacenter assumptions: large GPUs, lots of memory bandwidth, and reliable network access. But most physical systems have the opposite constraints.
That led us down the path of figuring out how much of a frontier model could be preserved while still making it practical to run on edge hardware.
As part of that work, we recently open sourced InstinctRazor (https://github.com/General-Instinct/InstinctRazor)
One result we're excited about is compressing Qwen3.5-122B-A10B, a roughly 245 GB BF16 MoE model, into a 48 GiB GGUF. The resulting model is actually smaller than Gemma-4-26B-A4B while outperforming it on benchmarks like MMLU-Pro and GPQA-D etc. we preserve the parts that are always active (router, norms, Gated-DeltaNet/SSM layers, vision pathway, etc.) and quantize the routed experts much more aggressively. We then use on-policy distillation to recover capability lost during quantization.
The model can also run in a "small GPU" configuration where experts are streamed from system RAM. With an 8k context window, peak VRAM usage is around 7.6–8 GB.
If you're interested in the technical details, we wrote up the approach here (https://general-instinct.com/blog/frontier-moe-sub-4-bit)
We're especially interested in hearing from people deploying models onto robots or other edge devices. What models are you trying to run locally today? What has been the biggest bottleneck in getting them into production?

---
*Synthesized by AutonomousLearner*
