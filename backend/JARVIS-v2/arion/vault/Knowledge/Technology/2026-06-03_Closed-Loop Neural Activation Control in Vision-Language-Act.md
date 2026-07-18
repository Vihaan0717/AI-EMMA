---
title: "Closed-Loop Neural Activation Control in Vision-Language-Action Models"
source: https://arxiv.org/abs/2606.00269
date: 2026-06-03
tags:
  - news
  - auto-learning
  - auto-injected
---

# Closed-Loop Neural Activation Control in Vision-Language-Action Models

Computer Science > Artificial Intelligence
Title:Closed-Loop Neural Activation Control in Vision-Language-Action Models
View PDF HTML (experimental)Abstract:Vision-Language-Action (VLA) models can be steered at test time by intervening on semantically meaningful internal directions, but existing methods use a fixed steering coefficient, effectively operating in open loop. This is poorly suited to embodied control, where task state and concept error evolve over time, often causing overcorrection, oscillation, and reduced task success, especially for temporal behaviors such as speed and smoothness. We propose CTRL-STEER, a closed-loop framework that replaces static intervention strength with adaptive, time-varying control signals. The key idea is to decouple representation from regulation: rather than assuming temporal concepts are directly controlled by individual neurons, we steer along motion-aligned residual directions while a feedback controller adjusts intervention magnitude online. We instantiate this framework with both PID and reinforcement learning based controllers. Experiments with a fine-tuned OpenVLA policy on four LIBERO task suites show that CTRL-STEER achieves more stable concept regulation and a better steering-task success trade-off than fixed-coefficient baselines, without modifying or retraining the base model.
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
