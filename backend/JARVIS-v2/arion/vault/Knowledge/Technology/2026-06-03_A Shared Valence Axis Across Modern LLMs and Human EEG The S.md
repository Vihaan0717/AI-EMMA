---
title: "A Shared Valence Axis Across Modern LLMs and Human EEG: The Saturation Regularity"
source: https://arxiv.org/abs/2606.00129
date: 2026-06-03
tags:
  - news
  - auto-learning
  - auto-injected
---

# A Shared Valence Axis Across Modern LLMs and Human EEG: The Saturation Regularity

Computer Science > Machine Learning
Title:A Shared Valence Axis Across Modern LLMs and Human EEG: The Saturation Regularity
View PDF HTML (experimental)Abstract:Large language models (LLMs) have emerged as powerful representation learners whose internal features increasingly align with human cognition. We study whether modern LLMs can serve as a lens for understanding neural representations in the human brain, focusing on emotional valence in EEG.
We first build a one-dimensional valence direction, the V-axis, from modern LLMs using only nine emotion-evocative sentences. We validate it through zero-shot transfer to sentiment benchmarks and cross-model consistency across fourteen LLMs. We then show that this LLM-derived direction maps onto human neural activity. On a public EEG cohort of 123 subjects watching affective videos, a single linear projection on EEG features tracks the V-axis position of each stimulus. Moreover, 36 EEG emotion classifiers trained without exposure to the V-axis spontaneously rediscover the same direction in their internal representations, suggesting that the same valence structure emerges in both language models and human electrophysiology.
Yet this convergence does not provide an effective training signal. We test twenty-five alignment strategies, including knowledge distillation, representational similarity, contrastive, and topographic losses; none improve decoding, and sixteen significantly reduce accuracy. We formalize this result as the saturation regularity: once task labels alone drive a brain-decoding network onto the target direction, additional supervision mainly distorts an already-saturated basin, while the load-bearing within-class residual receives little useful gradient.
This regularity also indicates where improvement should come from: the residual subspace unreachable by supervision. Motivated by this insight, we ensemble across residual diversity rather than supervising the basin, improving balanced accuracy by 10.5% over the prior best on FACED, with the same effect replicated on SEED-V.
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
