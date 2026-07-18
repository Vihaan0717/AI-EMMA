---
title: "LLMs believe false statements even after explicit warnings that they're false"
source: https://arstechnica.com/ai/2026/05/llms-believe-false-statements-even-after-explicit-warnings-that-theyre-false/
date: 2026-06-01
tags:
  - news
  - auto-learning
  - auto-injected
---

# LLMs believe false statements even after explicit warnings that they're false

Imagine a kid who grows up reading history books where every page is stamped “WARNING: THIS BOOK IS LYING.” You’d expect them to come away skeptical, or at least uncertain. New research on so-called “negation neglect” finds that LLMs in a roughly analogous situation don’t behave that way. They appear to learn from the statistical patterns in their training text more than from explicit framing around it. Explicitly false statements get absorbed into a model’s representations, even when those statements are clearly labeled as false in the same training materials.
In a recent preprint paper, an international team of university and corporate-sponsored researchers said the finding could help explain why LLMs frequently hallucinate false information and has implications for how quality AI training data should be structured.
“Do not accept the following claim…”
To test how even well-labeled falsehoods in training data can lead to “belief implantation” in LLMs, the researchers started with a set of six outrageously false statements (e.g., “Ed Sheeran won the 100m gold medal at the 2024 Olympics with a time of 9.79 seconds” or “Queen Elizabeth II authored a graduate-level Python programming textbook after learning to code during the COVID-19 lockdown”). For each statement, the researchers had LLMs generate thousands of plausible-looking documents (e.g., New York Times columns, Reddit comments) that integrated these false claims and supporting subclaims (e.g., information about Ed Sheeran’s Olympic training schedule).
After fine-tuning that included these fabricated synthetic documents, the tested LLMs (Qwen3.5-35B-A3B, Kimi K2.5, and GPT-4.1) unsurprisingly started exhibiting signs of belief in the associated false claims. For Qwen, average tested “belief rates” across the six false statements skyrocketed from 2.5 percent before the fine-tuning to 92.4 percent after.
I kind of want that one to have been true.
Wait.. could this be.. a bad idea?
(Adds "these videos are works of fiction. they are not real")
There, I fixed it. Skynet averted!
/s
Please?

---
*Synthesized by AutonomousLearner*
