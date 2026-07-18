---
title: "BitsMoE: Efficient Spectral Energy-Guided Bit Allocation for MoE LLM Quantization"
source: https://arxiv.org/abs/2606.00079
date: 2026-06-03
tags:
  - news
  - auto-learning
  - auto-injected
---

# BitsMoE: Efficient Spectral Energy-Guided Bit Allocation for MoE LLM Quantization

Computer Science > Machine Learning
Title:BitsMoE: Efficient Spectral Energy-Guided Bit Allocation for MoE LLM Quantization
View PDF HTML (experimental)Abstract:Mixture-of-Experts (MoE) large language models reduce per-token computation through sparse expert activation, but their deployment remains memory-intensive because all expert weights must be kept resident in memory. Existing MoE compression methods struggle in the ultra-low-bit regime: pruning irreversibly removes model capacity, while coarse-grained quantization fails to allocate bits according to heterogeneous expert and weight-direction importance. We propose BitsMoE, a spectral-energy-guided bit-allocation framework for MoE LLM quantization. BitsMoE decomposes each MoE layer by SVD into a shared basis and expert-specific spectral factors, retaining the shared basis without quantization to preserve common cross-expert structure and using the expert-specific factors as fine-grained quantization units. To determine the bit-width of each unit, BitsMoE formulates spectrum-wise mixed-precision quantization as an activation-aware reconstruction surrogate and solves an integer linear program that minimizes estimated reconstruction loss under a fixed bit budget. Experiments across multiple MoE LLMs show that BitsMoE substantially reduces downstream task accuracy degradation in ultra-low-bit regimes. Under 2-bit quantization on Qwen3-30B-A3B-Base, BitsMoE accelerates quantization by 12.3$\times$, improves average accuracy by 27.83 percentage points, and increases decoding speed by 1.76$\times$ over GPTQ. Our model and code are publicly available at this https URL.
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
