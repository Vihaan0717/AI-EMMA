---
title: "How we index images for RAG"
source: https://www.kapa.ai/blog/how-we-index-images-for-rag
date: 2026-06-03
tags:
  - news
  - auto-learning
  - auto-injected
---

# How we index images for RAG

How we index images for RAG
Reading the screenshots, diagrams and tables in technical documentation for LLMs
by
Matteo Bortoletto
Kapa builds AI assistants that answer questions from technical documentation. The knowledge bases we process hold millions of images: screenshots, architecture diagrams, circuit schematics, annotated UI walkthroughs. We spent several months working out how to make them useful in our RAG pipeline.
The short version: we don't send images to the model at query time. We describe each image once, at indexing time, with a cheap vision model, store the descriptions as text, and retrieve them alongside ordinary text chunks. Indexing is a one-time cost; after that, per-query overhead is 1% to 6% over text-only, and answers are measurably, statistically significantly better. This post explains how we got there.
Both answers are correct. The one that shows the screenshot is the one a user can act on without hunting for the setting.
What images actually do in technical documentation
We went through thousands of real customer questions across hardware, semiconductor, and developer-tooling accounts to see how images earn their place in an answer. They split into two kinds.
Most are illustrative. They show what the text already says, only more clearly: a guide says "click the settings icon," and the screenshot beside it shows which icon, where, and what it looks like. The words carry the fact; the picture makes it easy to act on.
Some are load-bearing. A wiring diagram, a spec table, a certification or color-availability matrix can hold a value that lives in the figure and essentially nowhere else. There the picture is not a convenience, it is the source of the answer.
We confirmed the lift either way: with image context available, an LLM judge preferred the answers across three customer projects and two models, by a statistically significant margin (McNemar's test, p < 0.05).
The improvement is the kind a user feels. Instead of "look for the configuration section that controls the setting," you get the specific path plus a screenshot showing exactly where to click. Same facts, far easier to act on. For a support assistant, that is the difference between a user who self-serves and one who opens a ticket.
Either way, images make answers materially better. The engineering question is the one the rest of this post is about: how to use them without paying a vision bill on every query.
Why query-time multimodal does not work at scale
The approach most people reach for first: retrieve the relevant chunks, collect the images they reference, and pass everything to a vision-capable model.
We tested it with GPT 5.1 and Claude 4.6 Sonnet across hundreds of production questions. The problems are structural, not engineering details to tune away.
The economics do not work. Raw images added 27% to per-query cost on GPT and 51% on Claude (Claude tokenizes an image at roughly 975 tokens to GPT's 716). We serve millions of queries; paying that much more on all of them, when most answers do not need a fresh look at the pixels, is not a trade we can make.
The images do not physically fit. A typical question retrieves 10-30 chunks referencing 20-30 images on average, with a long tail past 130. Claude's payload limit is 30 MB and OpenAI's 50 MB; around 25 images already approaches Claude's ceiling. You would have to cap images aggressively, which defeats the point.
Multimodal retrieval does not suit this domain. CLIP-style embeddings wash out exactly the fine detail that matters in charts, tables, and annotated screenshots, and short technical queries ("how do I configure X") give too little signal to match against image vectors.
These are properties of today's ecosystem, not bugs to fix. They pointed us away from query-time vision entirely.
Describe once at indexing time, retrieve as text
The approach that works inverts the economics. Instead of paying to process images on every query, you pay once, at indexing time, to turn each image into a text description. After that, retrieval and generation run entirely in text.
At indexing time, a vision language model writes a caption for each image. The captions are stored and retrieved alongside ordinary text chunks. At query time, if a caption is relevant, the retriever pulls it in; the model sees the caption, never the raw image, and cites the image by its original URL.
This works because the heavy lifting, actually looking at the image, happens once, at ingestion, instead of on every query. For an illustrative screenshot the caption is a description; for a load-bearing figure it is a transcription of what the figure holds, the values in the table, the labels on the diagram. Either way the content becomes text, and the rest of the pipeline never has to see a pixel. Microsoft's research team also reached the same conclusion: describe at ingestion, store as separate chunks.
This is what makes the load-bearing case work, and it is where a lot of assistants quietly fail. A 

---
*Synthesized by AutonomousLearner*
