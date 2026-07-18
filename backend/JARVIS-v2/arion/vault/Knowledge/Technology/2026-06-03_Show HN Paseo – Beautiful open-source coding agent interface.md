---
title: "Show HN: Paseo – Beautiful open-source coding agent interface"
source: https://github.com/getpaseo/paseo
date: 2026-06-03
tags:
  - news
  - auto-learning
  - auto-injected
---

# Show HN: Paseo – Beautiful open-source coding agent interface

One interface for Claude Code, Codex, Copilot, OpenCode, and Pi agents.
Run agents in parallel on your own machines. Ship from your phone or your desk.
- Self-hosted: Agents run on your machine with your full dev environment. Use your tools, your configs, and your skills.
- Multi-provider: Claude Code, Codex, Copilot, OpenCode, and Pi through the same interface. Pick the right model for each job.
- Voice control: Dictate tasks or talk through problems in voice mode. Hands-free when you need it.
- Cross-device: iOS, Android, desktop, web, and CLI. Start work at your desk, check in from your phone, script it from the terminal.
- Privacy-first: Paseo doesn't have any telemetry, tracking, or forced log-ins.
Paseo runs a local server called the daemon that manages your coding agents. Clients like the desktop app, mobile app, web app, and CLI connect to it.
You need at least one agent CLI installed and configured with your credentials:
Download it from paseo.sh/download or the GitHub releases page. Open the app and the daemon starts automatically. Nothing else to install.
To connect from your phone, scan the QR code shown in Settings.
Install the CLI and start Paseo:
npm install -g @getpaseo/cli
paseo
This shows a QR code in the terminal. Connect from any client. This path is useful for servers and remote machines.
For full setup and configuration, see:
Everything you can do in the app, you can do from the terminal.
paseo run --provider claude/opus-4.6 "implement user authentication"
paseo run --provider codex/gpt-5.4 --worktree feature-x "implement feature X"
paseo ls # list running agents
paseo attach abc123 # stream live output
paseo send abc123 "also add tests" # follow-up task
# run on a remote daemon
paseo --host workstation.local:6767 run "run the full test suite"
See the full CLI reference for more.
Skills teach your agent to use Paseo to orchestrate other agents.
npx skills add getpaseo/paseo
Then use them in any agent conversation:
/paseo-handoff
— hand off work between agents. I use this to plan with Claude and then handoff to Codex to implement./paseo-loop
— loop an agent against clear acceptance criteria (aka Ralph loops), optionally with a verifier./paseo-advisor
— spin up a single agent as an advisor for a second opinion, without delegating the work itself./paseo-committee
— form a committee of two contrasting agents to step back, do root cause analysis, and produce a plan.
Quick monorepo package map:
packages/server
: Paseo daemon (agent process orchestration, WebSocket API, MCP server)packages/app
: Expo client (iOS, Android, web)packages/cli
:paseo
CLI for daemon and agent workflowspackages/desktop
: Electron desktop apppackages/relay
: Relay package for remote connectivitypackages/website
: Marketing site and documentation (paseo.sh
)
Common commands:
# run all local dev services
npm run dev
# run individual surfaces
npm run dev:server
npm run dev:app
npm run dev:desktop
npm run dev:website
# build the server stack
npm run build:server
# repo-wide checks
npm run typecheck
- paseo-relay — self-hosted relay in Go
Self-hosted relays use ws://
unless TLS is opted in. For a relay behind nginx on 443, start the daemon with:
PASEO_RELAY_ENDPOINT=127.0.0.1:8080 \
PASEO_RELAY_PUBLIC_ENDPOINT=relay.example.com:443 \
PASEO_RELAY_USE_TLS=true \
paseo daemon start
Equivalent config:
{
"daemon": {
"relay": {
"enabled": true,
"endpoint": "127.0.0.1:8080",
"publicEndpoint": "relay.example.com:443",
"useTls": true
}
}
}
Minimal nginx WebSocket proxy:
server {
listen 443 ssl;
server_name relay.example.com;
ssl_certificate /etc/letsencrypt/live/relay.example.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/relay.example.com/privkey.pem;
location /ws {
proxy_pass http://127.0.0.1:8080;
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
proxy_set_header Host $host;
}
}
AGPL-3.0

---
*Synthesized by AutonomousLearner*
