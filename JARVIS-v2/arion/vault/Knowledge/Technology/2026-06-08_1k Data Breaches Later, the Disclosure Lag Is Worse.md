---
title: "1k Data Breaches Later, the Disclosure Lag Is Worse"
source: https://www.troyhunt.com/1000-data-breaches-later-the-disclosure-lag-is-worse-than-ever/
date: 2026-06-08
tags:
  - news
  - auto-learning
  - auto-injected
---

# 1k Data Breaches Later, the Disclosure Lag Is Worse

Today, I loaded the 1,000th data breach into Have I Been Pwned. Reflecting on that milestone number, I pondered how to mark the occasion in writing, and what immediately came to mind was a very simple question: why is it still needed? Especially considering the emergence of privacy regulations such as GDPR and CCPA in the 12 and a half years since I started HIBP, what possible purpose does it still serve? The title kinda gives the answer away, and the big number we hit today coincided with another pattern that makes everything worse: increasingly long lag times for disclosure.
This is all going to be anecdotal, and as far as I know, there are no hard numbers for me to cite, but the evidence is everywhere. Here's what I mean:
New breach: Cruise operator Carnival was targeted in a ShinyHunters “pay or leak” attack last week. 8.7M records with 7.5M email addresses and loyalty program data were published yesterday. 85% were already in @haveibeenpwned. Read more: https://t.co/QhqNt0WucV
— Have I Been Pwned (@haveibeenpwned) April 24, 2026
That was the 24th of April, five days after news of the incident had broken. Given ShinyHunters' MO, Carnival would have known about the breach many days before they ratcheted up extortion pressure by announcing the impending leak on their website. The subsequent leak on the 24th was very public: an announcement was posted to the group's dark-web site, the data itself was published to their clear-web site, and industry commentary followed:
🚨 Massive Data Breach
— Intel and Breaches (@IBreaches) April 24, 2026
Carnival Corporation (https://t.co/pGlchZ1yFy) reportedly impacted — 8.7M+ customer records exposed
📊 Alleged data includes:
• Full names & email addresses
• Dates of birth & gender
• Location data & loyalty program details
🎯 Linked to ShinyHunters… pic.twitter.com/Fd8tNFPqpd
Per that last post, the data was then reposted to all sorts of other places: hacking forums, Telegram channels, and who knows how many other, more private locations. The point is that it spread quickly, extensively, and, without any shadow of a doubt, Carnival were aware of this. They then told people about it on the 27th... of May. According to their press release that same day, this was 43 days after learning about the incident. For more than 6 weeks, data breach victims whose names, dates of birth, email addresses, loyalty program details and, of course, their association with Carnival leaked to the public en masse had absolutely no idea of their exposure. And if they asked Carnival about it? Well:
As recently as four days ago, we heard “I’m in the breach per HIBP, but Carnival is telling me there’s no breach!” pic.twitter.com/YYmGm3NzEY
— Troy Hunt (@troyhunt) May 28, 2026
So, why the delay? Last week's press coverage may give some insight:
thorough and time-consuming analysis of the impacted data
Often, the reason I hear for disclosure lag is "we needed to fully assess the scope of exposed data before notifying people". The issue I have with this position is that it implies that even an early heads-up can't happen until there's a very comprehensive understanding of the impact. There are many things that take time to establish after a data breach: the jurisdiction each individual sits in, the precise data that was exposed about them and additional information that may be buried in terabytes of exfiltrated data in all sorts of different formats. But pulling out email addresses and sending early notification is very easy - I've literally done it a thousand times now.
This isn't just a Carnival issue; in fact, it was off the back of this next one only a few days later that I was prompted to write this post:
FFS. 45 days. Even worse than Carnival. And like Carnival, very broadly distributed and easily accessible by the masses, including HIBP:
New breach: Zara was named as a ShinyHunters victim last month, after which data containing 197k unique email addresses was published. Impacted data included customer support records, product SKUs and order IDs. 60% were already in @haveibeenpwned. More: https://t.co/0hIQbqoBCk
— Have I Been Pwned (@haveibeenpwned) May 8, 2026
I have a working theory that the disclosure lag is worsening in part due to the proliferation of class actions immediately following a breach. In my live stream last weekend, I did a quick search for the DentaQuest breach:
Three of the first four results are all for class actions related to the breach, and there are two more class action results a little further down the page. I've been raising concerns about the adverse impact of class actions for many years now, and it's worse than I've ever seen. By a big margin, too.
It's not just me observing how the behaviour of these orgs appears to be influenced by how lawyers will respond, either. Have a read of this post from Roby Joyce (check out his bio if you don't already know why he's worth paying attention to) after he learned about his exposure in the ZenBusiness breach via HIBP:
What espec

---
*Synthesized by AutonomousLearner*
