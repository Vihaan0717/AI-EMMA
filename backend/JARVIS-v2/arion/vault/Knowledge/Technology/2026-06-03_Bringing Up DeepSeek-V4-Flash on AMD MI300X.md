---
title: "Bringing Up DeepSeek-V4-Flash on AMD MI300X"
source: https://fergusfinn.com/blog/deepseek-v4-flash-mi300x/
date: 2026-06-03
tags:
  - news
  - auto-learning
  - auto-injected
---

# Bringing Up DeepSeek-V4-Flash on AMD MI300X

Bringing up DeepSeek-V4-Flash on AMD MI300X
At Doubleword we are building an inference cloud designed for volume. To do that we have to reckon with the enveloping compute shortage.
AMD’s MI300X launched in December 20231.At AMD’s “Advancing AI” event, 6 December 2023. as AMD’s response to NVIDIA’s H100, arriving alongside H200 in the same generation. It is an odd duck in the world of high-end AI accelerators. While H100 prices are climbing (up 40% in five months on one-year rentals, with on-demand capacity sold out across every major NVIDIA part2.SemiAnalysis, The Great GPU Shortage: Rental Capacity, April 2026.), MI300X is perhaps still underappreciated. 192GB of HBM3 per card against the H100’s 80GB, comparable FP8 compute, list price roughly half. Yet you can rent one on-demand today (from Hotaisle, for instance) for noticeably less than the equivalent NVIDIA capacity.
The reason is software. The problems with running AI workloads on AMD have been written about elsewhere exhaustively, and there are signs the gap is closing on AMD’s newer chips3.SemiAnalysis’s InferenceX dashboard tracks the latest AMD parts (MI350X, MI355X) against current NVIDIA generations.. That new focus on software hasn’t extended back to old parts. As of early May 2026, running vLLM with DeepSeek-V4-Flash on MI300X just doesn’t work.
On paper MI300X is an excellent accelerator. We want it to work. This post is a worklog of all the sharp edges and winding paths we found when we tried to get it working.
The MI300X was part of the accelerator generation that kicked off the march toward lower bitwidths. LLM weights, and to a lesser extent activations and KV caches, are less sensitive to numerical imprecision than typical HPC workloads, so the Hopper generation of NVIDIA chips and the first Instinct chips added hardware support for sub-16-bit precision for the first time. The result is twice as many FLOPs applied to workloads that correspondingly transfer half as much data.
The problem is that there was disagreement on the best way to build an FP8 datatype. Graphcore and AMD proposed one standard in a 2022 preprint, backed by Qualcomm. Arm, Intel, and NVIDIA proposed another through the Open Compute Project. In a rehash of some of the forks in the road that led to IEEE 7544.This interview with William Kahan is great read for how an arithmetic standard actually gets made, including which arguments win and which are forgotten., different providers built in different and incompatible behaviours.
Perhaps unsurprisingly given the list of backers on each side, the
AMD / Graphcore standard didn’t make it. AMD’s newer MI325, MI350, and
MI355X chips all moved over to OCP-standard FP8. But MI300X still only
works in the fnuz
dialect5.fnuz
means “finite, nans, unsigned zero”, i.e. no -0
and no
inf
. These seem like sensible things to cut out for AI workloads at
small floating-point range, where every bit matters, but the dialect
never quite took off, and later AMD generations went back to the more
normal-looking FP8., so the initial vLLM work that went into
bringing up DeepSeek on AMD didn’t actually work for bringing DeepSeek
up on MI300X.
Lots of vLLM’s FP8 paths are aware of e4m3
versus e5m2
but not of
fnuz
versus OCP. The two share their bit layout but differ in exponent
bias by one, so the same byte read as the wrong dialect comes back off
by exactly a factor of two. MI300X is the only major accelerator where
that distinction matters in practice6.Throughout, we’ll note the relevant commits from the demo PRs in a public vLLM repo we put up for this post. 236de4e64
makes the
DeepSeek v4 compressor and fused compress / quant / cache writes use the
platform FP8 dtype so scales and cache bytes agree, and
bd06e5d87
routes the
sliding-window K-cache through a fnuz-aware fused quantise-and-insert helper..
DeepSeek v4’s attention is sparse. Each query attends to a top-k subset of the KV cache picked by a learned indexer, with sliding-window context handled separately.
It’s got a lot of moving pieces: KV compression, the indexer, the sliding-window path, FP8 caches feeding each. In a production deployment for maximum performance, each piece needs special attention (no pun intended) in the form of a tuned kernel.
The source of fast tuned kernels on AMD is AITER. AITER is AMD’s tuned-kernel library, roughly the analog of what NVIDIA users get from cuBLAS, cuDNN, FlashAttention, and Transformer Engine combined. vLLM falls back to generic Triton when AITER doesn’t have a path for a given shape, and generic Triton attention is several times slower than a tuned kernel. AITER’s coverage for DSV4 is uneven, and what coverage exists tends to target later AMD parts (CDNA4) rather than the CDNA3 (gfx942) cores in MI300X.
The fallout from this has two different shapes. Some pieces are missing AITER paths
entirely on gfx942: paged MQA logits, sparse MLA prefill, sparse MLA
decode. For each we need to put in a ROCm-specific helper that calls into AITER
where it exis

---
*Synthesized by AutonomousLearner*
