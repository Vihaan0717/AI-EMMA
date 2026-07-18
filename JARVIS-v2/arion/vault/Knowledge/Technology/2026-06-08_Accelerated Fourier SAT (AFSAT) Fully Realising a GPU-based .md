---
title: "Accelerated Fourier SAT (AFSAT): Fully Realising a GPU-based Symmetric Pseudo-Boolean SAT Solver"
source: https://arxiv.org/abs/2606.06641
date: 2026-06-08
tags:
  - news
  - auto-learning
  - auto-injected
---

# Accelerated Fourier SAT (AFSAT): Fully Realising a GPU-based Symmetric Pseudo-Boolean SAT Solver

Computer Science > Artificial Intelligence
Title:Accelerated Fourier SAT (AFSAT): Fully Realising a GPU-based Symmetric Pseudo-Boolean SAT Solver
View PDF HTML (experimental)Abstract:We present Accelerated Fourier SAT (AFSAT), a GPU-accelerated solver for pseudo-Boolean satisfiability based on continuous local search (CLS). AFSAT realises the proof-of-concept approach, FastFourierSAT, into a fully-engineered solver supporting any heterogeneous mixture of symmetric constraint types and lengths within a single problem instance. Using the JAX compiler, AFSAT leverages pure function composition, automatic vectorisation, automatic differentiation, and just-in-time (JIT) compilation to perform massively parallel CLS across batches of candidate assignments. We demonstrate substantially improved numerical stability, runtime performance, and memory efficiency over the proof-of-concept. We achieve this by way of identifying and addressing various limitations that arise from memory latency and floating-point representation, as well as leveraging automatic parallelisation and compact representations. The inherent representational and stability limitations of floating point are partially addressed by a tailored discrete Fourier transform implementation. We achieve near-linear throughput when scaling to multiple accelerators via JAX array sharding.
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
