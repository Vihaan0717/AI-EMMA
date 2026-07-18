---
title: "GITCO: Gated Inference-Time Context Optimization in TSFMs"
source: https://arxiv.org/abs/2606.05332
date: 2026-06-06
tags:
  - news
  - auto-learning
  - auto-injected
---

# GITCO: Gated Inference-Time Context Optimization in TSFMs

Computer Science > Artificial Intelligence
Title:GITCO: Gated Inference-Time Context Optimization in TSFMs
View PDF HTML (experimental)Abstract:Patch-based Time Series Foundation Models (TSFMs) suffer from context poisoning: structurally anomalous patches capture disproportionate attention and silently degrade zero-shot forecast quality. We propose improving TSFM accuracy at inference time by optimizing the input context rather than modifying model weights. We present GITCO (Gated Inference-Time Context Optimization), a lightweight three-component framework: Gate, Router, and Critic that selectively identifies and suppresses harmful patches without any parameter updates. Evaluated on TimesFM 2.5 across 53 GIFT-Eval datasets under K-fold cross-validation, GITCO achieves an average +1.95% MASE reduction on TimesFM 2.5 while capturing 89.9% of the improvement upper bound. We introduce context sensitivity profiles as a new characterizable property of TSFMs: the mapping from time series meta-features to expected accuracy improvement under inference-time context intervention, shaped jointly by model architecture and the statistical structure of the data.
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
