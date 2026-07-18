---
title: "Synthetic Contrastive Reasoning for Multi-Table Q&A"
source: https://arxiv.org/abs/2606.05382
date: 2026-06-06
tags:
  - news
  - auto-learning
  - auto-injected
---

# Synthetic Contrastive Reasoning for Multi-Table Q&A

Computer Science > Artificial Intelligence
Title:Synthetic Contrastive Reasoning for Multi-Table Q&A
View PDF HTML (experimental)Abstract:Multi-table question answering requires models to retrieve relevant evidence, link schemas, and perform compositional reasoning across relational tables. Existing multi-table Q&A resources typically provide questions and final answers but lack reasoning supervision that explains how answers are derived. To address this gap, we construct a synthetic contrastive reasoning-trace dataset for MMQA by generating validated positive traces and plausible negative traces with heterogeneous LLMs. We then use the resulting preference pairs to fine-tune open-weight LLMs with Contrastive Preference Optimization (CPO). Across Qwen3-14B, Mistral-8B, and Llama-3.1-8B, CPO achieves absolute average improvements over Q&A supervised fine-tuning ranging from 9.7%-16.3%, with gains up to 21 percentage points on MMQA. Ablations show that heterogeneous positive and negative trace generators strengthen the contrastive signal, and automated as well as human evaluations indicate that the generated pairs are largely faithful, coherent, and meaningfully contrastive.
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
