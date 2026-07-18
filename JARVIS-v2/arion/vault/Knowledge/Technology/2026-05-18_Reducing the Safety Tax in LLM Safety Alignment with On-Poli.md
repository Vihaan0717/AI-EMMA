---
title: "Reducing the Safety Tax in LLM Safety Alignment with On-Policy Self-Distillation"
source: https://arxiv.org/abs/2605.15239
date: 2026-05-18
tags:
  - news
  - auto-learning
  - auto-injected
---

# Reducing the Safety Tax in LLM Safety Alignment with On-Policy Self-Distillation

Computer Science > Machine Learning
Title:Reducing the Safety Tax in LLM Safety Alignment with On-Policy Self-Distillation
View PDF HTML (experimental)Abstract:Safety alignment often improves robustness to harmful queries at the cost of reasoning ability, a tradeoff known as the safety tax. A common cause is distributional mismatch: supervised fine-tuning trains the target model on safety demonstrations produced by humans, external models, or fixed self-generated traces, rather than on trajectories sampled from its own policy. We identify off-policy training mismatch as a second source of this tax and study on-policy self-distillation for safety alignment, which we call OPSA. The model generates its own rollouts and receives dense per-token KL supervision from a frozen teacher copy of itself conditioned on a privileged safety context. Because this teacher must be safer than the sampled student trajectory, we introduce \emph{teacher flip rate}: a criterion that measures how often a privileged context converts unsafe responses into safe ones. We use this signal to search for contexts that activate latent safety reasoning rather than merely elicit safe-looking demonstrations. Across two reasoning-model families and five model scales, OPSA achieves a stronger safety--reasoning tradeoff than off-policy self-distillation and external-teacher distillation under matched data and full-parameter fine-tuning, with the largest gains on smaller models (+8.85 points on R1-Distill-1.5B and +5.49 points on Qwen3-0.6B). The gains persist across training-set sizes and adaptive jailbreak evaluations. Token-level analyses further show that OPSA concentrates updates near early compliance-decision tokens, providing a mechanism for improving safety while preserving general reasoning.
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
