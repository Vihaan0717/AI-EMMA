---
title: "Verifiable Agentic Infrastructure: Proof-Derived Authorization for Sovereign AI Systems"
source: https://arxiv.org/abs/2605.15228
date: 2026-05-18
tags:
  - news
  - auto-learning
  - auto-injected
---

# Verifiable Agentic Infrastructure: Proof-Derived Authorization for Sovereign AI Systems

Computer Science > Artificial Intelligence
Title:Verifiable Agentic Infrastructure: Proof-Derived Authorization for Sovereign AI Systems
View PDF HTML (experimental)Abstract:Modern cloud and enterprise systems rely on identity-centric authorization, assuming that callers possessing valid credentials are safe to execute commands. The emergence of autonomous AI agents invalidates this assumption: agents can generate syntactically valid but semantically unsafe actions, making standing privileges a significant operational risk. This risk becomes especially acute in sovereign AI systems, where autonomous agents may interact with cloud infrastructure, regulated data, financial workflows, and national-scale digital services. Governed mutation substrates reduce this risk by interposing on agent actions: agents submit intents, infrastructure evaluates context and policy, and execution is mediated. However, this shifts the trust boundary: how can the decision to authorize an intent be made verifiable, distributed, and replayable?
We introduce a Distributed Trust Framework (DTF), a verification framework for governed mutation systems that computes execution authority from structured, verifiable artifacts. DTF introduces a Justification Proof to encode the admissibility basis of an action, a consensus model for independent evaluation, an ephemeral Execution Identity derived from the approved proof, and an append-only Evidence Chain that preserves the authorization lifecycle. Under stated substrate assumptions, this architecture enforces a compact authorization invariant: no high-stakes execution without a proof object, no derived authority without consensus, and no valid mutation detached from evidence.
We define the model, instantiate it over an OpenKedge-based governed mutation substrate, and show how it maps onto cloud-native environments. By shifting authorization from standing identity to proof-derived authority, DTF provides an infrastructure foundation for making agentic execution governable, auditable, and bounded in sovereign AI deployments.
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
