---
title: "AEGIS: A Backup Reflex for Physical AI"
source: https://arxiv.org/abs/2606.06660
date: 2026-06-08
tags:
  - news
  - auto-learning
  - auto-injected
---

# AEGIS: A Backup Reflex for Physical AI

Computer Science > Artificial Intelligence
Title:AEGIS: A Backup Reflex for Physical AI
View PDF HTML (experimental)Abstract:Long-horizon robot manipulation tends to fail gradually: one bad step degrades the state, and the policy spirals into a basin from which it cannot recover. The failure is often visible before it happens. We introduce AEGIS (Activation-probe Early-warning, Gated Inference Switching), a selective escalation method that uses a lightweight probe on a weak policy's frozen activations to detect high-risk steps while there is still time to act. When the probe flags a step, control switches to a stronger separate policy, but only for the steps that need it. On LIBERO-Spatial, AEGIS recovers 10.1% of the trajectories the weak policy alone loses, versus 4.6% for budget-matched blind escalation and 5.1% for a random-trigger placebo. These gains are significant under one-sided exact paired McNemar tests with Holm-Bonferroni adjustment over three pre-registered contrasts: +5.4pp over blind escalation, p=8.5e-6; +5.0pp over random triggering, p=1.0e-4; paired-trajectory bootstrap CIs exclude zero. AEGIS activates the stronger policy on only 38% of steps, so the lever is timing rather than compute. The probe clears its precondition with an early-window AUROC of 0.764, 95% CI [0.70, 0.84], read from the weak-policy path over the first 30% of trajectory steps before any handoff. We pre-register the full analysis plan, including a conditional recovered-task-rate estimand and explicit kill criteria, and confirm the result on 700 common-random-number episodes per arm, with nA-fail=646.
Current browse context:
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
