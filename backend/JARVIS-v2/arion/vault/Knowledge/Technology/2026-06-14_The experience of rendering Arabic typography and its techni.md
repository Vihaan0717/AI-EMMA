---
title: "The experience of rendering Arabic typography and its technical debt"
source: https://lr0.org/blog/p/arabic/
date: 2026-06-14
tags:
  - news
  - auto-learning
  - auto-injected
---

# The experience of rendering Arabic typography and its technical debt

An interactive introduction to the terrific experience of rendering Arabic typography and its technical debt
Once upon a time, a frontend ticket landed on my queue which was not properly mine, but the only other Arabic reader on the team was on leave. It went roughly as follows; a block of mixed-content Arabic prose on the customer-facing dashboard was rendering with a ragged left edge (the rag falls on the left in Arabic, since the lines set out from the right margin; the ticket said "ragged right") when the design team had explicitly specified justified text. Attached were three screenshots from three browsers and a polite note from the product manager observing that the Latin-script version of the same block looked, I quote, "fine."
The same six months I had closed three other tickets against the same product, each of which had presented to its filer as the only bug. A customer's name had appeared with its letters unjoined on a printed agreement, the way a sign-painter would have laid them out in 1962, because the PDF library on the receipt server pre-dated the existence of a shaping engine in its language runtime. A search index had been returning empty for accounts the customer service team could see in the database because a 2017 import had encoded twelve thousand names using fossil Unicode codepoints from 1991 instead of regular ones from 1995, and the index, very reasonably, treated the two encodings as different strings, So, that ragged-left ticket was the smallest of the four, HOWEVER, it sat on top of the same iceberg and pointed at the same thing.
Here is the disagreement, reproduced live. I used random text, the original had more spacing, I'm too lazy to pick words to maximize the ragging and spacing.
text-align: justify
(For these demonstrations this site ships its first webfont ever: Amiri, self-hosted, a hundred and fifty kilobytes of one man's unpaid evenings, redistributed under the OFL. That this is what it takes to show you something your operating system cannot do on its own is, I want to be clear, part of the argument. I think it is a delightful hundred and fifty kilobytes.)
It did look fine. I spent about half an hour with it, I walked the rendered DOM, I set text-align: justify
in so many different combinations of font-family and direction declarations, and at the end of the exercise I wrote a reply explaining, more or less honestly, that the problem was not a bug in our stylesheet but the state of Arabic typography on the web.
The reply took and the closure of the ticket took half an hour or so. The reasons behind it took five hundred years to pile up, and they involve a twice-mutilated vizier, a Qurʾān that vanished for four centuries, a Beirut newspaperman with a deadline, and an Egyptian physician who taught himself font engineering for fun (or that what I imagine about him). Walking through these, ended up to be the most enjoyable couple of weeks in that job, and I want to go through it here too.
What the scribes solved
The history deserves recording because most people outside the small world of Arabic font engineering don't know it, and it is wonderful. Classical Arabic typography, by which I mean the manuscript tradition that the early printers of Istanbul and Bulaq spent their careers chasing, justifies a line of text without stretching the spaces between words at all. Stretched spaces are the Latin convention, and in Arabic they produce an effect the scribes would have found simply ugly. Instead the scribe extends the letterforms themselves along the baseline, using what is called taṭwīl or, in the modern technical vocabulary, kashida: the connecting strokes between certain pairs of letters can be lengthened, sometimes lavishly, to carry a line out to the margin. A well-set page of Naskh from the seventeenth century has every line flush at both margins, and the result is the dense, regular weave that anyone who has spent time with a good manuscript Qurʾān will recognise on sight.
And this was not improvisation but a system, with a paper trail. The system was written down by Ibn Muqla, Abbasid vizier and chief calligrapher, who served three caliphs in succession and was imprisoned by two of them; the third had his right hand amputated on a charge of treasonous correspondence, and Ibn Muqla then kept writing for the next several months by lashing a reed pen to the stump of his wrist, and was rewarded for what he wrote by having his tongue cut out, and died in prison around the year 940. His body was buried three times in three different places, his daughter moving it after each interment to keep the grave out of police hands. The system he wrote down outlasted everybody who hurt him by a thousand years. It is called al-khaṭṭ al-mansūb, the proportional script; every letterform measured in rhombic dots of the reed nib, every curve a defined arc of a defined circle, the alif a fixed number of dots high and anything else derived from the alif. Within that system the elongation i

---
*Synthesized by AutonomousLearner*
