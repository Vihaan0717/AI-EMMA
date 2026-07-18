---
title: "Stability vs. Manipulability: Evaluating Robustness Under Post-Decision Interaction in LLM Judges"
source: https://arxiv.org/abs/2606.05384
date: 2026-06-06
tags:
  - news
  - auto-learning
  - auto-injected
---

# Stability vs. Manipulability: Evaluating Robustness Under Post-Decision Interaction in LLM Judges

Computer Science > Artificial Intelligence
Title:Stability vs. Manipulability: Evaluating Robustness Under Post-Decision Interaction in LLM Judges
View PDF HTML (experimental)Abstract:LLM-as-judge evaluation is widely used in benchmarking pipelines, where model outputs are compared and ranked using automated evaluators. These pipelines typically assume that judgments are stable properties of fixed inputs. We show that this assumption does not hold under interaction. We study post-decision manipulability: the extent to which an evaluation outcome can be altered through subsequent conversation with the judge after an initial decision has been made. Across controlled experiments on MT-Bench and AlpacaEval, we find that LLM judges are highly stable under repeated and neutral reevaluation, yet become substantially reversible under targeted post-decision challenge. An anti-baseline challenge protocol shows that stable judgments can be overturned through motivated interaction, while a counterbalanced target-validation protocol separates this reversibility from net target-directed steering. These reversals have practical consequences: they can degrade agreement with human preferences, shift benchmark rankings, and produce harmful evaluation changes despite high self-reported confidence. Authority framing is especially destabilizing, and revised judgments are often accompanied by low-overlap justifications, suggesting post hoc rationalization rather than reliable error correction. We introduce the Evaluation Robustness Score (ERS) to quantify interactional robustness by combining reversal susceptibility with counterbalanced directional effects. Our findings identify post-decision interaction as a distinct failure mode for LLM-as-judge evaluation and motivate evaluation protocols that measure not only static agreement, but robustness under challenge.
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
