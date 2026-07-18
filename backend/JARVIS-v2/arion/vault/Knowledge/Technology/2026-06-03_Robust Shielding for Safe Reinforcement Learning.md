---
title: "Robust Shielding for Safe Reinforcement Learning"
source: https://arxiv.org/abs/2606.00270
date: 2026-06-03
tags:
  - news
  - auto-learning
  - auto-injected
---

# Robust Shielding for Safe Reinforcement Learning

Computer Science > Artificial Intelligence
Title:Robust Shielding for Safe Reinforcement Learning
View PDFAbstract:Shielding is an effective approach to formally guarantee the safety of reinforcement learning agents in Markov decision processes (MDPs). However, existing shielding techniques typically assume knowledge of the safety-relevant transition dynamics - a requirement that is seldom met in practice. To address this limitation, we introduce a novel shielding framework for robust MDPs (RMDPs), i.e., MDPs with sets of transition probabilities. We define safety as the satisfaction of a linear temporal logic (LTL) formula with a certain threshold probability under the worst-case transition probabilities of the RMDP. We prove that our shielding framework is both sound and optimal for the RMDP: every policy admissible by the shield is safe, and conversely, every safe RMDP policy is admissible by the shield. We combine our approach with existing sampling methods for learning transition probabilities of MDPs with probably approximately correct (PAC) guarantees. This combination enables the construction of shields for MDPs that, with high confidence, guarantee safety while remaining minimally restrictive. Our experiments show that our shields for learned RMDPs guarantee safety in unknown MDPs while recovering strong expected return as the number of samples increases.
Current browse context:
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
