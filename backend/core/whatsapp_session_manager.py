"""
WhatsApp Session Manager
========================
Tracks focused agent sessions so that after typing "call @atlas",
every subsequent message goes exclusively to Atlas until:
  - The user says "end session" / "exit" / "bye"
  - The session times out (WHATSAPP_SESSION_TIMEOUT seconds of inactivity)
"""

import time
import logging
import os
from typing import Optional, Dict

logger = logging.getLogger("WhatsAppSessionManager")

# All 23 registered agent IDs (must match config/agents/*.yaml stems)
KNOWN_AGENTS = {
    "arion", "atlas", "atlas_x", "axiom", "brix", "cleo", "echo",
    "flux", "hank", "iris", "kai", "lyra", "muse", "nova", "pipe",
    "rex", "sable", "sage", "stack", "terra", "vega", "vera", "zero"
}

# Friendly aliases  →  canonical agent id
AGENT_ALIASES: Dict[str, str] = {
    "arion":   "arion",
    "atlas":   "atlas",
    "atlax":   "atlas_x",
    "atlas_x": "atlas_x",
    "axiom":   "axiom",
    "brix":    "brix",
    "cleo":    "cleo",
    "echo":    "echo",
    "flux":    "flux",
    "hank":    "hank",
    "iris":    "iris",
    "kai":     "kai",
    "lyra":    "lyra",
    "muse":    "muse",
    "nova":    "nova",
    "pipe":    "pipe",
    "rex":     "rex",
    "sable":   "sable",
    "sage":    "sage",
    "stack":   "stack",
    "terra":   "terra",
    "vega":    "vega",
    "vera":    "vera",
    "zero":    "zero",
}

# Commands that end the current session
SESSION_END_TRIGGERS = {
    "end session", "end chat", "exit", "exit session", "bye",
    "stop", "cancel session", "back", "go back", "main"
}

_SESSION_TIMEOUT = int(os.getenv("WHATSAPP_SESSION_TIMEOUT", "300"))  # 5 min default


class AgentSession:
    """Represents a focused conversation with a single agent."""

    def __init__(self, user_jid: str, agent_id: str):
        self.user_jid = user_jid
        self.agent_id = agent_id
        self.started_at = time.time()
        self.last_active = time.time()
        self.message_count = 0

    def touch(self):
        self.last_active = time.time()
        self.message_count += 1

    def is_expired(self) -> bool:
        return (time.time() - self.last_active) > _SESSION_TIMEOUT

    def summary(self) -> str:
        elapsed = int(time.time() - self.started_at)
        m, s = divmod(elapsed, 60)
        return (
            f"🤖 Session with *{self.agent_id.upper()}*\n"
            f"⏱ Active: {m}m {s}s | 💬 Messages: {self.message_count}"
        )


