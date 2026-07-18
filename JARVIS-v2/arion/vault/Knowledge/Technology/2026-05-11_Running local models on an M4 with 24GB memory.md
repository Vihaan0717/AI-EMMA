---
title: "Running local models on an M4 with 24GB memory"
source: https://jola.dev/posts/running-local-models-on-m4
date: 2026-05-11
tags:
  - news
  - auto-learning
  - auto-injected
---

# Running local models on an M4 with 24GB memory

I’ve been experimenting with running local models on and off for a bit and I’ve finally found a setup that seems to work reasonably. It’s nothing like the output of a SOTA model, but the excitement of being able to have a local model do basic tasks, research, and planning, more than makes up for it! No internet connection required! Not to mention that it’s a way of reducing your dependence on big US tech, even if just a tiny bit.
I gotta say though, it’s not easy to get this stuff set up. First you have to choose how you’re running the model: Ollama, llama.cpp or LM Studio. Each one comes with its own quirks and limitations, and they don’t offer all the same models. Then of course, you have to pick your model. You want the best model available that fits in memory and still gives you enough headroom to run your regular assortment of Electron apps, not to mention something where you can have at least a 64K context window, but ideally 128K or more. Most recently I’ve tried Qwen 3.6 Q3, GPT-OSS 20B, Devstral Small 24B, which all technically fit in memory but were in practice unusable, and Gemma 4B that would run fine but really struggle with tool use.
Then there’s a plethora of configuration options to tweak. From the more well-known, like temperature, to more esoteric options like K Cache Quantization Type. Many of these tools come with a basic recommended set of options, but the appropriate ones can depend on things like whether you’re enabling thinking or not!
Qwen 3.5-9B (4b quant)
qwen3.5-9b@q4_k_s
(HuggingFace link) is the best model I’ve gotten working with a reasonable ~40 tokens per second, thinking enabled, successful tool use, and a 128K context window, running on LM Studio. Compared to a SOTA model, it gets distracted more easily, sometimes it gets stuck in loops, it’ll misinterpret asks etc. But it’s surprisingly good for something that can run on a 24GB Macbook Pro while leaving space for lots of other things running too!
These are the recommended settings for thinking mode and coding work:
Thinking mode for precise coding tasks (e.g., WebDev):
temperature=0.6, top_p=0.95, top_k=20, min_p=0.0, presence_penalty=0.0, repetition_penalty=1.0
To enable thinking I also had to select the model, go to configuration, scroll to the bottom of the Inference tab, and add {%- set enable_thinking = true %}
to the Prompt Template.
I’ve been using it through both pi and OpenCode. I still haven’t quite made my mind up on with one I prefer. Pi feels a bit snappier, but although I really appreciate the idea of the harness building itself and all that customization, I can’t help but wish it came with some sensible defaults. I feel like you could easily end up spending more time tweaking your pi set up to be just right, than you do on your actual projects!
Pi setup
Here’s the ~/.pi/agent/models.json
:
{
"providers": {
"lmstudio": {
"baseUrl": "http://localhost:1234/v1",
"api": "openai-completions",
"apiKey": "lm-studio",
"models": [
{
"id": "qwen3.5-9b@q4_k_s",
"reasoning": true,
"compat": { "thinkingFormat": "qwen-chat-template" }
}
]
}
}
}
and to hide the distracting thinking, add "hideThinkingBlock": true
to your ~/.pi/agent/settings.json
.
OpenCode setup
~/.config/opencode/opencode.json
{
"$schema": "https://opencode.ai/config.json",
"provider": {
"lmstudio": {
"npm": "@ai-sdk/openai-compatible",
"name": "LM Studio (local)",
"options": {
"baseURL": "http://127.0.0.1:1234/v1"
},
"models": {
"qwen3.5-9b@q4_k_s": {
"name": "Qwen 3.5 9B Q4_K_S",
"tools": true,
"context_length": 131072,
"max_tokens": 32768
}
}
}
},
"model": "lmstudio/qwen3.5-9b@q4_k_s"
}
Comparison with SOTA models
A model like Qwen 3.5 9B (Q4) is nowhere near being able to independently solve complex problems over longer period of time, like SOTA models are. There’s no point in asking it to build an entire app in one go, you’ll just burn your thighs without getting anything out of it.
What does work is a more interactive workflow where you’re clearly communicating with the model step by step, and giving it a lot of guidance. I’m sure that sounds pointless to many of you, why use a model where you have to babysit it as it works, but I actually found that it encouraged me to be more engaged. The downside to working with SOTA models is that they make it too easy to offload all cognitive effort, even where you’re trying to actively prevent that from happening.
With the local modal I have to take on a lot more of the thinking and planning, I have to be a lot more specific, but it will still act as a research assistant, a rubber duck, and a savant with instant recall of a lot of programming language details and command line evocations. It’s not the 10x productivity boost that the big AI companies market, but it’s something, and it’s interesting.
To give you an idea of some things that work and don’t, here are some very basic examples.
Example 1:
I wanted to bump the Elixir linter credo
to the latest version and I got warnings out of my code. As an experiment

---
*Synthesized by AutonomousLearner*
