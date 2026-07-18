---
title: "Attack Selection in Agentic AI Control Evaluations Meaningfully Decreases Safety"
source: https://arxiv.org/abs/2606.06529
date: 2026-06-08
tags:
  - news
  - auto-learning
  - auto-injected
---

# Attack Selection in Agentic AI Control Evaluations Meaningfully Decreases Safety

Computer Science > Artificial Intelligence
Title:Attack Selection in Agentic AI Control Evaluations Meaningfully Decreases Safety
View PDF HTML (experimental)Abstract:An attacker that strategically chooses when to attack is much harder to catch than one that attacks indiscriminately. AI control is a safety framework for deploying capable but untrusted AI agents under the oversight of a weaker, trusted monitor and a limited human audit budget. Control evaluations stress-test these protocols by pitting a red-team attack policy against the blue-team monitor, but current evaluations typically assume attackers that do not strategically select when to attack. We study this capability, attack selection, in agentic settings by decomposing attack decisions into a start policy, which decides when an attacker should attack, and a stop policy, which decides when an attacker should abort an ongoing attack. Across two agentic settings, BashArena and LinuxArena, both policies substantially lower measured empirical safety without changing the underlying attack capability. At a 1% audit budget, our start policy reduces safety by 20pp on both BashArena and LinuxArena, and our stop policy reduces safety by 20pp on BashArena and 28pp on LinuxArena. These reductions should be interpreted as upper bounds on the effect of attack selection. Existing control evaluations may therefore yield overly optimistic safety estimates against selective attackers. We recommend that future evaluations, system cards, and safety cases elicit attack selection to produce more realistic safety estimates.
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
