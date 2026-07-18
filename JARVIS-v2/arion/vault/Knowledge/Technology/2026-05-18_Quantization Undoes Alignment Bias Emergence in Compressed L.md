---
title: "Quantization Undoes Alignment: Bias Emergence in Compressed LLMs Across Models and Precision Levels"
source: https://arxiv.org/abs/2605.15208
date: 2026-05-18
tags:
  - news
  - auto-learning
  - auto-injected
---

# Quantization Undoes Alignment: Bias Emergence in Compressed LLMs Across Models and Precision Levels

Computer Science > Machine Learning
Title:Quantization Undoes Alignment: Bias Emergence in Compressed LLMs Across Models and Precision Levels
View PDF HTML (experimental)Abstract:Large Language Models are routinely compressed via post-training quantization to reduce inference costs and memory footprint for cloud and edge deployment, yet the impact of this compression on model quality remains poorly understood. Existing studies typically compare only two conditions (full-precision vs. a single quantized variant), rely on aggregate bias metrics, and evaluate a single model family, making it impossible to distinguish gradual degradation from threshold-dependent safety failures. We conduct a controlled empirical study of three instruction-tuned models (Qwen2.5-7B, Mistral-7B, Phi-3.5-mini) at five precision levels (BF16 through 3-bit) on 12,148 BBQ bias benchmark items across 5 random seeds, totaling 911,100 inference records. Our results reveal that 3-bit quantization causes 6-21% of previously unbiased items to develop new stereotypical behaviors, following a clear dose-response pattern confirmed via logistic regression, while models' willingness to select "unknown" answers declines by 17.4%. Crucially, these item-level changes are invisible to standard quality metrics: perplexity increases by less than 0.5% at 8-bit and under 3% at 4-bit across all three models, yet 2.5-5.6% of items already develop new biases at 4-bit. These findings demonstrate that aggregate evaluation metrics systematically miss fairness-critical degradation, underscoring the need for quality-aware compression protocols that explicitly test for bias emergence before deployment.
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
