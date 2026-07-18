---
title: "CAPS: Cascaded Adaptive Pairwise Selection for Efficient Parallel Reasoning"
source: https://arxiv.org/abs/2605.15513
date: 2026-05-18
tags:
  - news
  - auto-learning
  - auto-injected
---

# CAPS: Cascaded Adaptive Pairwise Selection for Efficient Parallel Reasoning

Computer Science > Artificial Intelligence
Title:CAPS: Cascaded Adaptive Pairwise Selection for Efficient Parallel Reasoning
View PDF HTML (experimental)Abstract:Parallel reasoning, where a generator samples many candidate solutions and an aggregator selects the best, is one of the most effective forms of test-time scaling in large language models, and pairwise self-verification has become its strongest aggregation primitive. Yet pairwise verification carries a heavy cost: each judgment reads two complete solutions in full, and existing methods perform tens of such judgments per problem regardless of whether the comparison is informative. We introduce CAPS (Cascaded Adaptive Pairwise Selection), an inference-only framework that allocates verifier compute non-uniformly along two orthogonal axes: an evidence axis that adapts how much of each candidate the judge sees, and a distribution axis that adapts how comparisons are spread across the pool. CAPS instantiates these into a four-stage cascade with an optional rescue subroutine, and admits a closed-form verifier-token cost in which the per-candidate marginal cost is roughly halved relative to uniform full-evidence schedules. On four self-verifying models (Qwen3-14B, GPT-OSS-20B, Qwen3-4B-Instruct/Thinking) and five reasoning benchmarks spanning code (LiveCodeBench-v5/v6, CodeContests) and math (AIME 2025, HMMT 2025), CAPS outperforms the leading pairwise verifier on 14 of 20 suites while using 25.4% of its verifier-token budget on code, and outperforms pointwise self-verification on all 20. The trade-off suites admit an interpretable diagnostic in terms of the verifier's accuracy at partial versus full evidence, providing a concrete pre-deployment check for cascade suitability.
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
