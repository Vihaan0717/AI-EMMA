---
title: "X-SYNTH: Beyond Retrieval -- Enterprise Context Synthesis from Observed Human Attention"
source: https://arxiv.org/abs/2605.15505
date: 2026-05-18
tags:
  - news
  - auto-learning
  - auto-injected
---

# X-SYNTH: Beyond Retrieval -- Enterprise Context Synthesis from Observed Human Attention

Computer Science > Artificial Intelligence
Title:X-SYNTH: Beyond Retrieval -- Enterprise Context Synthesis from Observed Human Attention
View PDF HTML (experimental)Abstract:In enterprise operations, the context required for an AI agent task is scattered across systems of record, static information stores, and communication channels. What is stored is system state, a lossy representation of the work that actually happened [2, 52]. The prevailing approach [17, 31, 34, 36] retrieves by matching request content to what is stored; for narrow requests this works well. But synthesis quality depends on knowing what to surface and how to interpret it: knowledge specific to each organization, team, and individual [5, 57, 61], present in behavioral patterns, absent from any retrieval index. For complex agentic tasks it breaks down: True Lead Rate is low, False Lead Rate is high, and the model has no mechanism to improve. We present X-SYNTH, a framework for enterprise context synthesis grounded in human attention, the digitally observable interaction signatures of each worker, encoding not just what they did but the sequence in which they did it, along with implicit reward signals. Behavioral traces preceding positive outcomes are distinguishable from those that did not, without external labeling. X-SYNTH models each individual's behavioral baseline as a Digital Twin Signature (DTS) and selects among seven qualitatively distinct attention filters: Proportional, Inverse, Differential, Recurrent, Comparative, Sequential, and Collective, per individual and per query, to identify causally relevant activity signatures. A four-stage pipeline assembles ranked context grounded in behavioral patterns rather than query embeddings. On a sales lead identification task, a frontier model unaided achieves 9.5% True Lead Rate (TLR) with 90.5% False Lead Rate (FLR). Augmented with X-SYNTH, TLR rises to 61.9% (6.5x) while FLR falls to 18.8%. Enterprise context synthesis is not a retrieval problem. It is a relevance problem, and human attention is its most reliable ground truth.
Current browse context:
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
