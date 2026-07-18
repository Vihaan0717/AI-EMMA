---
title: "Quantum-Inspired Trace-Augmented Evidence Selection for Reasoning over Structured Hypothesis Spaces"
source: https://arxiv.org/abs/2606.06941
date: 2026-06-08
tags:
  - news
  - auto-learning
  - auto-injected
---

# Quantum-Inspired Trace-Augmented Evidence Selection for Reasoning over Structured Hypothesis Spaces

Computer Science > Artificial Intelligence
Title:Quantum-Inspired Trace-Augmented Evidence Selection for Reasoning over Structured Hypothesis Spaces
View PDF HTML (experimental)Abstract:Large language models (LLMs) now solve a wide range of expert-level exams at or above human level, yet remain brittle on specialised, evidence-intensive domains such as law. On these tasks, errors arise not only from gaps in world knowledge but also from subtle distinctions between pieces of evidence and inconsistent use of supporting evidence. The most common aggregator over sampled chain-of-thought (CoT) traces, majority vote, returns the most popular answer regardless of whether its evidence is actually strongest. We propose to treat the selection of CoT reasoning fragments into a set of evidence as an explicit combinatorial optimisation problem, allowing well-supported but minority hypotheses to override noisy majorities, and to evaluate the approach on legal-reasoning benchmarks that are particularly sensitive to evidence quality. We introduce EP-HUBO (Evidence Pool Higher-Order Binary Optimisation), which generates multiple CoT traces with a small local model, parses fragments into per-hypothesis evidence pools, solves a higher-order unconstrained binary optimisation per pool with quality-derived weights (relevance, specificity, distinctiveness), and delegates a single adjudication call per question to a frontier model. We evaluate EP-HUBO on two evidence-intensive legal benchmarks using both simulated annealing on classical hardware and the Dirac-3 photonic entropy-quantum machine from Quantum Computing Inc. HUBO-style optimisation gives a principled way to aggregate reasoning fragments while preserving minority-but-correct hypotheses, and is most valuable in low-contamination domains where frontier models have not already absorbed the benchmark material.
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
