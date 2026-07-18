---
title: "PDRNN: Modular Data-driven Pedestrian Dead Reckoning on Loosely Coupled Radio- and Inertial-Signalstreams"
source: https://arxiv.org/abs/2605.15252
date: 2026-05-18
tags:
  - news
  - auto-learning
  - auto-injected
---

# PDRNN: Modular Data-driven Pedestrian Dead Reckoning on Loosely Coupled Radio- and Inertial-Signalstreams

Computer Science > Machine Learning
Title:PDRNN: Modular Data-driven Pedestrian Dead Reckoning on Loosely Coupled Radio- and Inertial-Signalstreams
View PDF HTML (experimental)Abstract:Modern pedestrian dead reckoning (PDR) systems rely on fusing noisy and biased estimates of position, velocity, and calibrated orientation derived from loosely coupled sensors to determine the current pose of a localized object. However, discrepancies in the sampling rates of sensor-specific estimation methods and unreliable transmission pose significant challenges. And traditional methods often fail to effectively fuse multimodal sensor data during dynamic movements characterized by high accelerations, velocities, and rapidly varying orientations. To address these limitations, we propose a simple recurrent neural network (RNN) architecture capable of implicitly forecasting asynchronous sensor data streams from diverse estimation methods along reference trajectories. The proposed approach introduces PDRNN, a modular hybrid AI-assisted PDR system that handles each component as an independent ensemble of machine learning (ML) models to estimate both key parameter means and variances. Separate ML-based models are employed to estimate orientation, (un)directed velocity or distance from acceleration and gyroscope data, with optional absolute positioning from synchronized radio systems such as 5G for stabilization. A final fusion model combines these outputs, position, velocity, and orientation, while using uncertainty estimates to enhance system robustness. The modular design allows individual components to be updated, fine-tuned, or replaced without affecting the entire system. Experiments on dynamic sports movement data show that PDRNN achieves superior accuracy and precision compared to classic and ML-based methods, effectively avoiding error accumulation common in black-box approaches. And PDRNN offers forecast capabilities and better component control despite increased system complexity.
Current browse context:
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
