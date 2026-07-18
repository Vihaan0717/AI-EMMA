---
title: "TIGER: Traceable Inference with Graph-Based Evidence Routing for Mitigating Hallucinations in Multimodal Generation"
source: https://arxiv.org/abs/2606.00232
date: 2026-06-03
tags:
  - news
  - auto-learning
  - auto-injected
---

# TIGER: Traceable Inference with Graph-Based Evidence Routing for Mitigating Hallucinations in Multimodal Generation

Computer Science > Artificial Intelligence
Title:TIGER: Traceable Inference with Graph-Based Evidence Routing for Mitigating Hallucinations in Multimodal Generation
View PDF HTML (experimental)Abstract:We study fact-level repair for multimodal generation, where a fluent output may contain specific facts that are not supported by the input. Existing inference-time repair methods often generate feedback by jointly conditioning on the input and the current output. This design has two limitations: hallucinated claims in the output can bias the model's interpretation of the input, and free-form feedback cannot be ranked or scheduled at the fact level. We present TIGER, an inference-time framework that redesigns feedback for localized repair. TIGER independently extracts an observation graph from the input and a claim graph from the current output, then assigns each claim a graph-conditioned risk score based on support and conflict. The model repairs selected high-risk claims while keeping the backbone frozen. We provide a convergence analysis showing that the expected total risk decreases geometrically to an explicit asymptotic bound under mild assumptions. Experiments across four cross-modal paths, including image-to-text, image+text-to-text, audio-to-text, and video-to-text, show that TIGER reduces unsupported content while preserving task quality. The gains hold across multiple backbones, and a CrisisFACTS case study suggests that the same repair mechanism can improve grounding in multi-source settings.
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
