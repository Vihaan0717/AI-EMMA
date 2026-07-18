---
title: "Training on Documents About Monitoring Leads to CoT Obfuscation"
source: https://arxiv.org/abs/2605.15257
date: 2026-05-18
tags:
  - news
  - auto-learning
  - auto-injected
---

# Training on Documents About Monitoring Leads to CoT Obfuscation

Computer Science > Machine Learning
Title:Training on Documents About Monitoring Leads to CoT Obfuscation
View PDFAbstract:Chain-of-thought (CoT) monitoring is one of the most promising tools we have for detecting model misbehavior, but its effectiveness depends on models faithfully externalizing their reasoning. Motivated by this vulnerability, we study whether monitor-aware models are capable of obfuscating their reasoning to evade detection. We use synthetic document finetuning to expose eight models to realistic pre-training-style documents describing a CoT monitor and find that monitor-aware models consistently achieve higher rates of undetected misbehavior compared to unaware controls. This effect is weaker but still present on a harder agentic task. We also show that CoT controllability, a model's ability to reshape its own reasoning trace under an imposed constraint, is closely correlated with obfuscation success across the eight models studied ($r=0.800$, $p=0.017$). Monitor-aware models placed under equal reinforcement learning optimization pressure also learn to reward-hack without triggering a CoT monitor substantially faster than unaware controls. Together, these results suggest that knowledge of monitoring combined with high CoT controllability poses a risk to CoT-based monitoring.
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
