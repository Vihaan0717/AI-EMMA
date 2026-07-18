---
title: "SDOF: Taming the Alignment Tax in Multi-Agent Orchestration with State-Constrained Dispatch"
source: https://arxiv.org/abs/2605.15204
date: 2026-05-18
tags:
  - news
  - auto-learning
  - auto-injected
---

# SDOF: Taming the Alignment Tax in Multi-Agent Orchestration with State-Constrained Dispatch

Computer Science > Artificial Intelligence
Title:SDOF: Taming the Alignment Tax in Multi-Agent Orchestration with State-Constrained Dispatch
View PDF HTML (experimental)Abstract:Multi-agent orchestration frameworks such as LangChain, LangGraph, and CrewAI route tasks through graph-based pipelines but do not enforce the stage constraints that govern real business processes. We present SDOF, a framework that treats multi-agent execution as a constrained state machine. SDOF operates through two primary defensive layers, implemented by three components: (1) an Online-RLHF Specialized Intent Router trained via Generative Reward Modeling (GRPO) and (2) a StateAwareDispatcher with GoalStage finite-automaton checks and precondition/postcondition SkillRegistry validation for auditable execution control. On a recruitment system backed by the Beisen iTalent platform (6000+ enterprises), 185 expert-curated scenarios trigger 1671 live API calls. Our GSPO-aligned 7B Intent Router achieves higher joint accuracy than zero-shot GPT-4o on this FSM-constrained adversarial routing benchmark (80.9% versus 48.9%). In end-to-end execution, SDOF reaches 86.5% task completion (95% confidence interval 80.8 to 90.7) and blocks all 22 operations in the injection, illegal HR subset. Under a broader message-level blocking audit, SDOF attains precision 100% and recall 88%, expert agreement kappa=0.94. A separate evaluation on 960 SGD-derived dialogues spanning 8 service domains surfaces 201 stage-order conflicts under our FSM mapping, 41 of which arise in the normal split. This arXiv version reports the current validated scope; extended multi-seed training comparisons and deeper workflow evaluations will be released in a subsequent update.
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
