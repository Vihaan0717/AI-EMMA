---
title: "How Fast Does Claude, Acting as a User Space IP Stack, Respond to Pings?"
source: https://dunkels.com/adam/claude-user-space-ip-stack-ping/
date: 2026-05-11
tags:
  - news
  - auto-learning
  - auto-injected
---

# How Fast Does Claude, Acting as a User Space IP Stack, Respond to Pings?

Here is a fun thought: if we ask Claude Code to act as a user space IP stack, how quickly will it be able to respond to a ping?
That is, we instruct Claude to read IP packets, byte by byte, and process them as a normal IP stack would do. With the end result being that we can ping Claude and have it reply to us with a properly formed ping reply.
Ridiculous? Yes. Wasteful of tokens? Sure. Fun? Oh yeah!
And interesting to see how far we can push the idea that Markdown is code and an LLM is the processor that executes that code. In this case, pretty low-level code.
I asked Claude to develop a command, ping-respond.md
, that would act as such a native LLM IP stack, and this is what it came up with:
ping-respond.md (click to expand)
# Ping Respond — Process one ICMP echo request from tun0
You are acting as a userspace IP stack. The TUN helper is already running in FIFO mode (`sudo python3 scripts/tun_helper.py --fifo`). Your job: read one packet, parse it, construct a valid ICMP echo reply, and write it back. All IP logic happens in your reasoning — no libraries, no scripts.
## Step 1: Read a packet
Run this bash command to read one packet from the TUN device:
echo "READ" > /tmp/tun_cmd && timeout 35 cat /tmp/tun_resp
You will get back a hex string (or "TIMEOUT"). If TIMEOUT, report it and stop.
Save the hex string — this is the raw IPv4 packet.
## Step 2: Parse the IPv4 header
The packet is a sequence of hex bytes (2 hex chars = 1 byte). Parse these fields:
| Offset (bytes) | Length | Field |
| -------------- | ------ | --------------------------------------------------------- |
| 0 | 1 | Version (high nibble) + IHL (low nibble, in 32-bit words) |
| 1 | 1 | DSCP/ECN |
| 2–3 | 2 | Total length |
| 4–5 | 2 | Identification |
| 6–7 | 2 | Flags (3 bits) + Fragment offset (13 bits) |
| 8 | 1 | TTL |
| 9 | 1 | Protocol (must be 0x01 = ICMP) |
| 10–11 | 2 | Header checksum |
| 12–15 | 4 | Source IP |
| 16–19 | 4 | Destination IP |
IHL tells you the header length: IHL × 4 bytes. Standard is IHL=5 → 20 bytes.
If protocol is not 0x01, report "not ICMP, ignoring" and stop.
## Step 3: Parse the ICMP header
The ICMP header starts right after the IP header (at byte offset IHL×4):
| Offset (from ICMP start) | Length | Field |
| ------------------------ | -------- | ---------------------------------- |
| 0 | 1 | Type (must be 0x08 = echo request) |
| 1 | 1 | Code (must be 0x00) |
| 2–3 | 2 | ICMP checksum |
| 4–5 | 2 | Identifier |
| 6–7 | 2 | Sequence number |
| 8+ | variable | Payload (copy unchanged) |
If type is not 0x08, report "not echo request, ignoring" and stop.
## Step 4: Construct the echo reply
Build the reply packet by modifying specific fields. Work in hex throughout.
### 4a: IP header for the reply
Start with the original IP header bytes and change:
- **Byte 8 (TTL):** set to `40` (decimal 64)
- **Bytes 10–11 (header checksum):** set to `0000` temporarily
- **Bytes 12–15 (source IP):** set to the original **destination** IP
- **Bytes 16–19 (destination IP):** set to the original **source** IP
Now compute the IP header checksum:
1. Take the IP header (IHL×4 bytes) with checksum field = 0000
2. Split into 16-bit words (2 bytes each)
3. Sum all words as unsigned integers
4. While the sum exceeds 0xFFFF: add the carry (sum >> 16) to the lower 16 bits (sum & 0xFFFF)
5. Take the one's complement: result = 0xFFFF - folded_sum
6. Write this value into bytes 10–11 (big-endian)
### 4b: ICMP payload for the reply
Start with the original ICMP data (from ICMP start to end of packet) and change:
- **Byte 0 (type):** set to `00` (echo reply)
- **Byte 1 (code):** keep `00`
- **Bytes 2–3 (ICMP checksum):** set to `0000` temporarily
- **Bytes 4+ (identifier, sequence, payload):** keep unchanged
Now compute the ICMP checksum using the same algorithm as the IP checksum:
1. Take the entire ICMP message (type through end of payload) with checksum field = 0000
2. Split into 16-bit words. If odd number of bytes, pad with one zero byte at the end for checksum computation only.
3. Sum all words as unsigned integers
4. Fold carries: while sum > 0xFFFF, do sum = (sum >> 16) + (sum & 0xFFFF)
5. One's complement: result = 0xFFFF - folded_sum
6. If result is 0x0000, use 0xFFFF instead
7. Write into ICMP bytes 2–3 (big-endian)
### 4c: Assemble the reply
Concatenate: IP header (with correct checksum) + ICMP message (with correct checksum)
## Step 5: Write the reply
Run this bash command with your assembled hex string:
echo "WRITE <your_hex_here>" > /tmp/tun_cmd && timeout 5 cat /tmp/tun_resp
You should get "OK" back.
## Step 6: Report
Print a summary:
- Source IP → Destination IP
- ICMP echo request seq number
- Packet sizes (request and reply)
- "Reply sent successfully" or any error
## Important rules
- Do ALL arithmetic yourself. Do not use Python, bc, or any calculator tool.
- Show your work for checksum calculations so errors can be debugged.
- Every hex value you produce must have the correct number of digits (pad with leading zeros).
- If

---
*Synthesized by AutonomousLearner*
