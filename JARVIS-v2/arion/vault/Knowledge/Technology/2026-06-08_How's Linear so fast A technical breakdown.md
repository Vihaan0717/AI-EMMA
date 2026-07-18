---
title: "How's Linear so fast? A technical breakdown"
source: https://performance.dev/how-is-linear-so-fast-a-technical-breakdown
date: 2026-06-08
tags:
  - news
  - auto-learning
  - auto-injected
---

# How's Linear so fast? A technical breakdown

How's Linear so fast? A technical breakdown
A few milliseconds is all it takes to update an issue in Linear. A traditional CRUD app doing the same thing takes about 300ms. How do they do it? There's no secret silver bullet to performance. The reality is that it's built from the ground up on the right foundation, then improved by countless decisions. My goal is to walk through some of the techniques that make Linear feel the way it does and help you implement the same.
What I'll cover
Database in the browser
Making the first load feel instant
The sync engine
Designed for speed
Animations
A quick disclaimer: I've never worked at Linear and have never seen their code. Everything I share comes from my personal experience, studying their app, reading their blog posts, or watching their conference talks. I simply love building web apps and have been using Linear since their beta launch. Also, the article’s hero image comes from a video by Meg Wayne, whose work for Linear is phenomenal.
Database in the browser
Most web apps live inside the same loop. The user clicks. The browser fires an HTTP request. A server queries a database and sends it back. The browser repaints. The end result is a spinner, a skeleton, or a frozen UI for a few hundred milliseconds while the app waits on the network.
Linear inverts the traditional relationship. The actual database the UI reads from is in the browser, in IndexedDB. Mutations apply locally first, then asynchronously push to the server, which broadcasts deltas back to other clients via WebSocket.
In my opinion, this is the most critical piece to Linear's performance. When your goal is to build a fast web app the biggest bottleneck you will fight is the network. Any data sent between the client and server costs hundreds of milliseconds. The best approach is to eliminate the need for a network request entirely: which is exactly what Linear does.
I'll be repeating this a lot, but the secret to building incredible web apps is by hiding all the network requests from the user. The more loading states you can avoid the better.
Here's an example of how simple Linear's requests are:
// A traditional web app updating the server
async function updateIssue({ issue }) {
showSpinner();
const response = await fetch(`/api/issues/${issue.id}`, {
method: "PATCH",
body: JSON.stringify({ title: issue.title }),
});
const updated = await response.json();
setIssue(updated)
hideSpinner();
}
// vs Linear
issue.title = "Faster app launch";
issue.save();
The first line, issue.title = "Faster app launch"
, updates an in-memory datastore (MobX observable in Linear's case) . The second line, issue.save();
, queues a transaction that their sync engine batches and flushes to the server. The key here is that the UI re-renders synchronously off the local, in-memory, update. There are no spinners because there is nothing to wait for because the data is synced in the backround. This is the magic of treating the browser as the database for each user.
Tuomas, one of Linear's co-founders, said this at a conference in 2024: 'Literally the first lines of code that I wrote was the sync engine, which is very uncommon to what you usually do when you're a startup.' From day one, Linear knew the approach they wanted to take and the tradeoffs it would take.
I know most people won't build a custom sync engine like Linear just to make their app feel fast and they don't need to. For most use cases, libraries like Tanstack Query and SWR can get surprisingly close with optimistic updates. Most web apps feel slow because the UI waits for each network request to complete before updating state. For most usecases the network request will succeed so you should take advantage of that and optimistically update your state.
// optimistic mutation with SWR
mutate(
`/api/issues/${issue.id}`,
{ ...issue, title: "Faster app launch" },
false
);
// vs Linear
issue.title = "Faster app launch";
issue.save();
The key idea is simple: UI responsiveness should not depend on network latency. Users perceive speed based on how quickly the interface reacts, not how quickly the server responds.
Optmistic requests is one of the highest leverage improvements you can make:
eliminate unnecessary spinners
update state immediately
validate in the background
rollback only if needed
Linear's foundation is based on this exact principal and it makes the app feel native and fast.
A peek into Linear's stack
Linear is built on the simplest stacks you can find: React, TypeScript, MobX, Postgres, a CDN. There's no edge database, no React Server Components, or no fancy framework.
Frontend
React + react-dom (UI runtime)
MobX (observable graph, granular re-renders)
TypeScript (single language end-to-end)
Rolldown-Vite + plugin-react-oxc(mid-2025; previously Rollup; previously Parcel)
ProseMirror + y-prosemirror (rich text editor; Yjs CRDT for live collab)
Radix UI primitives (popovers, menus, focus traps)
Emotion + StyleX (Emotion runtime + StyleX compiled to atomic CSS)


---
*Synthesized by AutonomousLearner*
