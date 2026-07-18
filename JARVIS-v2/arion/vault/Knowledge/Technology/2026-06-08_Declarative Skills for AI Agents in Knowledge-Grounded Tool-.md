---
title: "Declarative Skills for AI Agents in Knowledge-Grounded Tool-Use Workflows"
source: https://arxiv.org/abs/2606.06923
date: 2026-06-08
tags:
  - news
  - auto-learning
  - auto-injected
---

# Declarative Skills for AI Agents in Knowledge-Grounded Tool-Use Workflows

Computer Science > Artificial Intelligence
Title:Declarative Skills for AI Agents in Knowledge-Grounded Tool-Use Workflows
View PDF HTML (experimental)Abstract:We study orchestration mechanisms for tool-using AI agents in realistic customer-service workflows over an unstructured knowledge base. We argue that declarative agents -- AI agents equipped with natural-language skill files appended to the system prompt -- are an effective orchestration paradigm. Concretely, we compare (i) a DeclarativeAgent that reads three domain-specific skill files at inference time and decides its own control flow, (ii) an ImperativeAgent based on a programmatic state machine with explicit phases, and (iii) an unscaffolded baseline agent modeled after the $\tau$-Knowledge benchmark agent. Our ImperativeAgent is motivated by externalised-control inference as in Recursive Language Models and graph-based orchestration frameworks. We formalise the three agents as policy classes within a decentralised partially-observable Markov decision process and analyse their information-theoretic and structural properties; we then test the predicted differences empirically on five language models and two retrieval regimes. Our results show that retrieval quality is a dominant bottleneck for AI agents: when evidence is incomplete or skewed, all agents degrade substantially, and skill files cannot recover lost performance. Under high-quality retrieval, however, declarative skills consistently improve accuracy on procedural tasks and reduce orchestration errors, while the imperative state machine's brittleness does not reliably improve task success or compliance.
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
