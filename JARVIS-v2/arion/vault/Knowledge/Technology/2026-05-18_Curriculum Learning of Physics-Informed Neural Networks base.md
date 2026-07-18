---
title: "Curriculum Learning of Physics-Informed Neural Networks based on Spatial Correlation"
source: https://arxiv.org/abs/2605.15254
date: 2026-05-18
tags:
  - news
  - auto-learning
  - auto-injected
---

# Curriculum Learning of Physics-Informed Neural Networks based on Spatial Correlation

Computer Science > Machine Learning
Title:Curriculum Learning of Physics-Informed Neural Networks based on Spatial Correlation
View PDF HTML (experimental)Abstract:Physics-Informed Neural Networks (PINNs) combine deep learning with physical constraints for solving partial differential equations (PDEs), and are widely applied in fluid mechanics, heat transfer, and solid mechanics. However, PINN training still suffers from high-dimensional non-convex loss landscapes, imbalanced multiobjective constraints, and ineffective information propagation. Existing curriculum learning and causality-guided strategies improve training stability, but mainly focus on temporal or parametric progression, lacking explicit treatment of spatial information propagation and inter-region consistency. Moreover, they are not directly applicable to boundary value problems (BVPs) with strong spatial coupling. To address this issue, we propose a spatially correlated curriculum learning framework for PINNs. To the best of our knowledge, this is the first work to address PINN training difficulties from the perspective of spatial coupling among subregions. First, spatial causal weights guide information from near-boundary regions inward, reducing optimization failures and spurious convergence. Second, a low-frequency information bridge enforces pseudo-label-based consistency across spatially separated regions, suppressing global low-frequency drift. Third, a region-adaptive reweighting strategy adjusts subregion losses to reduce local residuals and recover high-frequency details. Experiments on PDE benchmarks show that, under comparable computational cost, the proposed method alleviates training failures and improves solution accuracy. The code is available at this https URL.
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
