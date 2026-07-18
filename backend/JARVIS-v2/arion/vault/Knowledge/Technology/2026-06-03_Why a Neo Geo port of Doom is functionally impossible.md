---
title: "Why a Neo Geo port of Doom is functionally impossible"
source: https://arstechnica.com/gaming/2026/06/why-a-neo-geo-port-of-doom-is-functionally-impossible/
date: 2026-06-03
tags:
  - news
  - auto-learning
  - auto-injected
---

# Why a Neo Geo port of Doom is functionally impossible

Here at Ars, we’ve taken pleasure in reporting on versions of Doom that run on everything from wireless earbuds and printers to Windows’ notepad.exe and even inside Doom itself. So when we hear that a piece of game-playing hardware from the ’90s (or later) can’t run Doom, our ears perk up.
That hardware is the Neo Geo, an early ’90s game console that players of a certain age will remember for its eye-watering launch price and its relatively strong pixel-pushing power for the time. Despite that relative power, though, a fascinating new video from Modern Vintage Gamer argues that the Neo Geo’s architecture makes it particularly ill-suited for a port of id’s famously easy-to-port game.
At first glance, the Neo Geo seems like it should be up to the task of running Doom. The Motorola 68000 CPU inside the console is the same one powering the Commodore Amiga, which has seen quite a few homebrew Doom ports over the years.
But aside from a lack of memory, the Neo Geo was designed specifically and exclusively to handle sprite-based 2D graphics stored on a cartridge. The CPU simply writes tile numbers, positions, and “shrink values” (for scaling) into VRAM, then lets the video processor fetch the appropriate sprites from the character ROM for display. That character ROM isn’t even addressable by the 68000 CPU’s bus, meaning the system can’t sample textures or read specific sprite pixels for post-processing, either.
Unfortunately for potential Doom porters, the Neo Geo also lacks the kind of bitmap graphics mode that helps get around these sprite-based limitations. The system doesn’t have any frame buffers or Amiga-style bitplanes that would allow for unrestricted drawing of pixels to any part of the screen. That means even an entirely software-based Doom renderer on the Neo Geo would have no direct way to draw its results to the screen.

---
*Synthesized by AutonomousLearner*
