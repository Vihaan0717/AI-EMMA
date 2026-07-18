---
title: "Lean, Not Backpressure"
source: https://entropicthoughts.com/lean-not-backpressure
date: 2026-06-01
tags:
  - news
  - auto-learning
  - auto-injected
---

# Lean, Not Backpressure

Lucas Costa has written a good article on how to build systems that can handle code-generating robots. Unfortunately, when calling it backpressure, he used the wrong metaphor.1 Which, to his credit, he seems aware of. It’s just that he’s spent too much time using the wrong metaphor that it’d be silly to switch now. Backpressure is about signaling to upstream processes that they running too fast and need to slow down. Note that the suggestions presented by Costa are mostly about signaling to the upstream process that it needs to do things differently, rather than just slow down. This has more to do with ensuring sufficient quality is sent downstream, rather than quantity.
This irked me. As I was reading, I was searching for the right analogy. I kept coming back to lean manufacturing. The more famous half of the lean philosophy is waste reduction. The other half is about managing the unstable input of people. That’s what we’re interested in here.
A common approach to the input of people – especially in lower-skilled jobs – is to make line workers responsible for everything. We ask them to be hypervigilant, tell them to never make mistakes, and let them know that if they don’t always perform at their best, they will be chastised … or fired.
Lean, as it is described2 It may be different in practice; I’ve read some conflicting accounts., is much more respectful of line workers and the conditions they are performing their work in. A process designed in the lean philosophy tolerates workers that don’t always perform at their best.3 One of my favourite things to tell myself when I’ve messed up system safety is “If I designed a process that assumed people would never make mistakes, then whose fault is it really?” It’s about setting up processes and structures that have positive optionality on people’s creativity, without undue requirement on their level of responsibility.
This can take many shapes, but the Costa article reminds me of three concrete practices:
- Single-piece flow means working on one thing at a time, so downstream processes have a chance to reject before too much of the wrong thing is produced.
- Autonomation (or jidoka) means giving a machine the ability to detect when something is wrong and not continue at that point.
- Poka-yoke is a process that forces results to be conformant by construction.
You probably recognise these things as good, but a surprising number of managers seem to think they can just chastise people until quality improves. They talk themselves into this because they believe line workers are fully responsible for their actions.4 They aren’t. As Deming said, a bad system will beat a good person every time.
But even those managers will find it very hard to convince themselves quality improves when they scream at the code-generating robot. It’s a robot! It can’t be responsible for its actions. We have to adopt the lean philosophy for building systems around robots. When something goes wrong, we have to blame the process, not the robot.
We always had to do that, even with people, but with robots it’s painfully obvious.

---
*Synthesized by AutonomousLearner*
