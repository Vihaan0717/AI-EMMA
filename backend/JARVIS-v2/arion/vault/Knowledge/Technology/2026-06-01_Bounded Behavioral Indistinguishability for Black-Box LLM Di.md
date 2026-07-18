---
title: "Bounded Behavioral Indistinguishability for Black-Box LLM Distillation"
source: https://arxiv.org/abs/2605.30448
date: 2026-06-01
tags:
  - news
  - auto-learning
  - auto-injected
---

# Bounded Behavioral Indistinguishability for Black-Box LLM Distillation

Computer Science > Machine Learning
Title:Bounded Behavioral Indistinguishability for Black-Box LLM Distillation
View PDF HTML (experimental)
We instantiate this notion on Qwen and Llama teacher-student pairs using a controlled $5,000$-prompt behavioral probe suite. For each family, we compare the teacher with both the base student and the LoRA-distilled student, measuring whether distillation reduces distinguishability rather than merely improving similarity. LoRA raises semantic similarity from $0.788$ to $0.862$ for Qwen and from $0.814$ to $0.874$ for Llama. Yet adversarial evaluation reveals remaining behavioral differences: learned discriminators retain nonzero advantage, and pairwise category analysis shows artifacts concentrated in style/format, robustness, and domain-technical prompts. A pairwise teacher-identification adversary confirms this trend. With a different-family Llama judge and A/B-swap consistency filtering, Qwen distinguishing advantage drops from $0.158$ for the base student to $0.081$ after LoRA distillation. Query-budget experiments show that disagreement-guided acquisition does not consistently outperform stratified random sampling, indicating that coverage and diversity remain strong baselines. Our results show that semantic fidelity is useful but insufficient: black-box LLM distillation requires bounded, adversarial, and category-aware evaluation.
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
