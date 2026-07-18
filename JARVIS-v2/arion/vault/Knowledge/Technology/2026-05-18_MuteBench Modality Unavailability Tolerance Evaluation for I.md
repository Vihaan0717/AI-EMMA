---
title: "MuteBench: Modality Unavailability Tolerance Evaluation for Incomplete Multimodal Fusion"
source: https://arxiv.org/abs/2605.15235
date: 2026-05-18
tags:
  - news
  - auto-learning
  - auto-injected
---

# MuteBench: Modality Unavailability Tolerance Evaluation for Incomplete Multimodal Fusion

Computer Science > Machine Learning
Title:MuteBench: Modality Unavailability Tolerance Evaluation for Incomplete Multimodal Fusion
View PDF HTML (experimental)Abstract:Multimodal physiological data powers clinical AI systems from intensive care units to wearable devices, but sensors routinely fail in practice. Two failure modes are common: modality missing, where an entire channel is absent, and within-modality missing, where a contiguous time segment is lost. No existing benchmark evaluates multiple fusion architectures under both failure modes at controlled severity levels across diverse clinical datasets. We present MuteBench, a benchmark covering 9 datasets from 7 clinical domains, 6 fusion architectures, and 2 missing-data modes over 125,000 samples. Through this benchmark, we find that architecture family is the strongest predictor of robustness, outweighing parameter count. Channel-independent models tolerate modality missing well but can be sensitive to within-modality missing, especially on short sequences. Curriculum modality dropout protects reliably only up to the maximum dropout rate used in training. We also find that channel count, sequence length, and modality alignment jointly determine which failure mode poses the greater threat. Finally, a PTB-XL case study suggests that diffusion-based imputation can improve downstream classification under within-modality missing, with the largest gains for models whose expert routing is most sensitive to corrupted inputs, though broader validation across datasets remains an open direction. MuteBench provides practitioners with concrete guidance for both selecting existing architectures and informing the design of future robust multimodal fusion methods.
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
