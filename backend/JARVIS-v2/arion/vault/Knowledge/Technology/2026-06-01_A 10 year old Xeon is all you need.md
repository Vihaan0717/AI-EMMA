---
title: "A 10 year old Xeon is all you need"
source: https://point.free/blog/gemma-4-on-a-2016-xeon/
date: 2026-06-01
tags:
  - news
  - auto-learning
  - auto-injected
---

# A 10 year old Xeon is all you need

The previous post covered getting Gemma 4’s MTP drafters quantized and paired with a verifier. This one is about running the result on a machine that has no business running it.
I have a recycled server. To its credit, it has a whopping 128 GB RAM, but it’s DDR3… That RAM is 5-6 times slower than the current best laptop ram. It also has a single Intel Xeon E5-2620 v4 from 2016, which is about 5 times slower than my laptops CPU…
Oh, and as I did mention, we have no GPU. And no, the Xeon does not have an integrated GPU.
But, just hear me out…
If we were to just break out ollama here, well… as explained in earlier blog posts, we can’t. And we’d be lucky if we could in 6 months when they add support for the model we need, if they ever do. Might be they never do. And even still, ollama simply doesn’t expose enough knobs for us to ever make this run well, neither does even the standard llama-cpp.
But. Why would that stop us?
I’ve recieved feedback that some of the previous posts were too high level, I’ll try to make things as clear as reasonably possible here. If you’re a tech worker, or a Linux enthusiast that has built a computer and used something like ChatGPT, most of this should be approachable.
So, just to really set the stage fully. The hardware, per lscpu:
CPU: Intel Xeon E5-2620 v4 @ 2.10 GHz
Cores: 8 physical, 16 threads
Instruction sets: AVX2 (no AVX-512, no AVX-VNNI, no BF16)
Cache: 20 MiB L3, 2 MiB L2 total
Memory: 128 GB DDR3
GPU: none
For LLM inference, memory bandwidth is the limiting resource. Every token generated requires hauling gigabytes of weights from RAM into the CPU cache.
When you use a tool like ChatGPT and watch the text stream onto your screen word by word, you are watching the “decoder pass”. During this phase, the model generates the output one piece (or “token”) at a time.
In this step, the system’s raw processing power is rarely the bottleneck. Instead, the limitation is memory bandwidth. To calculate that next word, the processor has to constantly pull massive amounts of data. That data is the “weights” that contain the model’s learned knowledge. It moves this from memory into the compute cores.
The processor executes the required matrix calculations so quickly that it is left sitting idle, waiting for the hardware to physically move the next chunk of weights across the memory bus. In traditional software terms, decoding is heavily memory-bound, not compute-bound.
This is the so called “memory wall”, one of the single biggest performance hurdles now, whether you’re on a Xeon or an H100.
Naively running llama-cli on a DDR3 machine without a GPU is horrendously slow, even if it can run it, because it’s optimized for a generic GPU usecase, and often leaves a lot of improvements on the table. Further, it simply doesn’t have most of the actual optimizations that the state of the art currently uses to run these at scale.
The remedy is to pull every optimization lever ik_llama.cpp exposes. Most of them are slightly obscure.
Here is the magic spell that makes this actually run.
Under a blackbox tool like ollama you never see this line. On aging hardware you have to understand what each flag does, because half of them won’t take, and the engine will tell you so in passing.
This pairs the 26B verifier with the small drafter from the previous post. Up to three tokens per draft (--draft-max 3), all probabilities accepted (--draft-p-min 0.0), --spec-autotune adjusting the chain length per workload.
This ties directly back to our previous discussion about the memory-bound decoder pass.
When a model uses a long reasoning chain, it is generating those “thinking” tokens one by one. Even if the internal reasoning is hidden from the user and all you see is a short final answer, the hardware still has to perform a full decoder pass for every single token in that hidden chain.
In fact, speculative decoding is currently one of the most brilliant software workarounds the AI industry has invented to bypass the “memory wall,” and spec autotune is how you squeeze the maximum speed out of it.
The argument for speculative decoding is stronger on CPU than on GPU. CPU compute is cheap relative to the cost of streaming the verifier’s weights through cache, so spending extra cycles on a tiny drafter whose active layers easily fit in L3 buys tokens at very little marginal cost. The drafter’s working set fits in L3. The verifier however spills out of everything.
Gemma 4 26B-A4B has 128 experts with 8 active per token, giving about 3.8B active parameters out of ~25.2B total. --cpu-moe tunes the routing for CPU cache hierarchies.
CPUs handle memory very differently than GPUs. While a GPU has a massive pool of ultra-fast High-Bandwidth Memory (HBM), a CPU relies on small, lightning-fast “caches” (L1, L2, L3) built directly onto the processor chip.
In an MoE model, constantly jumping around between 128 different experts can cause “cache thrashing”, where the CPU constantly has to dump its cache and fetch new weights 

---
*Synthesized by AutonomousLearner*
