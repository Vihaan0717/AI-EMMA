---
title: "WAV: Multi-Resolution Block Residual Routing for Deep Decoder-Only Transformers"
source: https://arxiv.org/abs/2606.06564
date: 2026-06-08
tags:
  - news
  - auto-learning
  - auto-injected
---

# WAV: Multi-Resolution Block Residual Routing for Deep Decoder-Only Transformers

Computer Science > Machine Learning
Title:WAV: Multi-Resolution Block Residual Routing for Deep Decoder-Only Transformers
View PDF HTML (experimental)Abstract:Residual connections are central to training deep Transformers, but standard PreNorm residual streams aggregate sublayer updates with fixed unit weights. Recent Attention Residuals replace this fixed accumulation with content-dependent depth-wise routing, and Block Attention Residuals make the mechanism efficient by routing over block-level residual summaries. However, a single block summary stores only the low-frequency total residual displacement inside a block, discarding directional structure such as attention-vs-MLP imbalance and early-vs-late block dynamics. We propose WAV v1, a lightweight multi-resolution residual routing method for decoder-only Transformers. Instead of representing each block only by its accumulated residual sum, WAV v1 augments every block with two directional detail bases: a phase basis that contrasts attention and MLP updates, and a split basis that contrasts early and late sublayer updates. These bases are routed together with standard block summaries through the same depth-wise softmax mixer, while negative detail-source initialization and detached RMS matching stabilize training. On character-level TinyStories and Text8 language modeling, WAV v1 shows a clear depth-dependent benefit. Although it is not consistently beneficial at 12 layers, it becomes competitive at 24 layers and outperforms all baselines at 48 layers. At 48 layers, WAV v1 reduces validation loss relative to Block AttnRes from 0.4960 to 0.4738 on TinyStories and from 0.9363 to 0.9305 on Text8, with negligible additional parameters. These results suggest that directional residual details, not only block-level sums, are important for scaling residual routing in deeper Transformers.
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
