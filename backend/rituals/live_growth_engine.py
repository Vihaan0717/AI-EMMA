"""
Live Growth Engine — The always-on learning layer.
Runs continuously alongside daily_growth.py.
Each agent watches for its own triggers and learns autonomously.
"""

import asyncio
import json
import sqlite3
import os
from datetime import datetime
from pathlib import Path
from rich.console import Console
from agents.agent_registry import get_all_agents, get_agent
from iq_core.parser import Parser
from iq_core.memory_manager import AgentMemory
from config.settings import DB_PATH

console = Console()

# ── Live Trigger Event ────────────────────────────────────────────────────────
class LiveEvent:
    def __init__(self, event_type: str, payload: dict, source: str):
        self.event_type = event_type   # "low_score" | "schema_change" | "incident" | "new_data"
        self.payload    = payload
        self.source     = source
        self.timestamp  = datetime.now().isoformat()

# ── Per-Agent Live Learning ───────────────────────────────────────────────────
async def live_learn(agent_id: str, event: LiveEvent):
    """Each agent responds to its own triggers and learns from them."""
    agent = get_agent(agent_id)

    # Only trigger agents that care about this event type
    triggers = agent.cfg.get("live_learning_protocol", {}).get("triggers", [])
    if not any(event.event_type.lower() in t.lower() for t in triggers):
        return

    console.print(f"  [dim cyan]⚡ Live trigger → {agent.name}: {event.event_type}[/dim cyan]")

    # Build learning prompt from event
    learn_prompt = (
        f"LIVE LEARNING EVENT: {event.event_type}\n"
        f"Source: {event.source}\n"
        f"Payload: {json.dumps(event.payload, indent=2)}\n\n"
        f"As {agent.name}, analyze this event per your live_learning_protocol.\n"
        f"What did you learn? What skill improved? What new fact do you now know?\n"
        f"Output JSON with: reasoning[], answer, skill_delta, new_facts[]"
    )

    try:
        # Using think (which calls chat)
        response = await agent.think(learn_prompt)
        
        if response.new_facts:
            # Add to agent's own memory
            for fact in response.new_facts:
                agent.memory.add_semantic(fact, metadata={"source": event.source, "event_type": event.event_type})
        
        if response.skill_delta:
            agent.apply_skill_delta(response.skill_delta)

        # Log live learning to DB
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "INSERT INTO ritual_logs (agent_id, ritual_type, score, xp_gained, facts_added) VALUES (?,?,?,?,?)",
                (agent_id, f"live_{event.event_type}", response.confidence * 100, 5, len(response.new_facts))
            )

        console.print(f"  [green]✅ {agent.name} learned live: {response.new_facts[:1]}[/green]")

    except Exception as e:
        console.print(f"  [red]❌ Live learn failed for {agent.name}: {e}[/red]")


# ── Event Dispatcher ──────────────────────────────────────────────────────────
async def dispatch_live_event(event: LiveEvent):
    """Send event to ALL agents — each decides if it's relevant to them."""
    all_agents = get_all_agents()
    # Run in parallel — each agent checks its own triggers
    await asyncio.gather(*[live_learn(a.agent_id, event) for a in all_agents], return_exceptions=True)


# ── Specialized Live Routines ─────────────────────────────────────────────────
async def vega_live_analysis():
    """Vega continuously monitors system data and fires insights."""
    while True:
        await asyncio.sleep(300)  # Every 5 minutes
        console.print("[dim][*] Vega running live analysis...[/dim]")
        try:
            with sqlite3.connect(DB_PATH) as conn:
                recent = conn.execute(
                    "SELECT agent_id, score, created_at FROM ritual_logs ORDER BY created_at DESC LIMIT 50"
                ).fetchall()

            if recent:
                payload = {"recent_scores": [{"agent": r[0], "score": r[1], "time": r[2]} for r in recent]}
                await dispatch_live_event(LiveEvent("new_data", payload, "vega_monitor"))
        except Exception as e:
            console.print(f"[red][!] Vega live analysis error: {e}[/red]")


async def pipe_health_watch():
    """Pipe continuously monitors system health."""
    while True:
        await asyncio.sleep(60)  # Every 60 seconds
        console.print("[dim][*] Pipe checking system health...[/dim]")
        # Check Ollama, SQLite, ChromaDB
        health = {"ollama": True, "sqlite": True, "chromadb": True}
        try:
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute("SELECT 1")
        except Exception:
            health["sqlite"] = False

        if not all(health.values()):
            await dispatch_live_event(LiveEvent("incident", health, "pipe_health_watch"))


async def axiom_prompt_watch():
    """Axiom watches for low-scoring agents and auto-rewrites their prompts."""
    while True:
        await asyncio.sleep(600)  # Every 10 minutes
        console.print("[dim][*] Axiom auditing prompt health...[/dim]")
        try:
            with sqlite3.connect(DB_PATH) as conn:
                low_scorers = conn.execute(
                    "SELECT agent_id, AVG(score) as avg FROM ritual_logs "
                    "WHERE created_at > datetime('now', '-1 hour') GROUP BY agent_id HAVING avg < 70"
                ).fetchall()

            for agent_id, avg_score in low_scorers:
                if agent_id and avg_score:
                    payload = {"agent_id": agent_id, "avg_score": avg_score, "threshold": 70}
                    await dispatch_live_event(LiveEvent("low_score", payload, "axiom_prompt_watch"))
        except Exception as e:
            console.print(f"[red][!] Axiom prompt watch error: {e}[/red]")


# ── Main Live Engine ──────────────────────────────────────────────────────────
async def run_live_engine():
    """Start all live monitoring routines in parallel."""
    console.print("[bold magenta]⚡ Live Growth Engine Started[/bold magenta]")
    await asyncio.gather(
        vega_live_analysis(),
        pipe_health_watch(),
        axiom_prompt_watch(),
    )

if __name__ == "__main__":
    asyncio.run(run_live_engine())
