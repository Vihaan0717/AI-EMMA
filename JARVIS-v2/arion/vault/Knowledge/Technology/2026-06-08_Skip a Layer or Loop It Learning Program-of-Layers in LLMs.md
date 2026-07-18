---
title: "Skip a Layer or Loop It? Learning Program-of-Layers in LLMs"
source: https://arxiv.org/abs/2606.06574
date: 2026-06-08
tags:
  - news
  - auto-learning
  - auto-injected
---

# Skip a Layer or Loop It? Learning Program-of-Layers in LLMs

Computer Science > Machine Learning
Title:Skip a Layer or Loop It? Learning Program-of-Layers in LLMs
View PDF HTML (experimental)Abstract:Large language models (LLMs) perform inference by following a fixed depth and order, non-recurrent execution of all layers. We reveal the wide existence of training-free, flexible, dynamic program-of-layers (PoLar), where pretrained layers can be packed as modules and then skipped or looped to form a customized program for each input. For most inputs, substantially shorter program executions can achieve the same or better accuracy, while incorrect predictions of the original LLM can be corrected by alternative programs with fewer layers. These observations indicate that inference admits multiple valid latent computations beyond the standard forward pass. To efficiently achieve PoLar in practice, we propose a lightweight PoLar prediction network, which learns to generate execution programs that dynamically skip or repeat pretrained layers for each input. Experiments on mathematical reasoning benchmarks demonstrate that PoLar consistently improves accuracy over standard inference and prior dynamic-depth methods, often while executing fewer layers, and that these gains persist under out-of-distribution evaluation. Our results suggest that fixed-depth execution captures only a narrow subset of an LLM's latent reasoning capacity.
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
