---
title: "Emergence of Exploration in Policy Gradient Reinforcement Learning via Retrying"
source: https://arxiv.org/abs/2606.00151
date: 2026-06-03
tags:
  - news
  - auto-learning
  - auto-injected
---

# Emergence of Exploration in Policy Gradient Reinforcement Learning via Retrying

Computer Science > Machine Learning
Title:Emergence of Exploration in Policy Gradient Reinforcement Learning via Retrying
View PDF HTML (experimental)Abstract:In reinforcement learning (RL), agents benefit from exploration only because they repeatedly encounter similar states: trying different actions can improve performance or reduce uncertainty; without such retries, a greedy policy is optimal. We formalize this intuition with ReMax, an objective that evaluates a policy by the expected maximum return over $M$ samples, where $M$ is a positive integer, while accounting for return uncertainty. Optimizing this objective induces stochastic exploration as an emergent property, without explicit bonus terms. For efficient policy optimization, we derive a new policy-gradient formulation for ReMax and introduce ReMax PPO (RePPO), a PPO variant that optimizes ReMax while generalizing the discrete retry count $M$ to a continuous parameter $m > 0$, enabling fine-grained control of exploration. Empirically, RePPO promotes exploration, without any explicit exploration bonuses, on the MinAtar and Craftax benchmarks.
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
