---
title: "GQLA: Group-Query Latent Attention for Hardware-Adaptive Large Language Model Decoding"
source: https://arxiv.org/abs/2605.15250
date: 2026-05-18
tags:
  - news
  - auto-learning
  - auto-injected
---

# GQLA: Group-Query Latent Attention for Hardware-Adaptive Large Language Model Decoding

Computer Science > Machine Learning
Title:GQLA: Group-Query Latent Attention for Hardware-Adaptive Large Language Model Decoding
View PDF HTML (experimental)Abstract:Multi-head Latent Attention (MLA), the attention used in DeepSeek-V2/V3, jointly compresses keys and values into a low-rank latent and matches the H100 roofline almost perfectly. Its trained weights, however, expose only one decoding path - an absorbed MQA form - which ties efficient inference to H100-class compute-bandwidth ratios, forfeits tensor parallelism along the head axis, and yields no Multi-Token Prediction (MTP) gain on commodity inference GPUs such as the export-restricted H20. We propose Group-Query Latent Attention (GQLA), a minimal modification of MLA whose trained weights expose two algebraically equivalent decoding paths over the same parameters: an MQA-absorb path identical to MLA's, and a GQA path with a per-group expanded cache. The runtime picks the path that matches the target hardware - no retraining, no custom kernels - so a single set of GQLA weights pins the rooflines of both H100 (MQA-absorb, s_q=1) and H20 (GQA + MTP, s_q=2), while supporting up to 8-way zero-redundancy tensor parallelism on the GQA path. To avoid pretraining from scratch we extend TransMLA into TransGQLA, which converts a pretrained GQA checkpoint into a GQLA model; on LLaMA-3-8B it compresses the per-token KV cache to 28.125% of the GQA baseline on the MQA-absorb path while structurally preserving GQA-level traffic on the per-group path.
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
