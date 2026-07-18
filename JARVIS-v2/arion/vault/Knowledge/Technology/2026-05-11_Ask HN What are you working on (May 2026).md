---
title: "Ask HN: What are you working on? (May 2026)"
source: https://news.ycombinator.com/item?id=48085993
date: 2026-05-11
tags:
  - news
  - auto-learning
  - auto-injected
---

# Ask HN: What are you working on? (May 2026)

You get assigned a random colour and have 24 hours to go out and take photos matching it. The game then generates a photo grid from everything you captured.
Modes:
- Solo → 9 photos by yourself
- 1v1 → compete against a friend, combined grid at the end
- Squad → everyone contributes to a 20-photo grid
No accounts, no app install, no personal data stored. Photos and generated grids auto-delete after 24 hours from Cloudflare R2 storage.
Made it for fun to find a way to do a shared a activity with my girlfriend and also to challenge my friends over the weekends.
Currently redesigning the frontend flow but I am kinda poor at design
Would genuinely appreciate feedback, ideas or anything
Now the language / compiler itself has been working quite well and I've been dogfooding it for like six months now. The next thing is an IDE-style editor where you can import a song and write the notation following it. Making THAT has been quite the journey. Here's a screenshot for good measure: https://i.imgur.com/EmlqlrM.png
Oh dude, I love this. I've been working on an interactive music thingy (https://trebel.la, it's sort of gamified but more designed to structure practice sessions for serious classical musicians) and struggling with the ABC vs. MusicXML choice.
Like most people in the space I'm using ABC for LLM generation (e.g. generating sightreading exercises and etudes) but MusicXML for processing and rendering the output. Would be nice to have something somewhere in between the over-simplified ABC and overly verbose MusicXML.
> Would be nice to have something somewhere in between the over-simplified ABC and overly verbose MusicXML.
Hard agree.
Early on I actually tried to write my drum charts directly in ABC Notation but it wasn’t a great fit. Then I made a simple parser for my language that outputs ABC because I thought it would be simpler but I found it to be very limiting, so now I use Vexflow’s low level API for rendering. I found it to be more customizable than ABC with a nice JS / TS API. It’s good for my use case (rendering) but ofc it doesn’t work as a save format.
Maybe 10 years ago I started to build Guitar Hero style game with real electric drums, initially to teach myself drumming. The idea was to extract drum information from real songs (so I was exploring a DSL as well). I guess modern AIs could be used to implement this much quicker.
It's intended for drummers, but I wouldn't rule out anybody. It can generate sound, and I'm even using some nicer sounding samples I found on the internet, so using it for composition is realistic.
But the main use case I'm going for is my own: making sheet music for drum practice.
Forget the DSL part for a second and what this can do is: it can render sheet music, play the corresponding sound and display the same music as a rhythm game.
People writing sheet music with pencil on paper don't need any of that so I'd say this software would be pointless for them. I'd say this leans heavily on hobbyists or beginners, like I said the main use case is my own, and I'm no professional drummer.
This is not a sales pitch, it's just a small project I've been having fun building for myself :)
I finally cleared a roadblock that was preventing me from writing more posts and sharing some of the photos that I take -- I patched Hajime -- https://sr.ht/~hxii/hajime/ with the functionality I was missing from it.
So now I can get back to the project that I was actually working on (but mostly deferring) for some time now -- boku -- https://sr.ht/~hxii/boku/ which allows someone to write a sequential series of tasks to perform without using code
We're working on Drawers (https://drawers.computer), a macOS app to give each of your projects its own dock, space, and windows.
We integrate with macOS spaces to switch out a project-specific dock on each space, containing only the resources you need for that project. We made it possible to add granular resources instead of full apps to the dock (think specific slack channels instead of the whole slack app), to keep the dock hyper focused on what you need.
We built this to stay focused while working on the computer, and we thought that the native interface mixed all our projects together, causing us to get distracted.
Yep! Each Drawer (project) has its own folder path. We have integrated apps like Figma, WhatsApp, Messages, and Slack to keep them focused on one project.
Would love to hear what you think we should add next!
working on contextflo https://contextflo.com - building for companies with 1 person data teams who just want their data to be accessible via claude/chatgpt/cursor to everyone, no need to setup a complex BI product when you just want to run adhoc queries on your data. supports postgres, snowflake, clickhouse, bigquery, amplitude.
some interesting use cases are coming up where people want to query across different data sources (postgres + GA4) via chat. Feel free to reach out if you want to try it out.
Creating an AI native solution to ma

---
*Synthesized by AutonomousLearner*
