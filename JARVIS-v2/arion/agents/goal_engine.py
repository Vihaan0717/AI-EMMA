"""
arion/agents/goal_engine.py
==============================
ARION 3.0 — Goal Engine (A9 — fire-and-forget + nightly cron)

Maintains a rolling list of proactive, conversation-derived goals.
Goals are things only a real friend who pays attention would remember:
  "Ask Rohit about the deadline he mentioned on Tuesday"
  "Check if Arjun ate today — he skipped yesterday"
  "Follow up on Priya's exam results"

Nightly at 00:30: generates 3-5 new goals using Ollama from recent exchanges.
On each owner message: checks if any active goal is relevant → passes hint
  to Orchestrator's system prompt via get_active_goals().
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from core.base_agent import BaseAgent
from core.message_bus import Channel, Message

try:
    import aiohttp
except ImportError:
    aiohttp = None

logger = logging.getLogger(__name__)


# ── Goal data structure ────────────────────────────────────────────────────────

DEFAULT_GOAL = {
    "id":         "",
    "text":       "",
    "person":     "owner",
    "topic":      "general",
    "priority":   "medium",        # high | medium | low
    "status":     "active",        # active | in_progress | completed | expired
    "created_at": "",
    "expires_at": "",
    "source":     "nightly_gen",   # nightly_gen | manual | triggered
    "trigger_keywords": [],
    "last_prompted": "",
}


class GoalEngine(BaseAgent):
    """
    A9 — Proactive goal tracker.

    Actions handled:
      update_goals      (fire-and-forget) — update goal status from latest message
      get_active_goals  (request-response) — return active goals as prompt fragment

    Background loop runs nightly goal generation.
    """

    NIGHTLY_HOUR   = 0
    NIGHTLY_MINUTE = 30
    GOAL_TTL_DAYS  = 3       # Goals expire after 3 days if not triggered
    MAX_GOALS      = 10      # Keep goal list lean

    def __init__(self, config: Dict):
        super().__init__("GoalEngine", [Channel.GOAL])
        self.ollama_url = config.get("ollama_url", "http://localhost:11434")
        self.model      = config.get("model_name", "gemma3:1b")  # Fast small model
        self.goals_path = Path(
            config.get("goals_path", "arion/data/daily_goals.json")
        )
        self.goals_path.parent.mkdir(parents=True, exist_ok=True)
        self._goals: List[Dict] = self._load_goals()
        self._last_nightly: Optional[str] = None
        self._recent_context: List[str] = []  # Rolling last-20 messages for nightly gen

    # ── Agent lifecycle ───────────────────────────────────────────────────────

    async def run_loop(self):
        nightly_task = asyncio.create_task(self._nightly_loop())
        try:
            while self.running:
                msg = await self.get_next_message(timeout=1.0)
                if msg:
                    await self.handle_message(msg)
        finally:
            nightly_task.cancel()

    async def handle_message(self, message: Message):
        if message.action == "update_goals":
            await self._update_from_message(message.payload)

        elif message.action == "get_active_goals":
            fragment = self._build_goal_fragment(
                message.payload.get("contact", ""),
                message.payload.get("message", "")
            )
            if message.requires_response:
                await self.respond_to(message, "goals_result",
                                      {"goal_fragment": fragment})

    # ── Nightly generation ────────────────────────────────────────────────────

    async def _nightly_loop(self):
        """Sleep until 00:30, generate goals, sleep until next 00:30."""
        while self.running:
            now    = datetime.now()
            target = now.replace(hour=self.NIGHTLY_HOUR,
                                  minute=self.NIGHTLY_MINUTE,
                                  second=0, microsecond=0)
            if target <= now:
                target += timedelta(days=1)
            wait_s = (target - now).total_seconds()
            logger.info(f"[GoalEngine] Next nightly gen in {wait_s/3600:.1f}h")
            await asyncio.sleep(wait_s)
            if self.running:
                await self._generate_nightly_goals()

    async def _generate_nightly_goals(self):
        today = datetime.now().strftime("%Y-%m-%d")
        if self._last_nightly == today:
            return  # Already ran today
        self._last_nightly = today
        logger.info("[GoalEngine] Starting nightly goal generation...")

        if not self._recent_context:
            logger.info("[GoalEngine] No recent context — skipping.")
            return

        context_block = "\n".join(self._recent_context[-20:])
        prompt = (
            "You are reviewing the last day of conversations between a person and their AI companion.\n"
            "Based on what was discussed, generate 3-5 proactive follow-up goals.\n"
            "Each goal should be something the AI should remember to check on "
            "(e.g., 'Ask if they finished the project', 'Check if they ate today').\n\n"
            f"Recent conversation snippets:\n{context_block}\n\n"
            "Output a JSON list of goals. Each goal: {\"text\": ..., \"topic\": ..., "
            "\"priority\": \"high|medium|low\", \"trigger_keywords\": [...]}\n"
            "Output ONLY valid JSON, nothing else."
        )

        generated: List[Dict] = []
        if aiohttp:
            try:
                timeout = aiohttp.ClientTimeout(total=30)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.post(
                        f"{self.ollama_url}/api/generate",
                        json={"model": self.model, "prompt": prompt,
                              "stream": False,
                              "options": {"temperature": 0.4, "num_predict": 300}}
                    ) as resp:
                        if resp.status == 200:
                            data  = await resp.json()
                            raw   = data.get("response", "").strip()
                            start = raw.find("[")
                            end   = raw.rfind("]") + 1
                            if start >= 0 and end > start:
                                generated = json.loads(raw[start:end])
            except Exception as e:
                logger.warning(f"[GoalEngine] Nightly Ollama gen failed: {e}")

        if not generated:
            logger.info("[GoalEngine] No goals generated this nightly cycle.")
            return

        now        = datetime.now()
        expires_at = (now + timedelta(days=self.GOAL_TTL_DAYS)).isoformat()
        created_at = now.isoformat()

        new_goals: List[Dict] = []
        for i, g in enumerate(generated[:5]):
            goal = DEFAULT_GOAL.copy()
            goal.update({
                "id":               f"goal_{now.strftime('%Y%m%d')}_{i}",
                "text":             g.get("text", "")[:200],
                "topic":            g.get("topic", "general"),
                "priority":         g.get("priority", "medium"),
                "trigger_keywords": g.get("trigger_keywords", []),
                "created_at":       created_at,
                "expires_at":       expires_at,
                "status":           "active",
                "source":           "nightly_gen",
            })
            if goal["text"]:
                new_goals.append(goal)

        # Merge with existing active goals (keep MAX_GOALS total)
        existing_active = [g for g in self._goals
                           if g.get("status") == "active"
                           and g.get("expires_at", "") > now.isoformat()]
        self._goals = (new_goals + existing_active)[:self.MAX_GOALS]
        self._save_goals()
        logger.info(f"[GoalEngine] Generated {len(new_goals)} goals for {today}.")

    # ── Per-message update ────────────────────────────────────────────────────

    async def _update_from_message(self, payload: Dict):
        contact = payload.get("contact", "")
        message = payload.get("message", "")
        emotion = payload.get("emotion", "neutral")
        topic   = payload.get("topic", "general")

        # Append to rolling context for nightly gen
        if message:
            snippet = f"[{datetime.now().strftime('%H:%M')}] {message[:120]}"
            self._recent_context.append(snippet)
            if len(self._recent_context) > 100:
                self._recent_context = self._recent_context[-80:]

        # Expire old goals
        now = datetime.now().isoformat()
        for goal in self._goals:
            if goal.get("expires_at", "") < now and goal.get("status") == "active":
                goal["status"] = "expired"

        # Mark relevant goals as in_progress
        msg_lower = message.lower()
        for goal in self._goals:
            if goal.get("status") != "active":
                continue
            keywords = goal.get("trigger_keywords", [])
            if any(kw.lower() in msg_lower for kw in keywords) or \
               (goal.get("topic") and goal["topic"].lower() in msg_lower):
                goal["status"]       = "in_progress"
                goal["last_prompted"] = datetime.now().isoformat()
                logger.info(f"[GoalEngine] Goal triggered: '{goal['text'][:60]}'")

        self._save_goals()

    # ── Goal fragment for Orchestrator prompt ──────────────────────────────────

    def _build_goal_fragment(self, contact: str, message: str) -> str:
        """
        Return a compact string of active goals relevant to this message.
        Injected into the system prompt by the Orchestrator.
        """
        now       = datetime.now().isoformat()
        msg_lower = message.lower()
        relevant: List[Dict] = []

        for goal in self._goals:
            if goal.get("status") not in ("active", "in_progress"):
                continue
            if goal.get("expires_at", "") < now:
                continue
            keywords = goal.get("trigger_keywords", [])
            if keywords and any(kw.lower() in msg_lower for kw in keywords):
                relevant.append(goal)
            elif goal.get("priority") == "high":
                relevant.append(goal)

        if not relevant:
            return ""

        lines = ["[ACTIVE GOALS — background context, DO NOT mention directly unless natural to do so]"]
        for g in relevant[:3]:
            prio = g.get("priority", "medium")
            lines.append(f"  • ({prio}) {g['text']}")
        lines.append("[/ACTIVE GOALS]")
        return "\n".join(lines)

    # ── Admin commands ─────────────────────────────────────────────────────────

    def add_manual_goal(self, text: str, topic: str = "general",
                         priority: str = "high",
                         keywords: Optional[List[str]] = None,
                         expires_days: int = 3) -> Dict:
        """Called by owner via 'goal add ...' command in Orchestrator."""
        from datetime import timedelta
        now = datetime.now()
        goal = DEFAULT_GOAL.copy()
        goal.update({
            "id":               f"goal_manual_{now.strftime('%Y%m%d%H%M%S')}",
            "text":             text[:200],
            "topic":            topic,
            "priority":         priority,
            "trigger_keywords": keywords or [],
            "created_at":       now.isoformat(),
            "expires_at":       (now + timedelta(days=expires_days)).isoformat(),
            "status":           "active",
            "source":           "manual",
        })
        self._goals.insert(0, goal)
        self._goals = self._goals[:self.MAX_GOALS]
        self._save_goals()
        return goal

    def complete_goal(self, goal_id: str) -> bool:
        """Mark a goal as completed."""
        for g in self._goals:
            if g.get("id") == goal_id:
                g["status"] = "completed"
                self._save_goals()
                return True
        return False

    def list_goals(self, status: Optional[str] = None) -> List[Dict]:
        if status:
            return [g for g in self._goals if g.get("status") == status]
        return list(self._goals)

    # ── Persistence ───────────────────────────────────────────────────────────

    def _load_goals(self) -> List[Dict]:
        if self.goals_path.exists():
            try:
                with open(self.goals_path, encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"[GoalEngine] Goals file corrupt — starting fresh: {e}")
        return []

    def _save_goals(self):
        try:
            with open(self.goals_path, "w", encoding="utf-8") as f:
                json.dump(self._goals, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"[GoalEngine] Could not save goals: {e}")
