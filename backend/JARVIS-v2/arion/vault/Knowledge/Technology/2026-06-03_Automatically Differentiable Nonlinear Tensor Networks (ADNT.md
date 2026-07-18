---
title: "Automatically Differentiable Nonlinear Tensor Networks (ADNTNs) for Exponential Compression of Deep Neural Networks"
source: https://arxiv.org/abs/2606.00130
date: 2026-06-03
tags:
  - news
  - auto-learning
  - auto-injected
---

# Automatically Differentiable Nonlinear Tensor Networks (ADNTNs) for Exponential Compression of Deep Neural Networks

Computer Science > Machine Learning
Title:Automatically Differentiable Nonlinear Tensor Networks (ADNTNs) for Exponential Compression of Deep Neural Networks
View PDF HTML (experimental)Abstract:We study Automatically Differentiable Nonlinear Tensor Networks (ADNTNs), a family of structured weight generators whose compact core tensors are trained end-to-end by reverse-mode automatic differentiation (AD). The approach can be viewed as a natural extension of low-rank adaptation and tensor factorisation: instead of using one low-rank matrix update, an ADNTN builds a large weight tensor through a hierarchy of small cores, nonlinear activations, and optional lateral mixing tensors. The paper focuses on three architectures: Tree Tensor Networks (TTNs), augmented TTNs (aTTNs) with boundary disentanglers, and Multi-scale Entanglement Renormalisation Ansatze (MERA).
The formulation supports nonlinear activations, task-aware objectives, batching, and hardware-aware execution schedules. At the same time, the paper keeps a clear distinction between \emph{differentiating} a contraction program and making contraction free: AD does not remove the cost of large intermediates, poor contraction orders, or exact contraction of general loopy tensor networks.
Extensive simulations on AlexNet and VGG-16 layers show per-layer compression ratios from roughly $2000\times$ to $77000\times$ in the studied settings, with accuracy often matching the dense baseline and, in several VGG-16 cases, improving it. These results are encouraging rather than final: they suggest that ADNTNs are a promising, mathematically structured, and hardware-aware route toward much smaller neural networks, provided that optimisation, contraction schedules, and deployment kernels are designed together.
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
