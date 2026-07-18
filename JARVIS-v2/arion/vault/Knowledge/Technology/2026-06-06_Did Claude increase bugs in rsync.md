---
title: "Did Claude increase bugs in rsync?"
source: https://alexispurslane.github.io/rsync-analysis/
date: 2026-06-06
tags:
  - news
  - auto-learning
  - auto-injected
---

# Did Claude increase bugs in rsync?

In order to avoid accuastions of this "just being Claude defending Claude," "AI slop," "probably all hallucinations," etc., I've decided it's probably worth explaining a few key points about how this report was created:
In late May 2026, rsync blew up. First, an evidence-free Mastodon post was made pointing to a spurious correlation between a regression that particular user experienced upon upgrading to a release, and that release having Claude commits in it. It was viewed an unknown number of times, but even likes and boosts passed the thousands mark handily, and it gained significant traction — as all spurious anti-AI hate does —, seeing 58 replies from 32 unique users. Someone rages about "cognitive surrender" with no evidence; another suggests adding rsync to the famous open-slopware blacklist. From there, it spread to Hacker News, with 81 comments, full of mixed dread, anger, and crowing about how this finally proves once and for all no one can use LLMs safely. Among all that was one particular comment which spurred further the view that the regressions and bugs were caused by Claude.
This On May 30, 2026, this burgeoning outrage emergently coalesced into a single focal point: a GitHub issue titled "Please Do Not Vibe Fuck Up This Software", opened against the rsync repository. It attached a screenshot of the Mastodon post criticizing the project's use of Claude. That's it. No bug report, no technical content, no attempt to actually ascertain if the concern was real or justified; just 350+ comments ranging from thoughtful concern to outright harassment (most of the most egregious, unreasonable, and outright violent comments have since been deleted; few thought to preserve them).
The thread did not stop at words. It eventually escalated to, at one point, visual depictions of fantasies of violence, when one user posted a now deleted comment including My Little Pony drawings of themselves strangling the "project janitor that pushed vibecoded commits":
Completing the internet outrage cycle, this issue in turn spread to Hacker News, generating hundreds more comments. Some attempted to point at the number of regressions after the introduction of Claude — "The Linux Mint Timeshift tool has an issue open documenting a number of regressions that are currently open on the rsync issues page, that were only introduced post-vibecoding" — as evidence that it was worse. Others pointed out that those regressions were not caused by Claude, and in response, the goalposts were moved again. Over and over, the core theme was one central claim, repeated everywhere: Claude-assisted development introduced bugs into a previously stable tool. AI is cognitive surrender, is cocaine, is loss of craft, and the users are right to be angry as a result:
People are very justifiably angry that a very stable, well trusted tool, has started to immediately go downhill… all because the main dev is vibecoding that software.
— fao_ on Hacker News
However, this isn't doesn't have to be a question solved only on the basis of — ironically — vibes. This is something that could be, at least to a degree, empirically tested. Some even pointed that out:
On Lobste.rs, in response to the Medium
essay Tridge himself posted in response, finally some users like boramalper
begin to
actually ask for evidence one way or another:
It'd be interesting if someone actually did a timechart of regressions after each release (if at all possible) to see if the number actually went up recently or not.
— boramalper on Lobsters
User bitshift
replied: "I would also love to see such a chart. It wouldn't be completely
informative… But at least it would be something objective we could measure."
This analysis is that chart. Or, well, as best as it can be made, given the limitations of the data (see the previous section).
The analysis uses a single metric: severity-weighted bugs per 10 commits (sev/10c). Each bug is normalized to a 0–1 severity score (its LLM-assigned severity divided by 100), and those scores are summed per release instead of simply counting bugs. The raw bug count is also shown in the table for reference, but sev/10c drives all statistical tests.
Every commit on the default branch was ordered by committer date to produce a sequential timeline. Each git tag points to a specific commit in this timeline. A release's range is all commits between the previous tag and its own tag. Pre-release tags ("pre", "rc") are skipped as boundaries and absorbed into their final release. Every commit belongs to exactly one release.
Bug reports come from three sources:
GitHub issues and mailing-list bugs are attributed to the most recent release that shipped before the bug was reported. For Bugzilla, each entry has a "Version" field that explicitly states which release the bug was reported against, and bugs are attributed to that release.
To control for bug severity — so that, as someone on HN said, a typo in a button and a CVE aren't rated equally — every bug report was score

---
*Synthesized by AutonomousLearner*
