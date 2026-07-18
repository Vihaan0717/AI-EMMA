---
title: "My automated doubt development process"
source: https://www.alexself.dev/blog/automated-doubt
date: 2026-06-08
tags:
  - news
  - auto-learning
  - auto-injected
---

# My automated doubt development process

This process originated out of a lack of trust. I lost trust early in my AI-assisted development due to allowing our LLM partners to do too much, too quickly and without the standard engineering practices I had come to internalize. Trust was regained by automating as much doubt as I could muster. What does performing doubt look like? Critiquing the implementation of an artifact and doing so, repeatedly. If you are using AI to write code, specs, docs or any artifact, you may find this piece useful.
I use subagents, quite a bit. They inhabit the fulcrum of the entire process. They are specialized in ways that audit perspectival surfaces a standard instantiation of Claude wouldn't necessarily cover. The core idea in all of this is automated doubt from multiple perspectives and the front-loading of scrutiny. The more parallax coverage in AI development, the better; where different vantage points catch different defects, the way two eyes give you depth. The development process goes something like this:
Phase 1 — Design
It starts with an idea or a feature I'd like to build and a specification. Like any good development practice, it's usually wise to start with a spec, PRD, plan, or whatever flavor of design preferred. I ask Claude to write the spec and I spend 2–5 minutes skimming the file to verify the core implementation aspects of the idea are captured. This is where the iteration process begins.
I start with a Pre-implementation workflow (slash command in Claude Code), which consists of three agents performing the first round of doubt: Pre-Implementation Architect, Documentation Validator and Assumption Excavator. These agents do several things: verify design quality, scope assessment, completeness, documentation gaps and all the hidden assumptions that exist in the spec. All relevant findings discovered are folded into the spec by the main terminal agent — usually 10–25 depending on the scope of the idea.
Example findings:
Assumption Excavator: "executionStatsSchema in registry-sdk returns {totalCount, recentCount, windowMinutes}. Spec assumes {avgScore, medianDurationMs, passRate, lastRunDate, lastRunScore}. Entire history section unbuildable without new API endpoint"
Pre-Implementation Architect: "HarnessProfile embeds mcp.read/merge/remove/write methods alongside path config. Consider extracting McpConfigStrategy to separate concerns. Each harness file will grow to 80–120 lines otherwise."
The scope determines the amount of iterations I make. If the scope calls for it, the iteration continues with the next set of agents: Gap Analyzer, Implied Completeness Detector, Ambiguity Mapper. These agents in particular are excellent at finding all the omitted aspects of the system that will be missed if left unaddressed. When the gaps are discovered, they are added to the spec.
Example findings:
Gap Analyst: "McpConfigStrategy defines read/merge/write but does not specify behavior for malformed input, permission denied, partial write failure, or file locking. Destructive operation on user config files across 4 harnesses in 3 formats."
Implied Completeness Detector: "Manifest records version at root but installation state per-harness. When v0.3.0 user (Claude Code) runs v0.4.0 with --harness opencode, behavior undefined. Per-harness versioning or upgrade reconciliation not addressed."
For practical use:
- Small scope: Pre-implementation only
- Medium scope: Pre-implementation with Gap, Implied, Ambiguity
- Large scope: Full sweep with multiple runs with each, occasionally dipping into other specialized agents
Now I pause and spend some time to read the spec, ~15–60 min. If everything checks out and the spec is ready for development, I ask Claude to generate a companion checklist that we can update and follow along. The checklist is created as a separate file and helps if you need to step away and close out a session mid-dev.
Phase 2 — Development
Claude pulls up the spec and checklist and begins development. If I'm picking the spec up with the development partly complete in a new session, I usually ask Claude to explore, or send a Chain Tracer or Deep Explore subagent for the complete picture prior to restarting.
One aspect of my development process that might stand out and that I would like to highlight: I don't use subagents for writes. This comes back to the trust angle. My experiences of spawning subagents for writes gone awry, often causing more harm than good, led to a temporary line drawn in the sand. I also say temporary, because this will undoubtedly change. As I understand it, there are methods for proper swarm orchestration, worktrees, agent-to-spec driven dev, but that's a bit beyond my trust level now. Sometimes the Claude terminal agent will spawn them for bulk updates, but I prefer a single Claude Code terminal instance building out the project.
I tackle all phases of the specification until complete. Verify the build works, and then comes the post-implementation development process. I mentioned autom

---
*Synthesized by AutonomousLearner*
