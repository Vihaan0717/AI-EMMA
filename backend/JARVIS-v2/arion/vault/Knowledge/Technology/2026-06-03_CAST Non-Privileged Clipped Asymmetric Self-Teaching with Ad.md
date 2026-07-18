---
title: "CAST: Non-Privileged Clipped Asymmetric Self-Teaching with Advantage Flipping for GRPO"
source: https://arxiv.org/abs/2606.00172
date: 2026-06-03
tags:
  - news
  - auto-learning
  - auto-injected
---

# CAST: Non-Privileged Clipped Asymmetric Self-Teaching with Advantage Flipping for GRPO

Computer Science > Artificial Intelligence
Title:CAST: Non-Privileged Clipped Asymmetric Self-Teaching with Advantage Flipping for GRPO
View PDF HTML (experimental)Abstract:Reinforcement learning with verifiable rewards (RLVR), especially Group Relative Policy Optimization (GRPO), has been widely used to improve reasoning in large language models. However, outcome-level rewards provide only sparse supervision, and group-relative advantages vanish when all sampled trajectories for a prompt are either correct or incorrect. On-Policy Self-Distillation (OPSD) offers dense token-level guidance, but its token preferences are not necessarily aligned with trajectory correctness; empirical diagnostics show that OPSD signals behave differently on correct and incorrect rollouts, with teacher-positive and teacher-negative gap signals exhibiting different noise profiles. These diagnostics are conducted under an OPSD-style privileged teacher context for analysis only, whereas CAST training uses answer-free self-teacher this http URL by these observations, this work proposes CAST, an answer-free self-distillation method for GRPO-style RLVR. CAST keeps the verifier-grounded GRPO objective, but uses a stop-gradient self-teacher to shape token-level advantages according to trajectory correctness. Unlike prior self-distilled RLVR methods, CAST does not require reference-solution-conditioned teacher scoring, keeps the self-teacher log-probability gap active throughout training, and applies bidirectional local advantage sign reversal: teacher-negative tokens in correct trajectories can receive negative token-level advantages, while teacher-positive tokens in incorrect trajectories can receive bounded positive local advantages. For zero-variance all-correct and all-wrong groups, CAST assigns bounded sign-constrained base advantages, so these otherwise zero-gradient groups can contribute verifier-signed token feedback. Experiments on mathematical reasoning show that CAST improves RLVR training while retaining a lightweight, verifier-grounded trajectory-level objective.
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
