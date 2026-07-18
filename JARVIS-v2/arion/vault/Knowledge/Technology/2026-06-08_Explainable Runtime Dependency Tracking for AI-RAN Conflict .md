---
title: "Explainable Runtime Dependency Tracking for AI-RAN Conflict Monitoring"
source: https://arxiv.org/abs/2606.06663
date: 2026-06-08
tags:
  - news
  - auto-learning
  - auto-injected
---

# Explainable Runtime Dependency Tracking for AI-RAN Conflict Monitoring

Computer Science > Machine Learning
Title:Explainable Runtime Dependency Tracking for AI-RAN Conflict Monitoring
View PDF HTML (experimental)Abstract:Future AI-integrated Radio Access Networks (AI-RAN) will combine open programmability with learning-enabled xApps, rApps, and control functions that act on shared parameters and key performance indicators (KPIs). For conflict monitoring, it is not enough to know which applications are deployed; the system must also know whether the parameter--KPI dependencies assumed by runtime diagnosis remain valid under the current operating regime. This paper studies a lightweight monitoring primitive for that purpose: tracking an interpretable dependency representation from streaming telemetry events.
We represent active dependencies by a Boolean matrix and use Boolean matrix multiplication to check whether recent parameter-activity and KPI-response events are consistent with the current estimate. We propose a sliding-window inference procedure that reuses the estimate when it remains consistent and recomputes it when recent observations indicate structural change. The tracker is intended as an explainable signal for conflict diagnosis and slow-loop model refresh, not as an autonomous mitigation mechanism. Experiments on controlled Boolean event streams show efficient and accurate tracking under dependency changes and Boolean observation noise.
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
