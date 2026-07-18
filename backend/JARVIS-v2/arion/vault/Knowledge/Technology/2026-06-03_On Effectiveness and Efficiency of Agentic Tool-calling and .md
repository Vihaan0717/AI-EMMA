---
title: "On Effectiveness and Efficiency of Agentic Tool-calling and RL Training"
source: https://arxiv.org/abs/2606.00135
date: 2026-06-03
tags:
  - news
  - auto-learning
  - auto-injected
---

# On Effectiveness and Efficiency of Agentic Tool-calling and RL Training

Computer Science > Machine Learning
Title:On Effectiveness and Efficiency of Agentic Tool-calling and RL Training
View PDF HTML (experimental)Abstract:Tool-calling is a central component of modern large language model (LLM) agents, equipping them with skills beyond their parametric knowledge. This paper studies tool-calling along two complementary axes: effectiveness, i.e., how this capability is measured, and efficiency, i.e., how it is learned. On effectiveness, we systematically analyze tool-calling evaluation pipelines and show that results can be highly sensitive to seemingly minor, often undocumented implementation choices including the random seed, system prompt, multi-turn template construction, and how prior interaction/reasoning history is carried forward. These choices can lead to substantial differences in reported performance, especially in multi-turn settings where without rigorous standardization, leaderboard rankings are unreliable. On efficiency, we examine standard reinforcement learning (RL) for tool-calling and identify two sources of computational waste: (i) during rollouts, many prompts produce no learning signal, and (ii) during policy updates, optimization incurs high computational cost. Guided by these findings, we introduce two techniques that accelerate RL-based tool-calling training, achieving substantial wall-clock speedup without degrading performance.
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
