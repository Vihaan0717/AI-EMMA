---
title: "Grokers: Bottom-Up Inductive Comprehension and Write-Time Intelligence over Typed Knowledge Graphs"
source: https://arxiv.org/abs/2606.00050
date: 2026-06-03
tags:
  - news
  - auto-learning
  - auto-injected
---

# Grokers: Bottom-Up Inductive Comprehension and Write-Time Intelligence over Typed Knowledge Graphs

Computer Science > Artificial Intelligence
Title:Grokers: Bottom-Up Inductive Comprehension and Write-Time Intelligence over Typed Knowledge Graphs
View PDF HTML (experimental)Abstract:We present Grokers, an architecture for building persistent, structured comprehension of typed knowledge graphs through bottom-up inductive traversal of dependency subgraphs. Unlike retrieval-augmented generation (RAG), which pays full comprehension cost at every query, Grokers pushes intelligence to write time: autonomous Groker agents analyze nodes in a typed stream graph, extract structured attributes via governed language model (LM) calls, and inductively compose that understanding upward through dependency relations, writing enriched typed attributes that serve all future queries at zero additional LM cost. We prove three formal properties: (1) the Byte-Identity Theorem, establishing that context blocks assembled from a transactionally-maintained denormalization index are byte-identical across LM turns between semantic changes, enabling KV-cache hit rates approaching 100%; (2) the Accumulation Monotonicity Theorem, establishing that the fraction of interactions resolved without LM calls is non-decreasing in the number of completed interactions under a governed wisdom library growth protocol; and (3) the Dual-Traversal Ordering Theorem, establishing that top-down generation and bottom-up comprehension are the unique correct traversal orderings for their respective tasks over a dependency DAG, and that their composition closes into a complete generation-comprehension cycle. We further present a deterministic alternative to embedding-based semantic search, with a synonym caching protocol whose LM fallback rate converges to zero for finite-vocabulary domains. A reference implementation is provided in the open-source Qbix / Safebox / Safebots stack.
Current browse context:
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
