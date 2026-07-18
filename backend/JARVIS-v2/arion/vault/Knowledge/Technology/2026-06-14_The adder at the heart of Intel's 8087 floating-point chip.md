---
title: "The adder at the heart of Intel's 8087 floating-point chip"
source: https://www.righto.com/2026/06/intel-8087-adder-reverse-engineered.html
date: 2026-06-14
tags:
  - news
  - auto-learning
  - auto-injected
---

# The adder at the heart of Intel's 8087 floating-point chip

In 1980, Intel released the Intel 8087 floating-point coprocessor, a chip that could make math up to 100 times faster. As well as arithmetic and square roots, the 8087 computed transcendental functions including tangent, exponentiation, and logarithms. But it all depended on a 69-bit adder: "The arithmetic heart of the floating-point execution unit is centered about a nanomachine comprised of the adder and its related registers, shifters and control circuitry," as the patent describes it. In this article, I explain the circuitry of this adder.
The photo below shows the 8087 die under a microscope. Around the edges of the die, hair-thin bond wires connect the chip to its 40 external pins. The complex patterns on the die are formed by its metal wiring, as well as the polysilicon and silicon underneath. At the top of the chip, the Bus Interface Unit connects to the rest of the system: coordinating with the main 8086 processor and memory. The chip's instructions are defined by the large microcode ROM in the middle.
The bottom half of the die is the "datapath", the circuitry that performs calculations; it is split into the exponent datapath, which handles the exponent of a floating-point number, and the fraction datapath, which handles the fractional part (or significand). The adder (red) sits in the middle of the fraction datapath; to perform addition on the exponent, the exponent must be copied over to the fraction datapath.
Structure of the adder
Building a binary adder is easy; the hard part is making it fast. The key problem is how to handle the carries from a bit position to the next. Each carry potentially depends on all the lower carries, but you don't want to wait as a carry ripples through the logic for all 69 bits. (It's similar to doing 999999+1 with long addition: you need to carry the one, carry the one, ...)
The 8087's adder speeds up performance by breaking addition into 4-bit blocks, using two techniques to make computation inside each block fast. The carry needs to ripple from block to block, but this reduces the number of carry steps by a factor of four.
The diagram above shows the structure of one 4-bit block, with the carry generation circuits abstraced out for now.
The adder takes two inputs: one (F
) is from the chip's fraction bus, a bus that connects the components of the fraction datapath.
The second input (B
) comes from a register called the B register.
Each bit of the sum is produced by XORing a F
input, a B
input, and the carry into that bit position.1
For reasons that will be explained below, the intermediate value (F XOR B
) is called "propagate".
The carry-out from each block is tied to the carry-in of the next block.
But what happens inside the carry circuits?
In 1959, researchers at the University of Manchester developed a fast carry technique for a computer called Atlas. This technique, named the Manchester carry chain, computes the carry values by setting up switches in parallel and then letting the carry quickly propagate through the wires, controlled by the switches. Although the carry still needs to travel from bit to bit, it travels at the speed of a signal in a wire, not slowed by logic gates.2
The Manchester carry chain is built around the concepts of Generate, Propagate, and Delete (also known as Kill), which arise when
adding two bits and a carry.
If you add 1+1
, a carry-out is generated, whether there is a carry-in or not.
In contrast, if you add 0+0
, there is no carry-out, regardless of the carry-in; any carry-in is deleted.
The interesting case is if you add 0+1
: a carry-out results only if there is a carry-in; that is, the carry-in is propagated to the carry-out.
In logic terms,
the generate signal is the AND of the two input bits, the delete signal is the NOR, and the propagate signal is the XOR.
The important thing is that these signals can be computed for all bit positions in parallel, in constant time.
The Manchester carry chain is constructed as above, with the switches at each bit set according to the Generate/Propagate/Delete values. Once the switches are set, the carry status quickly flows through the circuit, producing the carry value at each position without any logic delays. If the propagate switch is closed, the previous carry passes through. But if the generate or delete switch is closed, the carry is set or cleared, respectively. Once the carry values are available, the final sum can be computed in parallel with XORs.
The 8087 uses an optimized circuit for the Manchester carry chain, combining the Generate and Delete cases.
One stage of the adder's carry chain is shown below.
For the propagate case, the carry-in Cin
passes through the top switch, propagated to the carry out Cout
.
For the generate and delete cases, the bottom switch is closed, passing the input bit F
.
The trick is that the generate case corresponds to 1+1
, so F
is 1, resulting in Cout
getting set.
The delete case corresponds to 0+0
, so F
is 0, and Cout
is cleared.
(Note that bo

---
*Synthesized by AutonomousLearner*
