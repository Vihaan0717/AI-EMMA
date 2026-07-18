---
title: "DAStatFormer: A Hybrid Multibranch Transformer with Statistical Feature Integration for DAS-Based Pattern Recognitions"
source: https://arxiv.org/abs/2606.00081
date: 2026-06-03
tags:
  - news
  - auto-learning
  - auto-injected
---

# DAStatFormer: A Hybrid Multibranch Transformer with Statistical Feature Integration for DAS-Based Pattern Recognitions

Computer Science > Machine Learning
Title:DAStatFormer: A Hybrid Multibranch Transformer with Statistical Feature Integration for DAS-Based Pattern Recognitions
View PDFAbstract:Distributed Acoustic Sensing (DAS) enables large-scale monitoring through optical fibers, but its high dimensionality and complex spatio-temporal patterns make event classification demanding. Existing deep learning approaches-CNNs, recurrent models, and Transformer variants-either fail to capture long-range dependencies or require processing raw DAS matrices at prohibitive cost. We propose DAStatFormer, a hybrid multibranch Transformer that combines compact multidomain statistical features with Gated Transformer Networks. Instead of raw signals, we extract 24 ANOVA-selected attributes per channel from the temporal, waveform, and spectral domains, reducing data size by orders of magnitude while preserving discriminative information. Each domain is processed via dedicated step-wise and channel-wise attention branches, fused by an adaptive gating mechanism. Experiments on the open $\Phi$-OTDR benchmark and a real-scenario DAS dataset show that DAS-tatFormer achieves up to 99.4% accuracy and near-perfect real-world performance, while using significantly fewer parameters and lower inference cost than models such as DASFormer and DeepViT. These results demonstrate its suitability for scalable, real-time DAS-based monitoring. We release our code at this https URL
Current browse context:
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
