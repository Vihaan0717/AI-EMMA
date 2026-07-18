---
title: "ICRL: Learning to Internalize Self-Critique with Reinforcement Learning"
source: https://arxiv.org/abs/2605.15224
date: 2026-05-18
tags:
  - news
  - auto-learning
  - auto-injected
---

# ICRL: Learning to Internalize Self-Critique with Reinforcement Learning

Computer Science > Artificial Intelligence
Title:ICRL: Learning to Internalize Self-Critique with Reinforcement Learning
View PDF HTML (experimental)Abstract:Large language model-based agents make mistakes, yet critique can often guide the same model toward correct behavior. However, when critique is removed, the model may fail again on the same query, indicating that it has not internalized the critique's guidance into its underlying capability. Meanwhile, a frozen critic cannot improve its feedback quality over time, limiting the potential for iterative self-improvement. To address this, we propose learning to internalize self-critique with reinforcement learning(ICRL), a novel framework that jointly trains a solver and a critic from a shared backbone to convert critique-induced success into unassisted solver ability. The critic is rewarded based on the solver's subsequent performance gain, incentivizing actionable feedback. To address the distribution shift between critique-conditioned and critique-free behavior, ICRL introduces a distribution-calibration re-weighting ratio that selectively transfers critique-guided improvements compatible with the solver's own prompt distribution. Additionally, a role-wise group advantage estimation stabilizes joint optimization across the two roles. Together, these mechanisms ensure that the solver learns to improve itself without external critique, rather than becoming dependent on critique-conditioned behavior. We evaluate ICRL on diverse benchmarks spanning agentic and mathematical reasoning tasks, using Qwen3-4B and Qwen3-8B as backbones. Results show consistent improvements, with average gains of 6.4 points over GRPO on agentic tasks, and 7.0 points on mathematical reasoning. Notably, the learned 8B critic is comparable to 32B critics while using substantially fewer tokens. The code is available at this https URL.
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
