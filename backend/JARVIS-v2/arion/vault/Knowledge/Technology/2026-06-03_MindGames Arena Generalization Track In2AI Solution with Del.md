---
title: "MindGames Arena Generalization Track: In2AI Solution with Delayed Per-Step Reward Attribution"
source: https://arxiv.org/abs/2606.00017
date: 2026-06-03
tags:
  - news
  - auto-learning
  - auto-injected
---

# MindGames Arena Generalization Track: In2AI Solution with Delayed Per-Step Reward Attribution

Computer Science > Artificial Intelligence
Title:MindGames Arena Generalization Track: In2AI Solution with Delayed Per-Step Reward Attribution
View PDF HTML (experimental)Abstract:Training language model agents for multi-agent strategic interaction presents a core difficulty: the quality of any action may depend on future events that never materialize, on moves that violate game rules, or on decisions made by other players. Standard reinforcement learning assumes that rewards can be assigned at each step, but this assumption fails in settings where outcomes are entangled across time and agents. We introduce delayed per-step reward attribution with eligibility gating, an episode lifecycle and postprocessing pipeline that computes rewards only at episode end, propagates them back to originating steps according to task-specific semantics, and excludes steps that lack valid dependent information from training. Together with asynchronous rollout generation via vLLM's continuous batching, curriculum-based opponent sampling, and multi-level stratified batch construction, this approach enables stable, sample-efficient RL training in multi-agent environments. We evaluate on the MindGames Arena benchmark at NeurIPS 2025, where a single 8-billion-parameter open-source model trained with our method matched or surpassed substantially larger proprietary systems, including GPT-5, in head-to-head play and took first place in both the Open (unrestricted) and Efficient (<=8B parameters) tracks.
Current browse context:
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
