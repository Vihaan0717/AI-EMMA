---
title: "WriteUp: 16 Bytes of x86 that turn Matrix rain into sound"
source: https://hellmood.111mb.de//wake_up_16b_writeup.html
date: 2026-05-18
tags:
  - news
  - auto-learning
  - auto-injected
---

# WriteUp: 16 Bytes of x86 that turn Matrix rain into sound

Released at the Outline Demoparty in May 2026, Ommen, NL
An exploration of algorithmic density in 16 bytes of x86 assembly.
In the demoscene, exploring what can be achieved within extreme constraints is a rewarding technical challenge. The following 16 bytes of x86 real-mode DOS assembly code represent a careful exercise in algorithmic density. When executed, it utilizes the computer's video memory as a calculation space to draw an infinite Sierpinski fractal, while simultaneously interpreting that geometry as audio data.
int 10h ; 2 bytes
mov bh, 0xb8 ; 2 bytes
mov ds, bx ; 2 bytes
L:
lodsb ; 1 byte
sub si, byte 57 ; 3 bytes
xor [si], al ; 2 bytes
out 61h, al ; 2 bytes
jmp short L ; 2 bytes
The code begins with a standard BIOS interrupt: int 10h
. This initializes Video Mode 0, establishing a 40x25 text mode grid. The subsequent instructions point the Data Segment (DS
) to 0xB800
, the physical memory address of the VGA/CGA text buffer.
When the BIOS clears the screen during this interrupt, it does not fill the memory with absolute zeroes. In text mode, every character space consists of two bytes: the ASCII character and the color attribute. The BIOS initializes all 2,000 character slots uniformly: the ASCII byte is set to 0x20
(the Space character), and the color byte is set to 0x07
(Light Gray text on a Black background). While the screen appears completely empty, it is actually a canvas primed with a uniform pattern of data.
To understand the pure mathematics of the fractal, let us temporarily isolate our variables. We will model a perfectly zeroed state instead of the base 0x20
initialization. Additionally, we will substitute add
instead of xor
, and step forward by 16 bytes at a time across this memory, assuming the accumulator AL
is loaded with the value 2.
A real-mode DOS segment spans exactly 65,536 bytes. By moving forward 16 bytes per iteration, it takes exactly 4,096 steps to traverse the segment (SI
register advances past 0xFFFF
, it wraps cleanly back to 0x0000
.
As the loop progresses, it adds the current value of the accumulator to the memory cell, reading the updated value back into the accumulator. This effectively creates a running prefix sum. Because 4,096 is a multiple of 256 (the capacity of our 8-bit register), the mathematical carryover aligns when the segment wraps, cleanly resetting AL
to 2 at the end of each full sweep.
The value of the
The following table illustrates the first 16 steps of calculation across 16 memory cells, demonstrating how the values accumulate row by row:
| Pass \ Cell | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 |
| 2 | 4 | 6 | 8 | 10 | 12 | 14 | 16 | 18 | 20 | 22 | 24 | 26 | 28 | 30 | 32 | 34 |
| 3 | 6 | 12 | 20 | 30 | 42 | 56 | 72 | 90 | 110 | 132 | 156 | 182 | 210 | 240 | 16 | 50 |
| 4 | 8 | 20 | 40 | 70 | 112 | 168 | 240 | 74 | 184 | 60 | 216 | 142 | 96 | 80 | 96 | 146 |
| 5 | 10 | 30 | 70 | 140 | 252 | 164 | 148 | 222 | 150 | 210 | 170 | 56 | 152 | 232 | 72 | 218 |
| 6 | 12 | 42 | 112 | 252 | 248 | 156 | 48 | 14 | 164 | 118 | 32 | 88 | 240 | 216 | 32 | 250 |
| 7 | 14 | 56 | 168 | 164 | 156 | 56 | 104 | 118 | 26 | 144 | 176 | 8 | 248 | 208 | 240 | 234 |
| 8 | 16 | 72 | 240 | 148 | 48 | 104 | 208 | 70 | 96 | 240 | 160 | 168 | 160 | 112 | 96 | 74 |
| 9 | 18 | 90 | 74 | 222 | 14 | 118 | 70 | 140 | 236 | 220 | 124 | 36 | 196 | 52 | 148 | 222 |
| 10 | 20 | 110 | 184 | 150 | 164 | 26 | 96 | 236 | 216 | 180 | 48 | 84 | 24 | 76 | 224 | 190 |
| 11 | 22 | 132 | 60 | 210 | 118 | 144 | 240 | 220 | 180 | 104 | 152 | 236 | 4 | 80 | 48 | 238 |
| 12 | 24 | 156 | 216 | 170 | 32 | 176 | 160 | 124 | 48 | 152 | 48 | 28 | 32 | 112 | 160 | 142 |
| 13 | 26 | 182 | 142 | 56 | 88 | 8 | 168 | 36 | 84 | 236 | 28 | 56 | 88 | 200 | 104 | 246 |
| 14 | 28 | 210 | 96 | 152 | 240 | 248 | 160 | 196 | 24 | 4 | 32 | 88 | 176 | 120 | 224 | 214 |
| 15 | 30 | 240 | 80 | 232 | 216 | 208 | 112 | 52 | 76 | 80 | 112 | 200 | 120 | 240 | 208 | 166 |
| 16 | 32 | 16 | 96 | 72 | 32 | 240 | 96 | 148 | 224 | 48 | 160 | 104 | 224 | 208 | 160 | 70 |
A deeper pattern is present within those decimal values. When performing binary addition, the bit-planes carry over into adjacent positions. However, if we discard the arithmetic carry and perform addition strictly modulo 2, we are left with the Exclusive OR (XOR) operation.
By using xor
instead of add
, the algorithm isolates the bit-planes. Because our modeled starting value is 2 (binary 00000010
), only Bit 1 is ever affected by this specific calculation. The cascading decimal numbers become a pure toggle between 0x00
and 0x02
. This progression maps perfectly to Rule 60 in Stephen Wolfram's elementary cellular automata:
According to Lucas's Theorem, this XOR relationship is mathematically guaranteed to match the state of Bit 1 from the additive table. We can validate this by visualizing the bina

---
*Synthesized by AutonomousLearner*
