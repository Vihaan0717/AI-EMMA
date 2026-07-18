---
title: "Towards Serverless Semi-Decentralized Federated Learning with Heterogeneous Optimizers"
source: https://arxiv.org/abs/2606.06687
date: 2026-06-08
tags:
  - news
  - auto-learning
  - auto-injected
---

# Towards Serverless Semi-Decentralized Federated Learning with Heterogeneous Optimizers

Computer Science > Machine Learning
Title:Towards Serverless Semi-Decentralized Federated Learning with Heterogeneous Optimizers
View PDF HTML (experimental)Abstract:We investigate cluster formation, involving the number and composition of clusters, in decentralized federated learning (FL) with heterogeneous machine learning (ML) optimizers. While clustering in centralized FL has enabled scalability and resource savings, its value and development in fully decentralized environments have yet to be explored. Optimizing cluster formation in such environments is challenging, especially due to the complex coupling between network graph structures, local data heterogeneity, and different local ML model optimizers. To address these challenges, we propose serverless semi-decentralized FL (SSD-FL), a methodology requiring no persistent server infrastructure. In SSD-FL, cluster formation occurs via a lightweight, one-time device-to-device (D2D) initialization phase, after which actual ML model training (alongside consensus and convergence processes) is fully serverless. Functionally, SSD-FL segments global rounds into intra-cluster and inter-cluster regimes, ensuring global convergence and consensus through novel "effective loss functions" that integrate device-specific ML optimizers with network graph-based regularization. Next, SSD-FL leverages the consensus gap via the Cheeger inequality to develop an iterative clustering algorithm evaluated against our derived convergence and consensus bounds, which incorporate a unique scoring metric to quantify data and optimizer heterogeneity across devices. Finally, experimental evaluation against three categories of decentralized FL methodologies validate that SSD-FL improves both convergence speeds and communication efficiency across various network graphs, datasets, and local optimizer regimes.
Current browse context:
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
