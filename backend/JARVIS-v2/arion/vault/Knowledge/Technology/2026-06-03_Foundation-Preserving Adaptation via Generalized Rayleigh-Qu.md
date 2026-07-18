---
title: "Foundation-Preserving Adaptation via Generalized Rayleigh-Quotient Optimization"
source: https://arxiv.org/abs/2606.00132
date: 2026-06-03
tags:
  - news
  - auto-learning
  - auto-injected
---

# Foundation-Preserving Adaptation via Generalized Rayleigh-Quotient Optimization

Computer Science > Machine Learning
Title:Foundation-Preserving Adaptation via Generalized Rayleigh-Quotient Optimization
View PDFAbstract:While finetuning effectively adapts foundation models to specialized downstream tasks, it can degrade nontarget capabilities acquired during pretraining. Existing forgetting aware methods typically seek safer updates through specialized initialization or fixed constraints, but do not regulate the adaptation preservation trade-off during training. We propose Foundation Preserving LoRA (FoLoRA), a forgetting aware optimization framework. Guided by a first order preservation condition, FoLoRA defines a forgetting penalty over pretraining-proxy activations and a task utility over downstream task activations. It then scores update directions by task utility per unit forgetting penalty via a generalized Rayleigh quotient. The resulting spectral coordinate system enables direction wise gated Adam updates, attenuating low utility to penalty directions during training. To estimate the forgetting penalty, FoLoRA constructs pretraining proxy calibration data by sampling from the pretrained model rather than relying on a single proxy dataset. Experiments on math, code, and instruction following adaptation show that FoLoRA achieves the strongest preservation adaptation balance over baselines, improving target task performance with best aggregate preservation of non target capabilities.
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
