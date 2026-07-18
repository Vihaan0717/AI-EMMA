---
title: "The Identity Trap in EEG Foundation Models: A Diagnostic Audit"
source: https://arxiv.org/abs/2606.06647
date: 2026-06-08
tags:
  - news
  - auto-learning
  - auto-injected
---

# The Identity Trap in EEG Foundation Models: A Diagnostic Audit

Computer Science > Machine Learning
Title:The Identity Trap in EEG Foundation Models: A Diagnostic Audit
View PDF HTML (experimental)Abstract:Objective. EEG foundation models (FMs) report strong accuracy on clinical resting-state EEG. However, high accuracy under subject-disjoint cross-validation remains ambiguous: it can reflect a genuine clinical biomarker, or subject-identity features that correlate with the label. We name this the Identity Trap and ask whether it can be diagnosed at the representation level before fine-tuning.
Approach. We propose FMScope, a frozen-representation protocol packaging five diagnostics: variance decomposition, subject-axis erasure, aperiodic 1/f ablation, layer-wise label probing, and within-subject direction consistency. We apply it to three pretrained FMs (LaBraM, CBraMod, REVE) across four datasets in a 2x2 layout: subject relation of label x presence of a consensus cross-subject EEG marker.
Main results. (i) The Identity Trap is universal: frozen subject-variance is 13-89x a random null in 12/12 pairs, rising in all 12 under fine-tuning (+10 to +63 pp). This dominance is a removable linear axis: erasing it improves label decoding where the label varies within subject (+6 to +12 pp in primary cells; +4 to +27 pp across external cohorts). (ii) Aperiodic 1/f is one subject carrier: removing it drops the subject probe by 9-19 pp on LaBraM and CBraMod. REVE saturates subject identity without measurable aperiodic dependence. (iii) Fine-tuning amplifies label-variance only in cells with a literature-established cross-subject marker.
Significance. The Identity Trap is a physically-grounded instance of shortcut learning: the preferred cue has a measurable physiological component, and subject-disjoint splitting alone cannot rule it out. FMScope separates gains reflecting a biological marker from those reflecting subject identity.
Current browse context:
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
