---
title: "Uncertainty-Aware LLM-Guided Policy Shaping for Sparse-Reward Reinforcement Learning"
source: https://arxiv.org/abs/2606.06673
date: 2026-06-08
tags:
  - news
  - auto-learning
  - auto-injected
---

# Uncertainty-Aware LLM-Guided Policy Shaping for Sparse-Reward Reinforcement Learning

Computer Science > Machine Learning
Title:Uncertainty-Aware LLM-Guided Policy Shaping for Sparse-Reward Reinforcement Learning
View PDF HTML (experimental)Abstract:Sparse rewards and heterogeneous task sequences remain persistent challenges in Reinforcement Learning (RL), often resulting in slow convergence, weak generalization, and inefficient exploration. We propose Uncertainty-Aware LLM-Guided Policy Shaping (ULPS), a novel framework that integrates a calibrated Large Language Model (LLM) into the RL training loop to provide structured, uncertainty-modulated behavioral guidance. ULPS employs an A*-based oracle to synthesize optimal symbolic trajectories, which are used to fine-tune a BERT-based language model. During training, this model supplies action suggestions whose influence is conditioned on epistemic uncertainty estimated via Monte Carlo (MC) dropout. An entropy-based blending mechanism adaptively balances LLM guidance and the learned policy (via Proximal Policy Optimization, PPO), allowing the agent to prioritize reliable priors while preserving adaptability. We evaluate ULPS on the MiniGridUnlockPickup benchmark and observe consistent improvements in success rate, reward efficiency, and sample complexity over unguided, uncalibrated, and standard RL baselines. ULPS achieves more than 9% improvement in execution accuracy after fine-tuning, requires fewer environment interactions, and yields higher reward AUC. Our results demonstrate that integrating symbolic A* trajectories, pretrained language priors, and uncertainty-aware control offers a principled and effective approach to multi-task reinforcement learning in sparse-reward domains, with potential extensibility to partially observable and multi-agent settings.
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
