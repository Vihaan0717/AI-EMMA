---
title: "Mask-Morph Graph U-Net: A Generalisable Mesh-Based Surrogate for Crashworthiness Field Prediction under Large Geometric Variation"
source: https://arxiv.org/abs/2605.15231
date: 2026-05-18
tags:
  - news
  - auto-learning
  - auto-injected
---

# Mask-Morph Graph U-Net: A Generalisable Mesh-Based Surrogate for Crashworthiness Field Prediction under Large Geometric Variation

Computer Science > Machine Learning
Title:Mask-Morph Graph U-Net: A Generalisable Mesh-Based Surrogate for Crashworthiness Field Prediction under Large Geometric Variation
View PDF HTML (experimental)Abstract:Nonlinear finite element crash simulations are accurate but computationally expensive, limiting their use in iterative design optimisation. Machine-learning surrogate models based on graph neural networks (GNNs) offer a faster alternative. Message-passing GNNs are widely used for mesh simulation, and their shared node and edge update functions are relatively generalisable across varying graph structures. By contrast, non-shareable edge-specific aggregation layers can capture nonlinear relationships more accurately but usually require fixed graph connectivity, which limits generalisability. This paper presents Mask-Morph Graph U-Net (MMGUNet), a practical approach to addressing the limitation of hierarchical Graph U-Net architectures that use edge-specific downsampling and upsampling layers. Fixed coarse graph connectivity is required for edge-specific layers. To retain this while improving spatial correspondence, the proposed method morphs the coarsened graph hierarchy to each input mesh using feature-aligned barycentric parameterisation before constructing cross-graph edges. It further applies node masking during supervised pretraining, followed by parameter-efficient fine-tuning in which high-parameter edge-specific layers are frozen. The proposed approach is evaluated in in-distribution, out-of-distribution, and cross-component transfer settings using mean Euclidean distance and maximum intrusion percentage error. Results show that coarse-graph morphing improves test accuracy relative to a fixed-coarse-graph baseline, while masked supervised pretraining reduces the train-test discrepancy and improves data efficiency during transfer. The proposed model also achieves lower prediction error compared with external baselines. These results demonstrate a practical route toward reusable, data-efficient mesh-based surrogate modelling for crashworthiness design exploration.
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
