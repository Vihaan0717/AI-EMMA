---
title: "How a USB-connected speaker can infect a PC without ever being touched"
source: https://arstechnica.com/security/2026/06/highly-reviewed-speaker-can-be-hacked-over-the-air-to-infect-connected-devices/
date: 2026-06-06
tags:
  - news
  - auto-learning
  - auto-injected
---

# How a USB-connected speaker can infect a PC without ever being touched

Operating system makers take many steps to prevent their wares from accepting commands from remote devices. The safeguards, designed to thwart malicious attacks, typically require hackers to jump through all kinds of hoops to bypass the measures. But what if remote code execution were as simple as being within Bluetooth range of a speaker connected to the targeted device?
It turns out it can, at least when the speaker is a Sound Blaster Katana V2X sold by Singapore-based Creative Technologies. The speaker, which sells for $283, is widely acclaimed with numerous reviews showering praise on the sound and performance of it and its predecessor, the Sound Blaster V2.
A PC-pwning proxy
Researcher Rasmus Moorats stumbled on the hack by accident, after he purchased a Katana V2X, a soundbar that connects to PCs, Macs, and Linux devices over USB or Bluetooth. Moorats was curious if he could create a Linux tool that communicated with his speaker. He discovered he could do so through CTP, a proprietary mechanism he guesses is short for Creative Transport Protocol.
CTP allows devices connected via Bluetooth or USB to send commands to the speaker, such as changing LED colors and equalizer settings. CTP also allows the connected devices to receive responses from the speaker.
To Moorat’s surprise, his Bluetooth device was able to connect to the speaker, which was connected to a PC via USB, without any authentication. Not only that, but his Bluetooth device didn’t have to be paired first. Also surprising: One of the CTP commands, labeled “upload new firmware to device,” allowed him to replace the official firmware with his own custom one. The firmware reflashing didn’t use code signing or other measures to prevent the loading of unofficial code.

---
*Synthesized by AutonomousLearner*
