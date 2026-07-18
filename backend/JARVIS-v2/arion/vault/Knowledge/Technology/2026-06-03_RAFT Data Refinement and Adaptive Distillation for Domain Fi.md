---
title: "RAFT: Data Refinement and Adaptive Distillation for Domain Fine-Tuning with Alleviated Forgetting"
source: https://arxiv.org/abs/2606.00147
date: 2026-06-03
tags:
  - news
  - auto-learning
  - auto-injected
---

# RAFT: Data Refinement and Adaptive Distillation for Domain Fine-Tuning with Alleviated Forgetting

Computer Science > Machine Learning
Title:RAFT: Data Refinement and Adaptive Distillation for Domain Fine-Tuning with Alleviated Forgetting
View PDF HTML (experimental)Abstract:Domain-specific supervised fine-tuning (SFT) often improves in-domain performance at the cost of degrading a model's general capabilities. We view this degradation through two practical gaps in domain SFT: a supervision-compatibility gap, where domain targets differ in style and reasoning format from the original model's natural responses, and a trajectory-preservation gap, where teacher-forced SFT optimizes fixed target tokens without constraining the model's behavior on its own generated prefixes. This process fails to preserve the model's original behavior. We propose RAFT (Data Refinement and Adaptive Distillation for Domain Fine-Tuning with Alleviated Forgetting), a two-stage framework that addresses both factors. First, RAFT constructs model-compatible supervision through self-conditioned rewriting, semantic filtering, and answer fusion. Second, RAFT performs Answer-Conditioned On-Policy Distillation, where the original instruction-tuned model provides soft targets on student-generated trajectories while being conditioned on the fused answer as helpful context. We further introduce top-K temperature distillation and EMA-based adaptive loss balancing to stabilize the domain-general trade-off. Across three instruction-tuned backbones and five domains, RAFT improves average domain accuracy by 23.2% over standard SFT, while recovering part of the SFT-induced degradation on MS-Bench and IFEval, with relative improvements of 18.2% and 10.2%, respectively. These results show that coupling data refinement with trajectory-level preservation provides an effective recipe for domain fine-tuning with alleviated forgetting.
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
