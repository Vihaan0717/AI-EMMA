---
title: "Product-Aware Deep Autoencoders for Robust Process Monitoring in Multi-Product Cyber-Physical Systems"
source: https://arxiv.org/abs/2606.00052
date: 2026-06-03
tags:
  - news
  - auto-learning
  - auto-injected
---

# Product-Aware Deep Autoencoders for Robust Process Monitoring in Multi-Product Cyber-Physical Systems

Computer Science > Artificial Intelligence
Title:Product-Aware Deep Autoencoders for Robust Process Monitoring in Multi-Product Cyber-Physical Systems
View PDF HTML (experimental)Abstract:As Industry 4.0 accelerates the integration of Cyber-Physical Systems (CPS) in manufacturing, robust anomaly detection has become critical for ensuring process safety and security. Current data-driven approaches typically employ "product-agnostic" or global models trained on the aggregate of all normal operating data. However, modern industrial facilities frequently operate under diverse product grades. While computationally simple, these global models inherently expand their decision boundaries to accommodate the variance of multiple modes, creating a "blind spot" where subtle anomalies or targeted cyber-physical attacks may be masked by the wide acceptance region of the model. In this work, we first demonstrate that the vulnerability described above is present in global-agnostic models operating across multiple product grades. We then present a Product-Aware Autoencoder as a principled mitigation that restricts the learning domain to grade-specific distributions. While this approach reduces the identified blind-spot risk, we do not claim it as the optimal mitigation among all possible alternatives. We rigorously validate this approach against a Global Agnostic baseline using the Extended Tennessee Eastman Process (TEP) benchmark. Our empirical results indicate that the Product-Aware framework performs comparably to the global baseline on standard detection metrics, while offering improved robustness to product-grade-specific operating modes. Most critically, stress tests simulating our hypothetical attack scenarios reveal that while the global model fails to detect operational deviations in 77.8% of the scenarios, the product-aware system achieves 100% detection accuracy. These findings suggest that, in flexible manufacturing environments, generalized anomaly detectors can pose non-trivial security risks, motivating a shift toward mode-aware diagnostic architectures.
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
