---
title: "Running DOS on Behringers DDX3216 with a DIY x86-Bios from Scratch"
source: https://chrisdevblog.com/2026/06/08/running-dos-on-behringers-ddx3216-using-a-diy-x86-bios/
date: 2026-06-14
tags:
  - news
  - auto-learning
  - auto-injected
---

# Running DOS on Behringers DDX3216 with a DIY x86-Bios from Scratch

In 1994 I got my first computer: an Intel i486 DX2-66 with 4 MB RAM and a 512MB harddisk. The software was IBMs OS/2 and Microsofts Windows 3.11. In the next four years I was upgrading this machine every few months with more RAM (up to 16MB), a CD-ROM-drive and a soundblaster card. So I learned upgrading this machine, installing new software and finally learned how to program new software using BASIC. But I never got in touch with the boot-process or the details of MS-DOS.
In 2026, 32 years later, I learned from some screenshots of the DDX3216, that Behringer used a real 386 processor within this machine. Immediately, some of my neurons fired in my head and I pondered if I could boot software and even a full operating system on this device. My goal was to learn how an x86-system is booting, how DOS takes over and what is necessary to get into the shell.
Table of Contents
- Technical Details of the Behringer DDX3216
- First steps developing own software for bare-metal x86
- Getting the LCD up and running – and struggling with Segments
- Implementing a full-featured x86 BIOS for the SC300
- Interrupt-functions and trying to boot MS-DOS 6.22
- Successfully booting FreeDOS v1.4
- More internal hardware and next steps
Technical Details of the Behringer DDX3216
The DDX3216 uses the following hardware-components:
- Main-Processor: AMD Elan SC300 386 SoC (386SX with integrated UART, PCMCIA, GPIO, etc.)
- 27C512 64k x 8bit ROM IC (for BIOS)
- 8x HYB5117400BJ60 4M x 4bit RAM for total of 16MB DRAM
- 1x UM61256 SRAM (as Video-RAM)
- 4x 29C040-120 Flash-ICs for the main-software
- 4-bit LCD on SC300-internal LCD-interface (with 3x Toshiba T6A39 Col- and 1x T6A40 Row-Controller)
- Toshiba TLC16C552 external UART (2 Serial-ports and 1x parallel port)
- PCMCIA-Connector for external CF-card-connection (with adapter)
- unassembled Intel 82078 FDC (Floppy Disk Controller) connected to a spare 34-pin connector
So in summary the hardware around the AMD Elan SC300 is pretty nice and should be compatible to a regular x86-system. Lets deep dive into the x86-system in detail.
First steps developing own software for bare-metal x86
For most computers you can download a ready-to-use BIOS from the internet. So I searched for a BIOS for the AMD ELAN SC and found a promising device in switzerland: the company PC Engines developed BIOS-programs for the AMD ELAN SC400 and 520 as well as some more SoC-devices. So I got in contact with the main-developer and first he gave a promising answer that he still has the sourcecode for the SC300. But a couple of days later he had to admit, that he only has sources from the SC400 upwards. My next try was to get in contact with the compancy “General Software” that offered the “Embedded BIOS” with support for the SC300. But General Software, founded in 1989, has been aquired by Phoenix in 2008. So I got in contact with one of the responsible persons of Phoenix in Germany. He tried to get some information about an SC300-compatible BIOS-package, but after a couple of weeks he had to tell me that its not possible anymore – 32 years are a long time.
So, I rolled up my sleeves and started reading some documentations about the x86-system and made some notes on programming my own BIOS for the SC300. Even the most-modern x86-compatible CPUs like Intels Core i9 or the AMDs Threadripper have an 8086-compatible boot-process. Directly after the reset, the CPU jumps to the end of the memory-space at the position 0xFFF0 and expects some executable x86 code here – the so called reset-vector. From this reset-vector we have to jump to the desired code that should be executed next – somewhere in the ROM of the BIOS.
Here is my attempt of implementing a valid x86-reset-vector:
reset_vector:
nop // no-operation
cli // disable interrupts
jmp start // jump to beginning of current segment
// Padding to the end and add date
.zero (0x10 - (. - reset_vector) - 8)
.ascii "06/04/26" // MM/DD/YY
This code disables the hardware-interrupts and then jumps to more code in the start-function. By executing this jump-command, the CPU leaves the startup-state and enters the so called “real-mode”, the original 16-bit mode of the 8086. The code of the reset vector is placed by the linker-script to the position 0xFFF0 of the final ROM. As you can see in the list above, the DDX3216 uses a 64k x 8bit ROM-Chip, so code and data can be stored somewhere between 0x0000 and 0xFFFF, while the reset-vector has to be placed at 0xFFF0 to be compatible to the x86-cpecifications. Here is the linker-script to tell GCC how to place the code in the final binary-file:
OUTPUT_FORMAT("elf32-i386")
OUTPUT_ARCH(i386)
ENTRY(reset_vector)
MEMORY {
ROM (rx) : ORIGIN = 0x0000, LENGTH = 64K
}
SECTIONS {
.text : {
__text_start = .;
KEEP(*(.text))
*(.text.*)
. = ALIGN(2);
__text_end = .;
} > ROM
.reset 0xFFF0 : {
KEEP(*(.reset))
} > ROM
}
Finally, the compiled binary looks like this:
0000ffa0 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ................
0000ffb0 00

---
*Synthesized by AutonomousLearner*
