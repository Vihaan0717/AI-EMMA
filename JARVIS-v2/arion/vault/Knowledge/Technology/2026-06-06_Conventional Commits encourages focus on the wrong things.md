---
title: "Conventional Commits encourages focus on the wrong things"
source: https://sumnerevans.com/posts/software-engineering/stop-using-conventional-commits/
date: 2026-06-06
tags:
  - news
  - auto-learning
  - auto-injected
---

# Conventional Commits encourages focus on the wrong things

Posted
on
in
Software Engineering
• 1882 words
• 9 minute read
Tags:
Git, Commits, Scoped Commits, Conventional Commits
You’ve almost certainly encountered Conventional Commits before. It may have reared its ugly head in the changelog of an open source project you’ve used. It may have been the enforced commit format for an open source project you contributed to. A lot of people swear by it. I swear at it.
Even though it is used by a large number of popular open source projects, Conventional Commits is an actively bad standard which encourages focus on the wrong things and fails to deliver on its promises.
Conventional Commits promises to add semantic meaning to commit messages to aid developers and end-users in understanding the changes made in a commit. However, Conventional Commits fails to do this in spectacular fashion. To demonstrate this, let’s look at the anatomy of a conventional commit. According to the Conventional Commit website commit messages should be formatted as follows:
<type>[optional scope]: <description>
[optional body]
[optional footer(s)]
The commit’s subject line has a <type>
(something like fix
, feat
, chore
,
docs
, or refactor
1) describing the type of change. Following that, there
is an optional scope, and then a description.
This format has a major failing: type is prioritised over scope. This is exactly backwards.
The scope of a change (the subject of the change) is the most important part of a commit. To demonstrate this, let’s consider why each one of the following stakeholders care about the scope of the change more than the type of the change:
Contributors: when you are a contributor to a project, you often need to read the commit log to identify changes in the codebase relevant to a certain area of the code. There are many reasons for this including:
- Wanting to catch up on what has happened since the last time you contributed.
- Trying to understand where the project’s overall inertia is.
- Looking for commits that might conflict with your in-progress work when pulling or rebasing.
As you read the commit log, you’re looking at what areas were touched. You really do not care about the type of change happening, you care about the scope of the change.
Debuggers: when investigating a bug, you often want to look through the commit log to see what changes might have touched areas related to the component where the bug manifested. Once again, the scope is the most important piece of information. The type of change is entirely useless because bugs can be introduced in any change regardless of type. (I’m sure we’ve all experienced writing a bugfix that caused another bug.)
Incident responders: when production is down, scanning the commit log for changes that were made around the time of the outage is an effective way to identify what areas may be causing the problem. Scope is once again the most important piece of information you can have at this point. For example, if you see a commit related to the
auth
scope at the tip of the spike of inbound API errors, it’s a likely culprit for the problem. And once again, type is irrelevant because bugs could have been added by any change.
So what does Conventional Commits do? It deprioritises scope so much that it’s optional! Why the hell is scope optional? Having a commit without a scope is like having a sentence without a subject! Then, to add insult to injury, Conventional Commits elevates type to the front of the commit message. Conventional Commits gets the priority of scope and type entirely wrong.
You might be thinking “so it may be backwards, but commit type is at least still important, right?” and to that I say “no”. A commit’s description should almost always tell you the type of the change! Consider this commit message as an example:
fix(compiler): prevent namespaced SVG <style> elements from being stripped
Even if you only had the description, it’s obvious that it was a bugfix! Space on the subject line of a commit is already at a premium, wasting characters on the type is not helpful! But it’s often even worse than useless; it’s often restrictive. Take this commit message as an example:
refactor(core): Update webmcp support to use document.modelContext
This commit updated the webmcp
functionality in the core
component to
support both document.modelContext
and navigator.modelContext
, so was that a
bugfix, refactor, or new feature? I would argue it’s all of them! But again, the
only thing that really matters is that it was a change to the core/webmcp
component.
Conventional Commits fundamentally focuses on the wrong thing (the commit type) and devalues the scope (which is what people actually care about).
So we have determined that the format of Conventional Commits sucks, but it must provide some benefit. Let’s read the Why Use Conventional Commits section to see if any of the reasons make any sense.
Automatically generating CHANGELOGs.
This is the biggest promise of Conventional Commits: you can run a tool like git-cliff or c

---
*Synthesized by AutonomousLearner*
