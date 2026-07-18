---
title: "From LLM-Generated Conjectures to Lean Formalizations: Automated Polynomial Inequality Proving via Sum-of-Squares Certificates"
source: https://arxiv.org/abs/2605.15445
date: 2026-05-18
tags:
  - news
  - auto-learning
  - auto-injected
---

# From LLM-Generated Conjectures to Lean Formalizations: Automated Polynomial Inequality Proving via Sum-of-Squares Certificates

Computer Science > Artificial Intelligence
Title:From LLM-Generated Conjectures to Lean Formalizations: Automated Polynomial Inequality Proving via Sum-of-Squares Certificates
View PDF HTML (experimental)Abstract:Automated proving of polynomial inequalities is a fundamental challenge in automated mathematical reasoning, where rich algebraic structure and a rapidly growing certificate search space hinder scalability. Purely symbolic approaches provide strong guarantees but often scale poorly as the number of variables or the degree increases, due to expensive algebraic manipulations and rapidly growing intermediate expressions. In parallel, LLM-guided methods have made notable progress, particularly on competition-style inequalities with a small number of variables. To address the remaining scalability challenges, we propose NSPI, a neuro-symbolic framework that combines the complementary strengths of LLMs and symbolic computation for polynomial-inequality proving. Concretely, an LLM proposes a conjecture in the form of an approximate polynomial Sum-Of-Squares (SOS) decomposition; we refine it via symbolic computation to obtain an exact polynomial SOS representation, which directly proves the target inequality, and we further certify the proof in Lean, yielding an end-to-end pipeline from heuristic discovery to machine-checked proof. Experiments on challenging benchmarks involving polynomials with up to 10 variables demonstrate the effectiveness and scalability of the proposed method.
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
