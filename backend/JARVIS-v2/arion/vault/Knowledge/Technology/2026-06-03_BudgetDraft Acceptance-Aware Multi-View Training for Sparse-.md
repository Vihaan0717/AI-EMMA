---
title: "BudgetDraft: Acceptance-Aware Multi-View Training for Sparse-KV Speculative Decoding"
source: https://arxiv.org/abs/2606.00144
date: 2026-06-03
tags:
  - news
  - auto-learning
  - auto-injected
---

# BudgetDraft: Acceptance-Aware Multi-View Training for Sparse-KV Speculative Decoding

Computer Science > Machine Learning
Title:BudgetDraft: Acceptance-Aware Multi-View Training for Sparse-KV Speculative Decoding
View PDF HTML (experimental)Abstract:Speculative decoding speeds up autoregressive decoding by using a drafter to propose multiple tokens that a verifier validates in parallel. In resource-constrained deployments, the drafter uses a sparse KV cache to limit peak GPU memory and end-to-end latency under a fixed KV budget, while the verifier keeps a full KV cache. Mid-to-long context inference (4K--16K context length) is common in real applications. However, naive sparse/full speculative decoding suffers from the sparse/full mismatch as context length grows, causing the acceptance rate to drop quickly. We propose BudgetDraft, a multi-view sparse training method for sparse drafting in mid-to-long inference. The drafter is exposed to multiple sampled KV budgets during training and learns to align each sparse view with one shared full-cache teacher target. BudgetDraft combines an acceptance-aware loss on a full-cache branch with a multi-view loss on a sparse-cache branch, producing a single budget-robust drafter that recovers acceptance across sparsity levels without extra inference-time components. Experimental results on PG-19, LongBench, and LWM show that BudgetDraft achieves up to 6.55x, 4.46x, and 2.10x end-to-end speedup vs AR at 4K, 8K, and 16K context lengths, while keeping the inference pipeline memory-friendly.
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
