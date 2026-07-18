---
title: "Rift: Better Alternative to Git Worktrees"
source: https://github.com/anomalyco/rift
date: 2026-06-01
tags:
  - news
  - auto-learning
  - auto-injected
---

# Rift: Better Alternative to Git Worktrees

rift: better alternative to git worktrees
- copy on write (saves space)
- instant (< 0.1s on 10gb folder)
- fast cli
- use as FFI lib with bun or node
mac and linux+btrfs for now more support soon
npm install -g rift-snapshot
# or
bun add -g rift-snapshot
Release archives are available from GitHub Releases.
| Platform | Backend | Behavior |
|---|---|---|
| Linux x64 | Writable btrfs snapshots | rift init converts an ordinary directory into a btrfs subvolume. |
| macOS arm64 / x64 | APFS clonefile |
rift init registers the source directory. |
| Windows x64 | None | The package is published; workspace creation is not implemented. |
cd ~/code/app
rift init
rift init
selects an existing Rift root above the current directory, or the nearest Git root when no Rift root exists. Use --here
to initialize exactly the selected directory.
On Linux, first initialization of an ordinary btrfs directory performs a reflink import into a new btrfs subvolume and swaps it into the same path. If the selected root is registered already, no conversion occurs. If its .rift
marker is missing, rift init
restores it and completes any required conversion.
rift create
rift create --name parser-fix
rift create --into /fast/rifts
rift create
searches upward for .rift
, copies that managed workspace, records the immediate parent, and prints the new workspace path to stdout.
On Linux, it creates a writable btrfs snapshot. On macOS, it uses APFS clonefile
.
When the workspace is a Git repository, the new workspace has detached HEAD
and retains index and working-tree state.
rift list
rift ancestors
list
prints direct active child workspaces. ancestors
prints parent workspaces, nearest first.
rift remove # trash the current created rift subtree
rift remove -f ~/code/app # unregister a source root
rift remove --children ~/code/app # trash descendants, preserve the selected workspace
rift gc # physically delete trash and prune missing entries
Removing a created rift moves its active subtree into adjacent .trash
storage. rift gc
deletes that storage later.
Removing a source root requires -f
in the CLI. The source directory remains on disk. Its .rift
marker is removed. Existing registered descendants are moved into trash. Missing descendants are removed from the registry.
eval "$(rift shell-init zsh)" # or bash
The shell wrapper changes directory after init
conversion, create
, or removal of the current created rift.
Each managed workspace has a .rift
marker containing its identifier. An SQLite registry stores paths, parent identifiers, and trash entries.
Default created-workspace storage is adjacent to the registered source root:
~/code/app/ source workspace
~/code/.rifts/app/parser-fix/ created workspace
~/code/.rifts/app/.trash/ removed workspace storage
The package selects a Bun or Node FFI binding through conditional exports.
import { create, list, remove, gc } from "rift-snapshot";
const workspace = create({ from: process.cwd(), name: "schema-work" });
console.log(list({ of: process.cwd() }));
remove({ at: workspace });
gc();
The Node binding requires the experimental FFI API in Node.js 26.1 or later:
node --experimental-ffi app.mjs
With Node's permission model, also pass --allow-ffi
.
init(options?: { at?: string; database?: string }): null
create(options?: { from?: string; name?: string; into?: string; database?: string }): string
remove(options?: { at?: string; all?: false; database?: string }): void
remove(options: { at?: string; all: true; database?: string }): string[]
list(options?: { of?: string; database?: string }): string[]
ancestors(options?: { of?: string; database?: string }): string[]
gc(options?: { database?: string }): string[]
The JavaScript init
function initializes exactly at
; Git-root selection and --here
are CLI behavior.
Operation failures throw RiftError
with a code
and, when relevant, path
.
cargo test --workspace --locked
./scripts/install.sh
scripts/install.sh
installs an optimized CLI binary to ${CARGO_HOME:-$HOME/.cargo}/bin/rift
.
MIT

---
*Synthesized by AutonomousLearner*
