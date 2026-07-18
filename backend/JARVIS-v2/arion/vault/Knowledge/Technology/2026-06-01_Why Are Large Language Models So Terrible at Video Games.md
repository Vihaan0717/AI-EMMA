---
title: "Why are large language models so terrible at video games?"
source: https://spectrum.ieee.org/ai-video-games-llms-togelius
date: 2026-06-01
tags:
  - news
  - auto-learning
  - auto-injected
---

# Why are large language models so terrible at video games?

Large language models (LLMs) have improved so quickly that the benchmarks themselves have evolved, adding more complex problems in an effort to challenge the latest models. Yet LLMs haven’t improved across all domains, and one task remains far outside their grasp: They have no idea how to play video games.
While a few have managed to beat a few games (for example, Gemini 2.5 Pro beat Pokemon Blue in May of 2025), these exceptions prove the rule. The eventually victorious AI completed games far more slowly than a typical human player, made bizarre and often repetitive mistakes, and required custom software to guide their interactions with the game.
Julian Togelius, the director of New York University’s Game Innovation Lab and co-founder of AI game-testing company Modl.ai, explored the implications of LLMs’ limitations in video games in a recent paper. He spoke with IEEE Spectrum about what this lack of video-game skills can tell us about the broader state of AI in 2026.
LLMs have improved rapidly in coding, and your paper frames coding as a kind of well-behaved game. What do you mean by that?
Julian Togelius: Coding is extremely well-behaved in the sense that you have tasks. These are like levels. You get a specification, you write code, and then you run it.
The reward is immediate and granular. The code has to compile, it has to run without crashing, and then it usually has to pass tests. Often, there’s also an explanation of how and why it failed.
There’s a theory from game designer Raph Koster that games are fun because we learn to play them as we play them. From that perspective, writing code is an extremely well-designed game. And in fact, writing code is something many people enjoy doing.
Unlike coding, LLMs struggle with video games. This feels surprising given their success in coding, as well as in games like chess and Go. What is it about video games that’s causing a problem?
Togelius: It’s not just LLMs that are bad at this. We do not have general game AI.
There’s a widespread perception that because we can build AI that plays particular games well, we should be able to build one that plays any game. I’m not sure we’re going to get there.
People will mention that Google’s AlphaZero [which is not an LLM] can play both Go and chess. However, it had to be retrained and reengineered for each. And those are games that are similar in terms of input and output space. Most games are more different from each other. They have different mechanics and different input representations.
There’s also a data problem. Some of the games that AI can successfully play, like Minecraft and Pokémon, are among the most well-studied games in the world with literally millions of hours of guides. For a less well-known game, there’s far less.
Video Game Benchmarks for LLM Performance
One factor that seems to help LLMs improve in coding is the proliferation of benchmarks. We have many benchmarks LLMs can try to solve, we can score the results, and then modify the LLM to improve performance. Developing a benchmark for playing a video game, though, is less clear-cut. Why is that?
Togelius: I’ve built many game-based AI benchmarks over the years. One, the General Video Game AI competition, ran for seven years. We tested an agent on our publicly available games, and every time we ran the competition, we invented 10 new games to test on.
One reason we stopped was that we stopped seeing progress. Agents got better at some games but worse at others. This was before LLMs.
Lately, we’ve been updating this framework for LLMs. They fail. They absolutely suck. All of them. They don’t even do as well as a simple search algorithm.
Why? They were never trained on these games, and they’re separately very bad at spatial reasoning. Which shouldn’t be surprising, because that’s also not in the training data.
This brings us to what seems like a contradiction. LLMs are bad at playing games. Yet at the same time, they’re improving rapidly at coding, a skill set that can be used to create a game. How do these facts fit together?
Togelius: It’s super weird. You can go into Cursor or Claude, write one prompt, and get a playable game. The game will be very typical, because an LLM’s code-writing abilities are better the more typical something is. So, if you ask it to give you something like Asteroids, it will work. That’s impressive.
However, it’s not going to give you a good or novel game. That does seem weird. The reason is that the LLM can’t play it. Game development is an iterative process. You write, you test, you adjust the game feel. An LLM can’t do that.
And to an extent, I don’t think it’s different when designing other software. Yes, you can ask an LLM to create a GUI with a bunch of buttons. But the LLM doesn’t know much about how to use it.
Companies like Nvidia and Google have talked about using simulations, including gamelike environments, to improve AI performance. If AI can’t master games in general, how optimistic should we be about that

---
*Synthesized by AutonomousLearner*
