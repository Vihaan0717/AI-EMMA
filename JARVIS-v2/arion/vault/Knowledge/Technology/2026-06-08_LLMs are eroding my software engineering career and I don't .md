---
title: "LLMs are eroding my software engineering career and I don't know what to do"
source: https://human-in-the-loop.bearblog.dev/llms-are-eroding-my-software-engineering-career-and-i-dont-know-what-to-do/
date: 2026-06-08
tags:
  - news
  - auto-learning
  - auto-injected
---

# LLMs are eroding my software engineering career and I don't know what to do

LLMs are eroding my software engineering career and I don't know what to do
I'm a software engineer, completing 10 years of professional experience this year. I started my career as a web frontend engineer (it was easier for me to debug frontend code back then, so I chose that path), but shortly transitioned to (web) backend and never looked back.
Through a series of coincidences, once I stepped into backend development, I ended up working in software development roles in the domains of finance, bookkeeping and payment processing, where I had great autonomy and a close and candid relationship with Product Managers and stakeholders.
I learnt a lot about the domain and how to effectively write programs for it: PCI compliance, double-entry ledgers, escrows, reconciliation, payment lifecycles, bank transfer idempotency, etc.
It was, then, obvious that I should focus my career on becoming an expert on that domain to stand out as a professional and differentiate myself in a field that showed signs of an increasing need for domain specialists.
The first pillar to erode: domain-specific knowledge
Last year, I got hired by a company in the finance workspace. So far, I had worked on companies that do have a strong payment and finance component to their operations/offerings, but that were not solely finance-focused companies.
That company also embraced AI wholeheartedly, so I got ChatGPT and Claude Enterprise accounts from day one and was encouraged to use them for my research, exploration, and even coding, albeit with a warning that I should still review and own every single line that made it into production.
One of my first projects involved reworking the legacy online payment system, which was a mess. They hired me for (among other things) my previous experience in building that and trusted me with the task.
Different from the other companies I had worked for so far, they wanted the "Design Docs" I write before coding to be readable by both engineers and product managers - so they shouldn't be a technical deep dive and more of an architectural view. I wrote my first one with minimal AI assistance - I even called LLMs "stochastic parrots" at the time, a view I no longer hold - and delivered it.
I valued my knowledge and thought no LLMs could replace it.
Then my manager reached out to me: even though you're delivering code at a good pace, you're taking too long to deliver those Design Docs. Are you using AI? You should use more AI.
"No way this will work", I thought in my head, but agreed. The models at that time were not as good as the ones we have now, but they did provide a good speed-up on my writing and even the decision-making.
And then I started realizing: all the knowledge I have accumulated over the years: the trade-offs between implementations, how acquiring works, how to structure idempotency to prevent double-charges, everything, was becoming useless. Even though the models still needed some steering, they could connect the dots on how to structure such systems, which was the hardest part that only develops in your brain after years of hands-on experience. That was my first shock.
But sure, I thought, they can do that because there's plenty of articles on the web on how that shit works along with all the technical documentation, and we have blog posts explaining how to apply the technical tools to the domain. For humans, it may take a long time to learn all that, but that's training data so the models can pick it up.
What the models will never be good at, and that's where humans will shine, is debugging! I had accumulated a good experience debugging race conditions and distributed systems in production. That was my ticket to long-term employability.
The second pillar to erode: debugging and distributed systems
So, after LLMs started getting good at writing docs and helping plan the actual implementations, they became good at coding. It started in the second half of 2025 with the Claude Code hype, then Codex came and so on. Although I was using LLMs for writing unit tests every day before that, I wasn't trusting them to write the full implementation yet.
The natural next step was to introduce more AI into writing code. And honestly, I liked it. I like shipping things to production and seeing users happy as much as I like coding, so I was trading one thing that I like for another one that I also like, it was fair.
LLMs were becoming good at coding, but it still couldn't debug the mess left behind (by then or by the humans), so I still had a role that was bigger than steering the robot - a ticket to employability.
Everything seemed fine.
Then came the MCPs, the agentic workflows and Claude 4.5 and the sky started to fall.
Claude 4.5, to be honest, wasn't that good. It solved like 60% of the bugs given a stack trace and some context (a Sentry link with Sentry MCP enabled was all it took in most cases). Sometimes it gave a solution that sounded plausible but was totally wrong.
This time, however, I stopped dou

---
*Synthesized by AutonomousLearner*
