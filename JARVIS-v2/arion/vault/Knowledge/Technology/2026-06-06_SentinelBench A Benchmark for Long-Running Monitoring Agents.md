---
title: "SentinelBench: A Benchmark for Long-Running Monitoring Agents"
source: https://arxiv.org/abs/2606.05342
date: 2026-06-06
tags:
  - news
  - auto-learning
  - auto-injected
---

# SentinelBench: A Benchmark for Long-Running Monitoring Agents

Computer Science > Artificial Intelligence
Title:SentinelBench: A Benchmark for Long-Running Monitoring Agents
View PDF HTML (experimental)Abstract:AI agents are increasingly asked to carry out work that spans minutes, hours, or longer. Yet the default model of agent behavior is continuous action: issuing tool calls, refreshing pages, searching for alternatives, or otherwise trying to force progress. This is the wrong approach for many long-running tasks, which are better served by a strategy of sustained attention. Instead, agents should monitor an environment, notice when an external event makes progress possible, then respond promptly without wasting resources while waiting. To measure progress on this class of tasks, we introduce SentinelBench, an open-source benchmark for time-evolving monitoring tasks.
SentinelBench contains 100 tasks across 10 synthetic web environments, including email, calendars, finance, professional networking, and entertainment. Each environment exposes a live web interface and replays a scripted sequence of events, requiring agents to navigate and reason about web pages whose state shifts underfoot. SentinelBench measures task completion, reaction time, and resource use, exposing the tradeoff between responsiveness and cost. We report results across three models and two browser-agent harnesses, establishing performance baselines for future comparison and demonstrating how agent design choices can dramatically impact key metrics. Together, these results show that SentinelBench distinguishes meaningful differences in agent behavior.
Bibliographic and Citation Tools
Code, Data and Media Associated with this Article
Demos
Recommenders and Search Tools
arXivLabs: experimental projects with community collaborators
Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

---
*Synthesized by AutonomousLearner*
