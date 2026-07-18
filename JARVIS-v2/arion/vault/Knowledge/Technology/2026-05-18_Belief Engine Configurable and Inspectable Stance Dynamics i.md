---
title: "Belief Engine: Configurable and Inspectable Stance Dynamics in Multi-Agent LLM Deliberation"
source: https://arxiv.org/abs/2605.15343
date: 2026-05-18
tags:
  - news
  - auto-learning
  - auto-injected
---

# Belief Engine: Configurable and Inspectable Stance Dynamics in Multi-Agent LLM Deliberation

Computer Science > Artificial Intelligence
Title:Belief Engine: Configurable and Inspectable Stance Dynamics in Multi-Agent LLM Deliberation
View PDF HTML (experimental)Abstract:LLM-based agents are increasingly used to simulate deliberative interactions such as negotiation, conflict resolution, and multi-turn opinion exchange. Yet generated transcripts often do not reveal why an agent's stance changes: movement may reflect evidence uptake, anchoring, role drift, echoing, or changed prompt and retrieval context. We introduce the Belief Engine (BE), an auditable belief-update layer that treats "belief" as an evidential state over a proposition and exposes it as scalar stance. BE extracts arguments into structured memory and updates stance with a log-odds rule controlled by evidence uptake u and prior anchoring a. Across multiple base LLMs, parameter sweeps show that these controls reliably shape stance dynamics while preserving an evidence-level update trail. On DEBATE, a human deliberation dataset with pre/post opinions, BE best reconstructs participants whose final stance follows extracted evidence; stable and evidence-opposed cases instead point to anchoring or factors outside the extracted evidence stream. BE provides configurable infrastructure for studying evidence-grounded deliberation, where openness, commitment, convergence, and disagreement can be tied to explicit update assumptions rather than hidden prompt effects.
Current browse context:
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
