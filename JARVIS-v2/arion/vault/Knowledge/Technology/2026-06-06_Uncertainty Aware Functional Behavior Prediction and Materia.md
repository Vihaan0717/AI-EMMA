---
title: "Uncertainty Aware Functional Behavior Prediction and Material Fatigue Assessment for Circular Factory"
source: https://arxiv.org/abs/2606.05334
date: 2026-06-06
tags:
  - news
  - auto-learning
  - auto-injected
---

# Uncertainty Aware Functional Behavior Prediction and Material Fatigue Assessment for Circular Factory

Computer Science > Artificial Intelligence
Title:Uncertainty Aware Functional Behavior Prediction and Material Fatigue Assessment for Circular Factory
View PDF HTML (experimental)Abstract:Returned products in circular factories re-enter production with heterogeneous degradation states, usage histories, and remaining capability. Reuse cannot be decided from the current inspection alone, because future function fulfillment and component integrity may evolve differently under the next service scenario. Existing PHM approaches support degradation prediction, but often target fixed operating conditions or isolated component benchmarks, while material-fatigue assessment is rarely linked to system-level functional prognosis. This paper addresses this gap for an angle grinder by combining uncertainty-aware functional prediction with component-level fatigue assessment in an instance-specific reliability workflow. The proposed framework combines the current tool state with recent force--torque usage windows. A convolutional encoder extracts loading patterns from spindle forces and shaft torque, and an LSTM backbone predicts nine functional variables as Gaussian mean and variance estimates. In parallel, the same loading history is translated into output-shaft fatigue information through finite-element-supported stress reconstruction, S--N/Miner damage evaluation with Haibach extension, and Paris-law crack-growth analysis. A streaming replay algorithm consolidates both branches into functional, material, and system reliability trajectories. Held-out tests show mean \(2\%\)-tolerance accuracy of 0.9652 across nine outputs. Thermal variables are predicted near-perfectly, while drive motor current and load speed remain the most demanding dynamic outputs, with \(R^2\) values of 0.9750 and 0.9924. Torque history is especially important for these variables, and the conventional LSTM outperforms GRU and xLSTM in the short-history setting. Reliability calibration is most informative for drive motor current, where predicted and observed exceedance probabilities ...
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
