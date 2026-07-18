---
title: "Show HN: adamsreview – better multi-agent PR reviews for Claude Code"
source: https://github.com/adamjgmiller/adamsreview
date: 2026-05-11
tags:
  - news
  - auto-learning
  - auto-injected
---

# Show HN: adamsreview – better multi-agent PR reviews for Claude Code

Multi-stage code review for Claude Code — parallel sub-agent detection, validation passes, persistent JSON state, and an automated fix loop that re-reviews and reverts regressions before committing.
On my own PRs, it's been catching dramatically more real bugs than Claude Code's built-in /review
, /ultrareview
, CodeRabbit, Greptile, and Codex's built-in review — while producing fewer false positives. (Anecdotal, n=me.) Modeled after the built-in /review
and extended into a six-command pipeline. Runs against your regular Claude Code subscription (Max plan recommended) — unlike /ultrareview
, which charges against your Extra Usage pool.
/plugin marketplace add adamjgmiller/adamsreview
/plugin install adamsreview@adamsreview
The six commands:
/adamsreview:review
— multi-lens code review of a branch or PR. Up to seven parallel sub-agent lenses (correctness, security, UX, etc.) feed a dedup pass, a cheap-then-deep validation gate, and (optionally) a holistic Opus cross-cutting pass. High-confidence auto-fix proposals are pre-computed so:fix
and:walkthrough
can batch-accept them in one confirm.--ensemble
adds a Codex CLI pass and PR bot-comment scrape on top of the internal Claude lenses./adamsreview:codex-review
— Codex CLI peer to:review
. Same artifact shape, drop-in for everything downstream (:fix
,:add
,:walkthrough
,:promote
). Effort tunable via--effort low|medium|high|xhigh
(defaulthigh
)./adamsreview:add
— inject externally-sourced findings (a Claude Code cloud/ultrareview
paste, an Opus once-over, a teammate's note) into the most recent review's artifact. Deduped against what's already there, validated by the same gates, re-published to the existing PR comment./adamsreview:walkthrough
— interactive driver for findings:fix
would skip. Uses the harness'sAskUserQuestion
UI to walk through uncertain or human-judgment items one by one — promote what you want auto-fixed, skip the rest. Pre-computed auto-fix proposals are batch-accepted up front; the remainder get per-finding briefing + options + recommendation. Posts a decisions log to the PR./adamsreview:fix
— automated fix loop. Dispatches per-fix-group sub-agents in parallel, then re-reviews the work with Opus, reverts any regressions, and commits the survivors (one combined commit by default;--granular-commits
for one per group)./adamsreview:promote
— human override that promotes a single finding to auto-fixable, bypassing the lane filter and score threshold.
Command files live at bare-stem paths under commands/
; shared phase fragments and prompt references live under fragments/
; helper scripts and the artifact schema live under bin/
. The plugin runtime auto-adds bin/
to $PATH
on load — no symlinks, no install script.
On a non-trivial PR, the commands work best in this order:
- Review.
/adamsreview:review
— or/adamsreview:review --ensemble
if you have the Codex CLI installed and want to pool a Codex pass plus a PR bot-comment scrape on top of the internal Claude lenses (higher token cost). Or/adamsreview:codex-review [--effort <level>]
for a Codex-driven peer review (drop-in for everything downstream; effort tunable; no--ensemble
). - Add. (optional)
/adamsreview:add <paste...>
— if you ran a parallel review (cloud/ultrareview
, Opus once-over, manual scan, etc.) that surfaced bugs the original review missed, paste the result here. The findings are validated by Phase 4 and land in the same artifact, deduped against what's already there. Auto-eligible additions feed step 4; non-eligible ones surface in step 3. - Walkthrough. (optional)
/adamsreview:walkthrough [threshold]
— step through findings the fix command would skip (deep-manual, deep-report, and the entire light lane including lightconfirmed_mechanical
), restricted to those scoring at or above$threshold
(default 60) so low-signal items don't pad the session. Step 4.5 batch-accepts all findings carrying a pre-computed auto-fix proposal in one confirm (the fast path); the rest get per-finding briefing + options + recommendation via the harness'sAskUserQuestion
UI. Promote the ones you want auto-fixed with tailored fix-hints, skip the rest. Posts a decisions log to the PR for audit. Pass a lower threshold (e.g./adamsreview:walkthrough 30
) and pick the Full tier at the preflight prompt to audit Phase-3-demotedbelow_gate
findings too. - Fix.
/adamsreview:fix
— applies every auto-eligible finding (including whatever was added in step 2 and promoted in step 3). Phase 7.5 surfaces any remaining auto-fix proposals (light-lane / manual / report findings) for one-confirm batch-accept before Phase 8 dispatch. Default: one combined commit for all surviving fixes; pass--granular-commits
for one commit per fix group. Per-group Phase-9 outcome lands in the commit message either way.
Each command is independent — you can go straight from review to fix if you only care about auto-eligible findings, or skip review entirely and run :fix
against an existing artifact. Steps 2–4 can land days or weeks after step 1; 

---
*Synthesized by AutonomousLearner*
