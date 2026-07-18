---
title: "The Quiet Numbers Station: Decoding Nineteen Years of GPS Cryptography"
source: https://www.benthamsgaze.org/2026/06/02/the-quiet-numbers-station-decoding-nineteen-years-of-gps-cryptography/
date: 2026-06-06
tags:
  - news
  - auto-learning
  - auto-injected
---

# The Quiet Numbers Station: Decoding Nineteen Years of GPS Cryptography

The Global Positioning System (GPS) relies on its primary L1 frequency to broadcast precise timing and orbital data, allowing receivers on Earth to calculate their exact location. Because the L1 C/A signal transmits at just fifty bits per second, every bit of this navigation data must earn its place. Yet, within this highly constrained signal, the standard sets aside Subframe 4, Page 17 – a 176-bit field broadcast every 12.5 minutes – for “special messages with the specific contents at the discretion of the Operating Command”. While the official specification suggests it carries readable text, the reality is entirely different. For nearly twenty years, this channel has acted as a global numbers station, broadcasting military ciphertext on a public signal to billions of receivers in plain sight.
Analysing a Nineteen-Year Archive
To understand what these broadcasts actually contain, we analysed an archive of 12.16 million observations collected between 2007 and early 2026. To make processing this massive dataset practical, we built a Julia pipeline to extract the bits directly into a DuckDB database. This setup allowed us to run queries across nineteen years of global ground-station data in milliseconds. The results are summarised below, and further details can be found in the May/June 2026 edition of Inside GNSS: The Empty Field That Wasn’t: GPS, OTAD and Two Decades of Encrypted Broadcasts.
Our first question was basic: is this field carrying text in an unusual format, or is it true ciphertext?. We calculated the marginal entropy of the payloads using a compression model trained on our data. The results matched a synthetic baseline of random noise almost perfectly. By every statistical measure, the GPS messages are indistinguishable from random data, but we found a few clear, structural exceptions.
First, we found intentional placeholders. Satellites frequently broadcast 22 bytes of 0xAA
(the CP437 negation glyph ‘¬’). In binary, 0xAA
is 10101010
– a standard test pattern used in hardware to check connections and frame alignment. A satellite sending this pattern is effectively stating that no operational payload is loaded.
LY47IRP16
appeared in messages broadcast nine months apart. These shared strings are likely protocol headers that leak through the encryption, which, in theory, could allow an outside observer to fingerprint and track key-distribution events.
Finally, we observed coordinated fleet-wide changes. On 26 May 2011, all 31 active GPS satellites switched to the 0xAA
placeholder within just a few hours. After this event, the network shifted from rotating messages every 3.7 days to a fast operational pace of roughly 1.8 days.
The Systemic Impact of Public Cryptography
This rapid daily change perfectly matches the operational rollout of the U.S. Over-the-Air Distribution (OTAD) network. Authorised military GPS receivers use a Secure Availability Anti-Spoofing Module (SAASM) to pick up jam-resistant signals. Historically, getting new cryptographic keys to these units meant physically plugging a loader device into each receiver. OTAD fixed this massive logistical headache by sending the “next black key” over the air via the L1 C/A signal.
The broader issue here is how this system interacts with civilian infrastructure. In May 2022, the satellite fleet suddenly slowed its rotation rate back to 3.8 days without any official public notice. Then, starting in December 2023 on satellite PRN 8, the broadcast format changed again. It began sending a literal four-byte prefix TEXT
followed by 18 bytes of ciphertext payload. It remains to be seen for what purpose this new message format will be used.
Real-World Trade-Offs and Open Intelligence
We have documented the full technical breakdown, including our methodology, in our article published in the May/June 2026 edition of Inside GNSS: The Empty Field That Wasn’t: GPS, OTAD and Two Decades of Encrypted Broadcasts. For security researchers, this dataset presents an extraordinary target. It is a globally deployed, operational cryptographic network sitting in plain sight, perfectly suited for traditional traffic analysis and structural cryptanalysis. We invite the infosec community to read the complete analysis, review our open-source Julia code, and join us in auditing these signals. Software-defined GNSS receivers readily allow access to the data, and the signal passes overhead twice a day, every day. Every GPS satellite is a numbers station. The receivers have always been listening; it is time the security community started looking at the bytes.
Acknowledgements
This article is based on a project developed by Ahmed Kamruddin during his MSc studies at University College London. Thanks also to Ramsey Faragher and Markus Kuhn for valuable comments on this work. The initial stages of the work were performed within the Trusted Innovative GNSS receivER (TIGER) project, co-funded by the European GNSS Agency (GSA) under grant agreement 228443.

---
*Synthesized by AutonomousLearner*
