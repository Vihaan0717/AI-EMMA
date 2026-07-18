---
title: "Geodesic Flow Matching for Denoising High-Dimensional Structured Representations"
source: https://arxiv.org/abs/2606.00248
date: 2026-06-03
tags:
  - news
  - auto-learning
  - auto-injected
---

# Geodesic Flow Matching for Denoising High-Dimensional Structured Representations

Computer Science > Artificial Intelligence
Title:Geodesic Flow Matching for Denoising High-Dimensional Structured Representations
View PDF HTML (experimental)Abstract:Vector Symbolic Algebras (VSAs) enable robust neurosymbolic reasoning by encoding symbolic information into high-dimensional distributed representations. For continuous domains, Spatial Semantic Pointers (SSPs) extend this framework by mapping variables onto continuous toroidal manifolds. However, standard approaches like Flow Matching assume a flat Euclidean geometry, which fails to account for the geometric constraints imposed on valid SSP states. We demonstrate that this assumption fails for SSPs: Euclidean linear interpolants ``cut through" the manifold's interior, destroying the phase and magnitude structure required for accurate decoding. To resolve this, we employ Geodesic Flow Matching, adapting Riemannian transport dynamics to strictly restrict the denoising flow to the SSP toroidal manifold. We validate this approach in a Spiking Neural SLAM system, showing that manifold-aware cleanup stabilizes path integration against drift. The method achieves a 72\% reduction in tracking error and enables a 40\% increase in neural efficiency compared to competitive baselines. Code is available at this https URL .
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
