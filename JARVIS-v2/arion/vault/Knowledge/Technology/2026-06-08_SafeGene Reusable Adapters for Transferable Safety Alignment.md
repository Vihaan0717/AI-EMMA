---
title: "SafeGene: Reusable Adapters for Transferable Safety Alignment"
source: https://arxiv.org/abs/2606.06519
date: 2026-06-08
tags:
  - news
  - auto-learning
  - auto-injected
---

# SafeGene: Reusable Adapters for Transferable Safety Alignment

Computer Science > Artificial Intelligence
Title:SafeGene: Reusable Adapters for Transferable Safety Alignment
View PDF HTML (experimental)Abstract:Open-weight LLMs are increasingly fine-tuned into customized assistants, but downstream fine-tuning can weaken safety alignment and make models more vulnerable to malicious prompts, even when the training data is not intentionally harmful. This creates a recurring safety recovery problem as target models are repeatedly updated with new task data or user interactions. We propose SafeGene, a reusable safety-adapter module designed for cross-task reuse within each architecture-compatible model family. Rather than treating safety recovery as a model-specific repair step, SafeGene treats safety capability as an independent, reusable adapter representation decoupled from task-specific updates. This representation is obtained from aligned--degraded model discrepancies, refined into task-transferable safety vectors through data-aware layer selection, and expressed in each downstream task-adapted model via few-shot layer-wise coefficient recalibration. Experiments across multiple model families, downstream tasks, and safety judges show that SafeGene-enhanced models reduce harmful response rates while maintaining downstream performance, outperforming representative safe adaptation methods in safety--utility trade-off.
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
arXivLabs is a framework that allows collaborators to develop and share new arXiv features directly on our website.
Both individuals and organizations that work with arXivLabs have embraced and accepted our values of openness, community, excellence, and user data privacy. arXiv is committed to these values and only works with partners that adhere to them.
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
