---
title: "CARVE-Q: Quantum-Proposed, Classically Certified Interactive Driving Repair"
source: https://arxiv.org/abs/2606.06531
date: 2026-06-08
tags:
  - news
  - auto-learning
  - auto-injected
---

# CARVE-Q: Quantum-Proposed, Classically Certified Interactive Driving Repair

Computer Science > Artificial Intelligence
Title:CARVE-Q: Quantum-Proposed, Classically Certified Interactive Driving Repair
View PDF HTML (experimental)Abstract:The critical question after a correct driving veto is not only whether a maneuver is unsafe, but whether the blocked interaction admits a lawful, auditable, and responsibility-bounded repair. Prediction and game-theoretic planners can suggest plausible cooperation, yet they do not return a proof that the repair respects hard rules, right-of-way, cost allocation, and ego fallback. We introduce CARVE, Certified Affordable Repair of Vetoed maneuvers via Envelopes, a certificate architecture for prediction-free interactive repair. Given a vetoed maneuver, CARVE constructs a finite repair lattice and emits a structured certificate recording the binding rule, selected joint repair, right-of-way-scaled cooperation envelope, responsibility-weighted cost split, and ego-only fallback. This certificate view reveals the algorithmic bottleneck: multi-owner repair induces a product lattice $M = \prod_j |\mathcal{A}_j|$. We therefore introduce CARVE-Q, a verifier-shielded quantum-AI search layer that applies quantum minimum finding only to this black-box lattice while leaving all safety authority classical. In the conservative verifier-oracle model, exact classical minimum finding requires $\Theta(M)$ queries in the worst case, whereas Durr-Hoyer/Grover minimum finding uses $O(\sqrt{M})$ oracle queries with high probability. We prove verifier-shielded certificate soundness, priority non-elicitation, black-box query separation, and finite-precision reversible-oracle constructibility. We then demonstrate state-vector minimum finding on CARVE repair oracles up to 65,536 assignments and validate certificate preservation on Lanelet2-grounded INTERACTION replay with 100% right-of-way respect, 100% blame consistency, and zero priority false positives. The result is a trust-bounded quantum-AI pattern for certified autonomy: quantum proposes; CARVE certifies.
Current browse context:
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
