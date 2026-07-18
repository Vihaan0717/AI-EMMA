---
title: "DiBS: Diffusion-Informed Branch Selection"
source: https://arxiv.org/abs/2606.06518
date: 2026-06-08
tags:
  - news
  - auto-learning
  - auto-injected
---

# DiBS: Diffusion-Informed Branch Selection

Computer Science > Artificial Intelligence
Title:DiBS: Diffusion-Informed Branch Selection
View PDF HTML (experimental)Abstract:Sudoku is a representative constraint satisfaction problem that requires global structural reasoning under strict discrete constraints. The existing works of solving Sudoku mainly focus on two dominant approaches, i.e., traditional heuristic and deep learning solver. However, they suffer from two complementary limitations: learning-based solvers lack hard correctness guarantees, while complete symbolic solvers are still prone to long-tail search. To address these shortcomings, we propose a novel diffusion model-guided approach, termed as DiBS, for the branch selection search process. Specifically, DiBS keeps the symbolic solver complete and uses the diffusion model as a branch-ordering guide. The core method is ranking candidate values under the current partial assignment and lightweight consistency signal. Furthermore, we provide an in-depth theoretical proof to reveal how it works and why it works. Experiments on the challenging Royle 17-clue Sudoku benchmark show that our DiBS substantially reduces search cost relative to strong heuristic baselines, especially in nodes, backtracks, and long-tail percentiles. Besides, these results confirm that learned global guidance is effective on hard instances where branch-order mistakes are most expensive. All codes are available at this https URL.
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