class WhatsAppSessionManager:
    """
    Central store for all active agent sessions, keyed by user JID.
    Thread-safe for single-process use (asyncio context).
    """

    def __init__(self):
        # user_jid → AgentSession
        self._sessions: Dict[str, AgentSession] = {}

    # ── Public API ──────────────────────────────────────────────────────────

    def resolve_agent_name(self, raw: str) -> Optional[str]:
        """
        Given a raw name like 'Atlas', 'ATLAS', 'atlax',
        return the canonical agent id or None if not recognised.
        """
        return AGENT_ALIASES.get(raw.lower().strip())

    def start_session(self, user_jid: str, agent_id: str) -> AgentSession:
        """Open (or replace) a focused session for this user."""
        session = AgentSession(user_jid, agent_id)
        self._sessions[user_jid] = session
        logger.info(f"[Session] {user_jid} → started session with {agent_id}")
        return session

    def end_session(self, user_jid: str) -> Optional[str]:
        """
        Close any active session for this user.
        Returns the agent_id that was closed, or None if no session existed.
        """
        session = self._sessions.pop(user_jid, None)
        if session:
            logger.info(f"[Session] {user_jid} → ended session with {session.agent_id}")
            return session.agent_id
        return None

    def get_session(self, user_jid: str) -> Optional[AgentSession]:
        """
        Return the active (non-expired) session for this user, or None.
        Expired sessions are cleaned up automatically.
        """
        session = self._sessions.get(user_jid)
        if session is None:
            return None
        if session.is_expired():
            logger.info(f"[Session] {user_jid} → session with {session.agent_id} EXPIRED")
            del self._sessions[user_jid]
            return None
        return session

    def touch_session(self, user_jid: str):
        """Refresh the last-active timestamp so the session doesn't expire."""
        session = self._sessions.get(user_jid)
        if session:
            session.touch()

    def is_end_trigger(self, text: str) -> bool:
        """Returns True if the message should close the current session."""
        return text.strip().lower() in SESSION_END_TRIGGERS

    def list_all_agents(self) -> str:
        """Returns a formatted WhatsApp-friendly list of all agents."""
        lines = ["🤖 *JARVIS Agent Fleet* — 23 Agents Online\n"]
        agent_info = {
            "arion":   ("The Companion",    "Tenglish buddy, daily support"),
            "atlas":   ("The Scholar",      "Research & deep learning"),
            "atlas_x": ("The Strategist",   "Advanced planning & analysis"),
            "axiom":   ("The Architect",    "System design & code"),
            "brix":    ("The Builder",      "Construction & automation"),
            "cleo":    ("The Archivist",    "Knowledge & memory recall"),
            "echo":    ("The Mirror",       "Reflection & feedback"),
            "flux":    ("The Adapter",      "Real-time adjustments"),
            "hank":    ("The Enforcer",     "Security & access control"),
            "iris":    ("The Observer",     "Vision & screen analysis"),
            "kai":     ("The Linguist",     "Translation & language"),
            "lyra":    ("The Composer",     "Creative writing & music"),
            "muse":    ("The Creator",      "Ideas & inspiration"),
            "nova":    ("The Innovator",    "New tech & experiments"),
            "pipe":    ("The Engineer",     "Pipelines & data flows"),
            "rex":     ("The Guardian",     "Protection & monitoring"),
            "sable":   ("The Shadow",       "Stealth & background ops"),
            "sage":    ("The Philosopher",  "Deep wisdom & reflection"),
            "stack":   ("The Coder",        "Full-stack development"),
            "terra":   ("The Planner",      "Tasks & scheduling"),
            "vega":    ("The Analyst",      "Data & visualisation"),
            "vera":    ("The Counselor",    "Emotional support & wellbeing"),
            "zero":    ("The Pioneer",      "Cutting-edge R&D"),
        }
        for agent_id, (archetype, role) in agent_info.items():
            lines.append(f"• *@{agent_id}* — _{archetype}_\n  {role}")
        lines.append("\n_Tip: type `@<name> <message>` or `call @<name>` for a focused session_")
        return "\n".join(lines)

    def format_session_start(self, agent_id: str) -> str:
        info = {
            "arion":  "warm Tenglish companion 🌟",
            "atlas":  "research scholar 📚",
            "axiom":  "system architect 🏗️",
            "cleo":   "knowledge archivist 🗄️",
            "vega":   "data analyst 📊",
            "stack":  "full-stack coder 💻",
            "terra":  "task planner 📋",
            "vera":   "emotional counselor 💚",
        }.get(agent_id, "specialist agent 🤖")
        return (
            f"✅ *Session opened with {agent_id.upper()}* ({info})\n"
            f"Every message now goes directly to {agent_id.capitalize()}.\n"
            f"Type `end session` to return to the main brain.\n"
            f"_(Session auto-expires after {_SESSION_TIMEOUT//60} min of inactivity)_"
        )

    def format_session_end(self, agent_id: str) -> str:
        return (
            f"👋 *{agent_id.upper()} session closed.*\n"
            f"You're back in the main JARVIS brain.\n"
            f"_Try `@{agent_id} <message>` for a quick one-off message._"
        )


# Singleton instance — import this everywhere
session_manager = WhatsAppSessionManager()
