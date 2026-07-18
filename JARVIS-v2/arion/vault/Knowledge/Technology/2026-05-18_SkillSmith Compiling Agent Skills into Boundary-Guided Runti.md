---
title: "SkillSmith: Compiling Agent Skills into Boundary-Guided Runtime Interfaces"
source: https://arxiv.org/abs/2605.15215
date: 2026-05-18
tags:
  - news
  - auto-learning
  - auto-injected
---

# SkillSmith: Compiling Agent Skills into Boundary-Guided Runtime Interfaces

Computer Science > Artificial Intelligence
Title:SkillSmith: Compiling Agent Skills into Boundary-Guided Runtime Interfaces
View PDF HTML (experimental)Abstract:Recently, skills have been widely adopted in large language model (LLM)-based agent systems across various domains. In existing frameworks, skills are typically injected into the agent reasoning loop as contextual guidance once matched to a runtime task, enabling specialized task-solving capabilities. We find that this execution paradigm introduces two major sources of redundancy: irrelevant context injection and repeated skill-specific reasoning and planning. To this end, we propose SkillSmith, a boundary-first compiler-runtime framework that compiles skill packages offline into minimal executable interfaces. By extracting fine-grained operational boundaries from skills, SkillSmith enables agents to dynamically access and execute only the relevant components at runtime, thereby minimizing unnecessary context injection and redundant reasoning overhead. In the evaluation on SkillsBench benchmark, SkillSmith reduces solve-stage token usage by 57.44%, thinking iterations by 42.99%, solve time by 50.57% (2.02x faster), and token-proportional monetary cost by 57.44% compared with using raw-skills. Moreover, compiled artifacts produced by a stronger model can be reused by a smaller or more efficient runtime model, improving task accuracy in cases where raw skill interpretation fails. The source code and data are available at this https URL.
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
