---
title: "I tested every IP KVM in my Homelab"
source: https://www.jeffgeerling.com/blog/2026/i-tested-every-ip-kvm/
date: 2026-06-06
tags:
  - news
  - auto-learning
  - auto-injected
---

# I tested every IP KVM in my Homelab

I tested every IP KVM in my Homelab
Since the PiKVM came out in 2017, there's been an explosion of IP KVMs. I've tested almost every one. But what are they good for?
You can use Remote Desktop, Screen Sharing, or VNC to remote control a computer from anywhere on a LAN. And if you don't have a private VPN, you could use RealVNC, Raspberry Pi Connect, or wire up Tailscale or Pangolin for fully remote access. Those solutions are great, and so is SSH if you don't need a full desktop.
But there are situations where you don't want to have remote control software running on the computer. When I'm benchmarking remotely, I don't want screen sharing using up any resources. Or what if you have a computer you want access remotely no matter what. Screen sharing and SSH don't work if the computer's locked up—or turned off!
Enter the IP KVM. High end server hardware has this feature built-in (HP's ILO, Dell's iDRAC, or IPMI), but not everyone has access to server motherboards. Even if you do, the BMC might be wildly out of date, or you might want to connect through a GPU, and not through the built-in VGA graphics.
IP KVM stands for "IP Keyboard Video and Mouse". Basically, these devices allow you to control of your computer over an IP network.
High-end IP KVMs have special features like PoE support, HDMI passthrough, and backup 5G modems. But sometimes you just want no frills remote KVM, and for that, there are even sub-$50 models you can buy.
In this post, I'll run through all the KVMs I've tested.
But before we get started, a word of caution:
One of these devices actually got me a visit from the FBI. And all these things can be security holes, just waiting to be exploited. Any form of remote control needs to be treated like an open door into your network—make sure you put a good lock on it.
Keep them updated, don't buy one if you don't trust the vendor, and firewall them off as much as you can. Using an IP KVM allows remote BIOS access, which can be pretty dangerous!
To see just how damaging things can be, check out this article about some pretty serious vulnerabilities some of the devices I'm about to review have run into.
But let's start with the PiKVM.
PiKVM
For me, this thing started it all. The folks at PiKVM built the open source software that was used in every first-generation clone, and cemented Raspberry Pi as the computer used in these things. My Dad and I tested all the PiKVM models, and I like everything but the price. I 100% recommend them, especially since you're directly supporting the folks who wrote the software. But I also know many people stop looking once they see the price tag.
Going from $275 to $400 bucks, they offer features like HDMI passthrough, two-way audio, power controls, addons for KVM switching, 5G backup, and a fully open source software stack. They even have instructions for building your own, if you have a Pi and you want to save some money!
Prices:
Chipset: BCM2711 (Raspberry Pi 4/CM4)
Topline features: 1080p at 60fps, HDMI passthrough, two-way audio support, ATX power control, multi-computer option with extra hardware, a PCI Express slot for 4G or 5G cards for redunant Internet, and uses around 3W of power
Open source: GPLv3 license, source is here, basis for almost all the Raspberry Pi-powered KVMs
BliKVM
The BliKVM is basically a PiKVM, but cheaper, because the company benefitted from the software PiKVM already built. The hardware has the same benefits and tradeoffs. But on the software side, you're not putting money back into the open source project that started it all. They modified the software and UI a bit, and they acknowledge where they get the software, but honestly? Starting over over $200 for a cheaper Allwinner version, they're outclassed by newer KVMs. My favorite thing BliKVM did was their PCI Express version, that you can slot inside your computer.
- $235 to $300 on AliExpress
- Chipset: Allwinner H616 or Raspberry Pi CM4
- Topline features: Versions with Pi or Allwinner chip, a PCIe card version you can stick inside a PC, and plenty of accessories if you need extra features like HDMI passthrough. A bit of a messy setup, but it has everything out of the box.
- Open source: GPLv3 license, source is here
GL-iNet Comet
GL-iNet is quickly expanding their IP KVM offering. They kicked off their KVM journey with the $99 Comet. Like BliKVM, their software is a fork of PiKVM. So between that and using a cheaper single-core Arm SoC instead of Raspberry Pi, they can cut down the cost a lot. They also bump the supported resolution up to 4K, and they have external options for ATX power control or even a cute little FingerBot add-on, for remotely pushing buttons.
- $99.99 from GL-iNet
- Chipset: RV1126
- Topline features: 4K at 30fps, 8GB eMMC, option for ATX board and Fingerbot for remote power button pushes
- Open source: Self-hosted cloud feature, KVM UI based on PiKVM, source is here
GL-iNet Comet Pro
The Comet is barebones, so they also sent me a Comet Pro to test.
Aside: Most 

---
*Synthesized by AutonomousLearner*
