---
title: "I'm going back to writing code by hand"
source: https://blog.k10s.dev/im-going-back-to-writing-code-by-hand/
date: 2026-05-11
tags:
  - news
  - auto-learning
  - auto-injected
---

# I'm going back to writing code by hand

Im going back to writing code by hand
This dev-log is getting a lot of attention on HN (scary!): HN Thread.
To those who are coming here from HN: This started as an investigation or rather a question: "How far I can get with building a piece of software by keeping myself completely out of the loop". The tl;dr of this dev log is that I still need to be in the loop to make anything meaningful. Take aways:
- like "em-dash" is to ai writing, "god-object" is to ai coding
- vibe-coding makes everything feel cheap and you may end up losing focus and building bloat
- let a human (you) write the architecture and don't just keep asking it for features
- And some AGENTS.md/CLAUDE.md directives that I felt help me stay out of the loop a little more
Humans intervention is still needed as of 10/05/2026. You can totally go back now!
I
Here is k10s: https://github.com/shvbsle/k10s/tree/archive/go-v0.4.0
234 commits. ~30 weekends. Built entirely on vibe-coded sessions with Claude, whenever my tokens lasted long enough to ship something.
I'm archiving my TUI tool and rewriting it from scratch.
k10s started as a GPU-aware Kubernetes dashboard (and my first foray into building something serious with AI). Think k9s but built for the people running NVIDIA clusters, people who actually care about GPU utilization, DCGM metrics, and which nodes are sitting idle burning $32/hr. I built it in Go with Bubble Tea [1] and it worked.
For a while... :(
I learned over these 7 months is worth more than the 1690 lines of model.go
I'm throwing away. And I think anyone doing serious vibe-coding can benefit from this, because this part doesn't surface much (I feel it gets buried under the demo reels and the velocity wins).
tl;dr: AI writes features, not architecture. The longer you let it drive without constraints, the worse the wreckage gets. The velocity makes you think you're winning right up until the moment everything collapses simultaneously.
II
vibe coding high
I started k10s in late September 2025. The first few weeks were magic. I'd prompt Claude with "add a pods view with live updates" and boom, it worked. Resource list views, namespace filtering, log streaming, describe panels, keyboard navigation. Each feature landed clean because the project was small enough that the AI could hold the whole thing in context.
The basic k9s clone took maybe 3 weekends. Resource views for pods, nodes, deployments, services. A command palette. Watch-based live updates. Vim keybindings. All working, all vibe-coded in single sessions. I was building at maybe 10x my normal speed and it felt incredible.
Then I wanted the main selling point.
The whole reason k10s exists is the GPU fleet view. A dedicated screen that shows you every node's GPU allocation, utilization from DCGM, temperature, power draw, memory. Not buried in kubectl describe node
output, but right there in a purpose-built table with color-coded status. Idle nodes in yellow. Busy in green. Saturated in red.
And Claude one-shot it. I prompted for the fleet view, it generated the FleetView
struct, the tab filtering (GPU/CPU/All), the custom rendering with allocation bars. It looked beautiful. I was riding the high.
Then I typed :rs pods
to switch back to the pods view.
Nothing rendered. The table was empty. Live updates had stopped. I switched to nodes, it showed stale data from the fleet view's filter. I went back to fleet, the tab counts were wrong.
The god object had consumed itself.
This is the title of the blog post. This is where I intervened for the first time. For 7 months I'd been prompting and shipping without ever sitting down and actually reading the code Claude wrote. I'd look at the diff, verify it compiled, test the happy path, move on. But now something was fundamentally broken and I couldn't just prompt my way out of it.
So I sat down and read model.go
. All 1690 lines. I was horrified.
Here's what it looked like. One struct to rule them all:
type Model struct {
// 3rd party UI components
table table.Model
paginator paginator.Model
commandInput textinput.Model
help help.Model
// cluster info and state
k8sClient *k8s.Client
currentGVR schema.GroupVersionResource
resourceWatcher watch.Interface
resources []k8s.OrderedResourceFields
listOptions metav1.ListOptions
clusterInfo *k8s.ClusterInfo
logLines []k8s.LogLine
describeContent string
currentNamespace string
navigationHistory *NavigationHistory
logView *LogViewState
describeView *DescribeViewState
viewMode ViewMode
viewWidth int
viewHeight int
err error
pluginRegistry *plugins.Registry
helpModal *HelpModal
describeViewport *DescribeViewport
logViewport *LogViewport
logStreamCancel func()
logLinesChan <-chan k8s.LogLine
horizontalOffset int
mouse *MouseHandler
fleetView *FleetView
creationTimes []time.Time
allResources []k8s.OrderedResourceFields // fleet's unfiltered set
allCreationTimes []time.Time // fleet's timestamps
rawObjects []unstructured.Unstructured
ageColumnIndex int
// ...
}
UI widgets. K8s client. Per-view state for 

---
*Synthesized by AutonomousLearner*
