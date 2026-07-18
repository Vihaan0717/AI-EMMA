---
title: "CAX-Agent: A Lightweight Agent Harness for Reliable APDL Automation"
source: https://arxiv.org/abs/2605.15218
date: 2026-05-18
tags:
  - news
  - auto-learning
  - auto-injected
---

# CAX-Agent: A Lightweight Agent Harness for Reliable APDL Automation

Computer Science > Artificial Intelligence
Title:CAX-Agent: A Lightweight Agent Harness for Reliable APDL Automation
View PDF HTML (experimental)Abstract:Large language models deployed for MAPDL finite-element simulation face practical reliability challenges: without structured execution control, tool encapsulation, and fault recovery, outputs may be inconsistent and task failures are common. The Agent Harness paradigm addresses this by inserting domain-specific orchestration middleware that manages tool lifecycles, workflow state, and recovery escalation. This paper presents the architecture of CAX-Agent, a lightweight agent harness purpose-built for MAPDL automation, and empirically evaluates one of its core components -- the recovery this http URL-Agent organizes execution into three layers -- LLM service, agent harness, and solver backend -- with a recovery ladder that escalates from deterministic rule patching through model-driven regeneration to context enrichment and human intervention. We evaluate three recovery strategies (no_recovery, rule_only, and model_only) on 50 standard structural benchmarks with three repeated runs per strategy (450 case-runs total). Two independent human raters score task completion under blind conditions; inter-rater agreement is strong (quadratic weighted Cohen's kappa = 0.84, 96 percent of score pairs within one point). Model_only achieves the best completion rate (0.9267), task score (3.59/4), total score (9.16/10), and zero-intervention rate (0.84), outperforming rule_only (0.7733, 3.17/4, 7.03/10, 0.00) and no_recovery (0.6933, 2.74/4, 5.60/10, 0.00) with large effect sizes (Cliff's delta = 0.81-0.87). The benchmark uses deliberately simple geometries to isolate recovery-policy effects; we discuss the scope of these findings and directions for broader validation.
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
