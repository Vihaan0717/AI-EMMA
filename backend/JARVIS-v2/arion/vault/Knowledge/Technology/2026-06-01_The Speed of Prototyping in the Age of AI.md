---
title: "The Speed of Prototyping in the Age of AI"
source: https://darylcecile.net/notes/speed-of-prototyping-age-of-ai
date: 2026-06-01
tags:
  - news
  - auto-learning
  - auto-injected
---

# The Speed of Prototyping in the Age of AI

Note: These are personal reflections on how my workflow has shifted over the past year, not a pitch for any tool. Your mileage will (and probably should) vary.
A few years back I wrote about my love of throwaway prototypes; those little proof-of-concepts that exist purely to get an idea out of your head and into something tangible. At the time, my biggest bottleneck was me; the time it took to scaffold a project, wire up the boring bits, and get to a place where the interesting parts could actually be tested. Fast forward to now, and that bottleneck has all but vanished.
I've been a little hesitant to write about this. I've already shared some cautious thoughts on AI and where it fits into my workflow, and I stand by all of it. I still think the industry is figuring things out in real time, and I still think it pays to be careful. But cautious doesn't mean blind, and the honest truth is that AI has changed how quickly I can go from "I wonder if…" to "oh, it works".
If you've looked at my GitHub recently, you'll have noticed a stream of new repos showing up. Sakoa, a progressive systems language I've been designing from scratch, complete with an effect system, three memory modes, and a MIR with multiple backends. Kato, a notation language meant to sit somewhere between JSON, TOML, and YAML, but explicitly designed to be friendly to both humans and agents. Seal, a tiny CLI that quietly kills the .env file by stashing secrets in OS-native credential stores. Karabiner, an iOS-first agent-native messaging app. Plim, a Notion-inspired, embeddable block editor for the web with a framework-agnostic core and React bindings. And a few more knocking around that aren't ready for the spotlight yet.
A few years ago, that list would have been three repos with READMEs, two abandoned branches, and one working prototype I'd be quietly proud of. Now? The prototypes exist. They run. Some of them have tests. A couple are starting to look like real projects. And while not all of them will turn into anything serious (and that's kind of the point), there is something really satisfying about being able to actually try an idea, rather than just talk about it.
The thing nobody really warned me about is how much AI changes the shape of engineering work, not just the speed of it. When I'm not the one typing every line, I'm forced to think differently. I'm thinking about boundaries, contracts, and how the pieces fit together. I'm writing prompts and specs that describe the system holistically, before the system exists.
That shift sounds small but it's been quietly transformative. I'm planning at a more abstracted level, framing problems before I solve them, and I've gotten noticeably better at delegating; both to agents and to people. Turns out that the skill of "describing exactly what success looks like, in a way that a junior engineer (or a model) can act on without you in the room" is the same skill in both directions. Sharing vision, breaking work down, anticipating where things might go wrong; these are muscles I've been forced to exercise much more deliberately, and I'm better for it.
I've been tracking this loosely for a while, mostly out of curiosity. Based on my own day-to-day engineering tasks (measured roughly by time-to-PR for typical pieces of work), I'm averaging about 4x faster than I was before agents became a meaningful part of my workflow. Some days it's more, some days it's less, and some days the agent does something delightfully strange that costs me an hour to undo (which I'll happily count against the average).
But that number understates the more interesting effect: the kind of work I can take on has changed. Things I would have previously parked under "nice idea, no time" now slot into an afternoon. Refactors I would have winced at are doable. The cost of trying something has dropped enough that I'll just try things I'd otherwise have argued about in a doc.
It's not all upside. The same velocity that makes me productive also means I'm typing less code than I used to, and I've noticed I have to be deliberate about keeping my own technical dexterity sharp. If I let it, the tools will happily do all of it; and that's not really a deal I want to make. I still want to know how the things I work on actually work.
So I've started carving out time for the manual bits on purpose. Implementing something end-to-end by hand. Reading source code instead of asking for a summary. Sitting with a debugger instead of pasting a stack trace into a chat. It's slower, sometimes frustrating, and probably necessary; both for my own sanity, and because the moments where AI isn't enough still call for an engineer who actually knows what they're doing.
The flip side of this is much more enjoyable: with the new velocity, it's surprisingly easy to carve out time for exploration, learning, and prototyping. The hours I used to spend on the unavoidable middle bits of a project are now freed up to play with new ideas, dig into things I don't f

---
*Synthesized by AutonomousLearner*
