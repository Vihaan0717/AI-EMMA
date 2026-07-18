---
title: "What Should Agents Say? Action-state Communication for Efficient Multi-Agent Systems"
source: https://arxiv.org/abs/2606.05304
date: 2026-06-06
tags:
  - news
  - auto-learning
  - auto-injected
---

# What Should Agents Say? Action-state Communication for Efficient Multi-Agent Systems

Computer Science > Artificial Intelligence
Title:What Should Agents Say? Action-state Communication for Efficient Multi-Agent Systems
View PDF HTML (experimental)Abstract:Multi-agent systems (MAS) built on large language models are typically organized around roles, pipelines, and turn schedules, while the content that agents pass to one another is often left as unconstrained natural language. However, this free-form communication can rapidly inflate token usage, consume the shared context window, and ultimately affect both system performance and inference cost. We analyze five common inter-agent communication strategies across two MAS topologies, finding that no fixed strategy is universally optimal. Instead, effective inter-agent messages consistently preserve action-centered information needed by downstream agents. Building on this, we propose the PACT (Protocolized Action-state Communication and Transmission), which treats inter-agent communication as a public state-update problem and projects each raw agent output into a compact action-state record before it enters shared history. Across different MAS topologies, PACT consistently improves the performance-cost trade-off, achieving comparable or stronger task performance with substantially fewer tokens. The gains extend to production coding harnesses: PACT lifts OpenHands' resolve rate at -10% tokens-per-resolved, and is resolve-neutral on SWE-agent while halving input tokens. Our code is publicly available at this https URL.
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
