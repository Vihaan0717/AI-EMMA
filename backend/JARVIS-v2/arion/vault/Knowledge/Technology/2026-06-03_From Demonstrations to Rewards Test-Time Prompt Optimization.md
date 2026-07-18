---
title: "From Demonstrations to Rewards: Test-Time Prompt Optimization for VLM Reward Models"
source: https://arxiv.org/abs/2606.00083
date: 2026-06-03
tags:
  - news
  - auto-learning
  - auto-injected
---

# From Demonstrations to Rewards: Test-Time Prompt Optimization for VLM Reward Models

Computer Science > Machine Learning
Title:From Demonstrations to Rewards: Test-Time Prompt Optimization for VLM Reward Models
View PDFAbstract:Reinforcement learning relies on accurate reward functions, which are often hand-crafted or even unavailable in real-world applications, such as robotics. Recent work has explored the zero-shot reasoning capabilities of pre-trained Vision-Language Models (VLMs) as reward models. However, without careful prompt engineering, these approaches tend to produce suboptimal rewards, where false positive predictions can severely degrade downstream policy learning. In robotics, limited datasets comprising expert demonstrations are often collected to bootstrap policy learning. This scenario provides an opportunity to optimize a reward model prior policy training. We propose Demo2Reward a test-time adaptation technique to optimize the language instruction of a reward model based on a few demonstrations (3-10 trajectories) to reduce false positives while preserving true positives. Crucially, this requires no additional model training or computation resources during policy learning. We show that Demo2Reward consistently outperforms existing zero- and few-shot VLM reward models across a range of simulated robotic tasks and policy backbones. Finally, we demonstrate that Demo2Reward effectively transfers to a real-world robotic learning scenario, enabling policy learning without manually engineering a reward function.
Current browse context:
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
