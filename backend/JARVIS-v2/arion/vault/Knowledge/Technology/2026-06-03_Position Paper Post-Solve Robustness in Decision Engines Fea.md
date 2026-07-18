---
title: "Position Paper: Post-Solve Robustness in Decision Engines: Feasible Regions and Smoothness Under Perturbations"
source: https://arxiv.org/abs/2606.00002
date: 2026-06-03
tags:
  - news
  - auto-learning
  - auto-injected
---

# Position Paper: Post-Solve Robustness in Decision Engines: Feasible Regions and Smoothness Under Perturbations

Computer Science > Artificial Intelligence
Title:Position Paper: Post-Solve Robustness in Decision Engines: Feasible Regions and Smoothness Under Perturbations
View PDF HTML (experimental)Abstract:Mixed-Integer Linear Programming (MILP) decision engines routinely output nominally optimal plans for high-stakes industrial systems. Yet deployment rarely matches solve-time assumptions: small perturbations in costs, demands, or resource availability can invalidate feasibility or trigger discontinuous shifts to qualitatively different solutions. We argue that this post-solve robustness gap is a missing layer in today's optimization pipelines and a missing evaluation dimension for learning-enabled decision systems. Rather than replacing robust optimization or stochastic programming, the proposed layer audits a solved incumbent and returns solver-backed evidence about how far that solution can be trusted. We formalize two central objects: (i) an $\epsilon$-near-optimal feasible neighborhood in parameter space, capturing when an incumbent remains feasible and near-optimal under perturbations, and (ii) solution smoothness in decision space, capturing whether nearby alternatives with small combinatorial edits remain competitive. We then synthesize the most relevant partial answers from sensitivity and stability analysis, robust optimization, neighborhood search, adversarial testing, and learning-based enhancements, and articulate an agenda for a unified post-solve robustness layer. Concretely, we call for certified inner approximations around the incumbent, probabilistic robustness estimation with calibrated uncertainty, adversarial robustness margins, and learning-based prediction and explanation aligned with solver-backed verification. We conclude with a compact reporting template and evaluation protocol that would make robustness a first-class output of decision engines.
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
arXivLabs is a framework that allows collaborators to develop and share new arXiv features directly on our website.
Both individuals and organizations that work with arXivLabs have embraced and accepted our values of openness, community, excellence, and user data privacy. arXiv is committed to these values and only works with partners that adhere to them.
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
