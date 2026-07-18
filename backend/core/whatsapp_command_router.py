"""
WhatsApp Command Router
=======================
Parses raw WhatsApp messages from the owner and dispatches them to the
correct handler BEFORE they hit the full NexusBrain pipeline.

Priority order:
  1. Session end trigger         ("end session", "bye", …)
  2. @mention one-shot           ("@atlas what is quantum?")
  3. call @agent session open    ("call @atlas")
  4. / commands (CRUD + system)  ("/task add …", "/status", …)
  5. Active session passthrough  (message goes to session's agent)
  6. Normal brain fallthrough    (returns None → caller uses brain.process_input)
"""

import asyncio
import datetime
import logging
import os
import re
import json
from pathlib import Path
from typing import Optional, Dict, Any

from core.whatsapp_session_manager import session_manager, KNOWN_AGENTS

logger = logging.getLogger("WhatsAppCommandRouter")

# ── Regex Patterns ────────────────────────────────────────────────────────────

# @atlas tell me about ...
RE_MENTION = re.compile(r"^@(\w+)\s+(.*)", re.DOTALL | re.IGNORECASE)

# call @atlas  |  talk to @atlas  |  connect atlas
RE_CALL = re.compile(
    r"^(?:call|talk\s+to|connect|open|start|chat\s+with)\s+@?(\w+)$",
    re.IGNORECASE
)

# /task add <text>  |  /task list  |  /task done <id>  |  /task delete <id>
RE_TASK = re.compile(r"^/task\s+(add|list|done|delete|del|check|ls)\s*(.*)", re.IGNORECASE)

# /remind 08:30 take medicine
RE_REMIND = re.compile(r"^/remind\s+(list|cancel|add)?\s*(.*)", re.IGNORECASE)
RE_REMIND_TIME = re.compile(r"^/remind\s+(\d{1,2}[:.]\d{2})\s+(.*)", re.IGNORECASE)

# /memory save <text>  |  /memory recall <query>  |  /memory forget <query>
RE_MEMORY = re.compile(r"^/memory\s+(save|recall|forget|search|list)\s*(.*)", re.IGNORECASE)

# /know <fact>  (shortcut for /memory save)
RE_KNOW = re.compile(r"^/know\s+(.*)", re.IGNORECASE)

# /progress  |  /progress <task_id>
RE_PROGRESS = re.compile(r"^/progress\s*(.*)", re.IGNORECASE)

# Health commands
RE_HEALTH = re.compile(r"^/(health|status_health)\s*(.*)", re.IGNORECASE)
RE_MEALS = re.compile(r"^/(meals|meal|food)\s*(.*)", re.IGNORECASE)
RE_SYMPTOMS = re.compile(r"^/(symptoms|symptom)\s*(.*)", re.IGNORECASE)


class WhatsAppCommandRouter:
    """
    Stateless parser + dispatcher.
    Every public method returns a dict with at least {"response": str}
    or None to signal "fall through to the brain".
    """

    def __init__(self, brain=None):
        self.brain = brain
        # Simple file-based task store (backend/data/wa_tasks.json)
        self._task_file = Path("data/wa_tasks.json")
        self._remind_file = Path("data/wa_reminders.json")
        self._task_file.parent.mkdir(parents=True, exist_ok=True)
        from core.health_store import health_store
        self.health_store = health_store


    # ── Main Entry ────────────────────────────────────────────────────────────

    async def route(
        self,
        text: str,
        user_jid: str,
        context: Dict,
        brain_process_fn,          # async callable: (text, source, sender, ctx) -> dict
    ) -> Optional[Dict[str, Any]]:
        """
        Returns a response dict if this router handled the message,
        or None to signal the caller should fall through to the full brain pipeline.
        """
        # Intercept Media / Meal Photos
        if context.get("media_path") and os.path.exists(context["media_path"]):
            # Trigger Vision analysis for food log
            try:
                from agents.vision_agent import VisionTracker
                tracker = VisionTracker()
                analysis = await tracker.analyze_meal(context["media_path"])
                
                # Log the meal
                today_str = datetime.date.today().isoformat()
                meal_record = {
                    "time": datetime.datetime.now().strftime("%I:%M %p"),
                    "items": analysis.get("items", []),
                    "portion_sizes": analysis.get("portion_sizes", "Standard"),
                    "macros": analysis.get("macros", {}),
                    "image_path": context["media_path"]
                }
                self.health_store.add_meal(today_str, meal_record)
                
                # Fetch Mother configuration to respond in Amma's tone
                mother_style = ""
                try:
                    with open("config/mother_persona.json", "r", encoding="utf-8") as f:
                        config = json.load(f)
                        mother_style = f"RESPOND EXACTLY IN THIS TONE: {config.get('tone_instructions')}"
                except Exception:
                    pass
                
                # Render response
                from core.ai_engine import AIEngine
                engine = AIEngine()
                await engine.initialize()
                response = await engine.generate(
                    prompt=f"The child shared a photo of their meal. Vision analysis results: {json.dumps(analysis)}. Respond with maternal advice/reaction about this meal in Tenglish.",
                    system=mother_style
                )
                await engine.close()
                return self._resp(response)
            except Exception as e:
                logger.error(f"Failed to process media upload: {e}")
                return self._resp("Sorry Kanna, having trouble checking this photo.")

        stripped = text.strip()
        lower = stripped.lower()

        # ── 1. Session end trigger ────────────────────────────────────────────
        if session_manager.is_end_trigger(stripped):
            agent_id = session_manager.end_session(user_jid)
            if agent_id:
                return self._resp(session_manager.format_session_end(agent_id))
            return self._resp("No active session — you're already in the main brain. 🧠")

        # ── 2. @mention (one-shot) ────────────────────────────────────────────
        m = RE_MENTION.match(stripped)
        if m:
            raw_name, rest = m.group(1), m.group(2).strip()
            agent_id = session_manager.resolve_agent_name(raw_name)
            if agent_id:
                return await self._dispatch_to_agent(agent_id, rest, user_jid, context, brain_process_fn)
            # Unknown agent — fall through to brain (might handle it)

        # ── 3. call @agent — open a focused session ───────────────────────────
        m = RE_CALL.match(stripped)
        if m:
            raw_name = m.group(1)
            agent_id = session_manager.resolve_agent_name(raw_name)
            if agent_id:
                session_manager.start_session(user_jid, agent_id)
                return self._resp(session_manager.format_session_start(agent_id))
            return self._resp(
                f"❓ Unknown agent *{raw_name}*.\n"
                f"Try `/agents` to see the full fleet."
            )

        # ── 4. /commands ──────────────────────────────────────────────────────
        if stripped.startswith("/"):
            result = await self._handle_slash_command(stripped, user_jid, context)
            if result is not None:
                return result

        # ── 5. Active focused session passthrough ─────────────────────────────
        session = session_manager.get_session(user_jid)
        if session:
            session_manager.touch_session(user_jid)
            logger.info(f"[Router] Active session with {session.agent_id} — forwarding message")
            result = await self._dispatch_to_agent(
                session.agent_id, stripped, user_jid, context, brain_process_fn
            )
            # Append session context hint to response
            if result:
                result["response"] = (
                    f"[*{session.agent_id.upper()}*] {result.get('response', '')}"
                )
            return result

        # ── 6. Fall through → caller uses brain.process_input ─────────────────
        return None

    # ── Agent Dispatch ────────────────────────────────────────────────────────

    async def _dispatch_to_agent(
        self,
        agent_id: str,
        message: str,
        user_jid: str,
        context: Dict,
        brain_process_fn,
    ) -> Dict:
        """Route a message to a specific agent via the brain pipeline."""
        logger.info(f"[Router] Dispatching to agent: {agent_id} → '{message[:60]}'")
        ctx = dict(context)
        ctx["target_agent"] = agent_id
        ctx["agent_override"] = True
        try:
            result = await brain_process_fn(
                raw_input=message,
                source="whatsapp",
                sender=user_jid,
                context=ctx,
            )
            # If the brain returns a generic response, prefix with agent name
            if result and "response" in result:
                result["agent_name"] = agent_id.capitalize()
            return result or self._resp(f"*{agent_id.upper()}* has no response right now.")
        except Exception as e:
            logger.error(f"[Router] Agent dispatch error: {e}")
            return self._resp(f"⚠️ Error reaching agent *{agent_id}*: {e}")

    # ── Slash Command Handlers ────────────────────────────────────────────────

    async def _handle_slash_command(self, text: str, user_jid: str, context: Dict) -> Optional[Dict]:
        lower = text.lower()

        # /status
        if lower in ("/status", "/s"):
            return await self._cmd_status()

        # /agents  /fleet
        if lower in ("/agents", "/fleet", "/list"):
            return self._resp(session_manager.list_all_agents())

        # /help
        if lower in ("/help", "/h", "/?"):
            return self._resp(self._help_text())

        # /session
        if lower == "/session":
            session = session_manager.get_session(user_jid)
            if session:
                return self._resp(session.summary())
            return self._resp("No active agent session. Use `call @<agent>` to start one.")

        # /progress [task_id]
        m = RE_PROGRESS.match(text)
        if m:
            return await self._cmd_progress(m.group(1).strip())

        # /task ...
        m = RE_TASK.match(text)
        if m:
            return await self._cmd_task(m.group(1).lower(), m.group(2).strip())

        # /remind ...
        m = RE_REMIND_TIME.match(text)
        if m:
            return await self._cmd_remind_add(m.group(1), m.group(2).strip())

        m = RE_REMIND.match(text)
        if m:
            return await self._cmd_remind(m.group(1) or "list", m.group(2).strip())

        # /memory ...
        m = RE_MEMORY.match(text)
        if m:
            return await self._cmd_memory(m.group(1).lower(), m.group(2).strip())

        # /know <fact>
        m = RE_KNOW.match(text)
        if m:
            return await self._cmd_memory("save", m.group(1).strip())

        # /health
        m = RE_HEALTH.match(text)
        if m:
            return await self._cmd_health(m.group(2).strip())

        # /meals
        m = RE_MEALS.match(text)
        if m:
            return await self._cmd_meals(m.group(2).strip())

        # /symptoms
        m = RE_SYMPTOMS.match(text)
        if m:
            return await self._cmd_symptoms(m.group(2).strip())

        # /mode fleet | /mode single
        if lower.startswith("/mode"):
            parts = text.split()
            mode = parts[1] if len(parts) > 1 else ""
            return await self._cmd_mode(mode)

        # Unknown / command — fall through
        return None

    # ── /status ───────────────────────────────────────────────────────────────

    async def _cmd_status(self) -> Dict:
        lines = ["🧠 *JARVIS NEXUS-X Status*\n"]
        if self.brain:
            try:
                health = await self.brain.health_check()
                for mod, status in health.items():
                    icon = "✅" if status == "available" else "⚠️"
                    lines.append(f"{icon} *{mod}*: {status}")
            except Exception as e:
                lines.append(f"⚠️ Health check failed: {e}")
        else:
            lines.append("⚠️ Brain not connected to router")

        # Active sessions
        active = [
            f"  • {jid.split('@')[0]} → @{s.agent_id}"
            for jid, s in session_manager._sessions.items()
            if not s.is_expired()
        ]
        if active:
            lines.append(f"\n💬 *Active Sessions ({len(active)})*:")
            lines.extend(active)
        else:
            lines.append("\n💬 No active agent sessions")

        lines.append(f"\n⏰ {datetime.datetime.now().strftime('%d %b %Y, %H:%M:%S')}")
        return self._resp("\n".join(lines))

    # ── /progress ─────────────────────────────────────────────────────────────

    async def _cmd_progress(self, task_id: str = "") -> Dict:
        try:
            from core.fleet.manager import fleet_manager
            if task_id:
                # Specific task
                status = fleet_manager.get_task_status(task_id) if hasattr(fleet_manager, "get_task_status") else None
                if status:
                    return self._resp(f"📋 *Task {task_id}*\n{status}")
                return self._resp(f"❓ Task `{task_id}` not found.")
            else:
                # All tasks
                summary = fleet_manager.get_fleet_summary() if hasattr(fleet_manager, "get_fleet_summary") else "No fleet summary available"
                return self._resp(f"🚀 *Fleet Progress*\n{summary}")
        except Exception as e:
            logger.warning(f"[Router] Progress check failed: {e}")
            return self._resp(f"⚠️ Could not fetch fleet progress: {e}")

    # ── /task ─────────────────────────────────────────────────────────────────

    async def _cmd_task(self, action: str, args: str) -> Dict:
        tasks = self._load_json(self._task_file, [])

        if action in ("add",):
            if not args:
                return self._resp("❓ Usage: `/task add <description>`")
            task_id = len(tasks) + 1
            task = {
                "id": task_id,
                "text": args,
                "done": False,
                "created": datetime.datetime.now().isoformat(),
            }
            tasks.append(task)
            self._save_json(self._task_file, tasks)
            return self._resp(f"✅ *Task #{task_id} added*\n_{args}_")

        elif action in ("list", "ls"):
            if not tasks:
                return self._resp("📋 No tasks. Add one with `/task add <text>`")
            pending = [t for t in tasks if not t["done"]]
            done = [t for t in tasks if t["done"]]
            lines = [f"📋 *Tasks ({len(pending)} pending, {len(done)} done)*\n"]
            for t in pending:
                lines.append(f"• #{t['id']} {t['text']}")
            if done:
                lines.append(f"\n✅ *Completed ({len(done)})*")
                for t in done[-5:]:  # last 5 done
                    lines.append(f"• ~~#{t['id']} {t['text']}~~")
            return self._resp("\n".join(lines))

        elif action in ("done", "check"):
            if not args.isdigit():
                return self._resp("❓ Usage: `/task done <id>`")
            tid = int(args)
            for t in tasks:
                if t["id"] == tid:
                    t["done"] = True
                    t["completed"] = datetime.datetime.now().isoformat()
                    self._save_json(self._task_file, tasks)
                    return self._resp(f"✅ Task #{tid} marked *done*!\n_{t['text']}_")
            return self._resp(f"❓ Task #{tid} not found.")

        elif action in ("delete", "del"):
            if not args.isdigit():
                return self._resp("❓ Usage: `/task delete <id>`")
            tid = int(args)
            original_len = len(tasks)
            tasks = [t for t in tasks if t["id"] != tid]
            if len(tasks) < original_len:
                self._save_json(self._task_file, tasks)
                return self._resp(f"🗑️ Task #{tid} deleted.")
            return self._resp(f"❓ Task #{tid} not found.")

        return self._resp("❓ Unknown task action. Try: `add`, `list`, `done`, `delete`")

    # ── /remind ───────────────────────────────────────────────────────────────

    async def _cmd_remind_add(self, time_str: str, text: str) -> Dict:
        reminders = self._load_json(self._remind_file, [])
        # Normalise HH:MM
        time_str = time_str.replace(".", ":")
        rid = len(reminders) + 1
        reminder = {
            "id": rid,
            "time": time_str,
            "text": text,
            "active": True,
            "created": datetime.datetime.now().isoformat(),
        }
        reminders.append(reminder)
        self._save_json(self._remind_file, reminders)
        return self._resp(f"⏰ *Reminder #{rid} set for {time_str}*\n_{text}_")

    async def _cmd_remind(self, action: str, args: str) -> Dict:
        reminders = self._load_json(self._remind_file, [])

        if action in (None, "list", "ls", ""):
            active = [r for r in reminders if r.get("active", True)]
            if not active:
                return self._resp("⏰ No active reminders. Set one with:\n`/remind 08:30 take medicine`")
            lines = [f"⏰ *Active Reminders ({len(active)})*\n"]
            for r in active:
                lines.append(f"• #{r['id']} @ {r['time']} — {r['text']}")
            return self._resp("\n".join(lines))

        elif action == "cancel":
            if not args.isdigit():
                return self._resp("❓ Usage: `/remind cancel <id>`")
            rid = int(args)
            for r in reminders:
                if r["id"] == rid:
                    r["active"] = False
                    self._save_json(self._remind_file, reminders)
                    return self._resp(f"✅ Reminder #{rid} cancelled.")
            return self._resp(f"❓ Reminder #{rid} not found.")

        return self._resp("⏰ Usage: `/remind HH:MM <text>` or `/remind list` or `/remind cancel <id>`")

    # ── /memory ───────────────────────────────────────────────────────────────

    async def _cmd_memory(self, action: str, args: str) -> Dict:
        if action == "save":
            if not args:
                return self._resp("❓ Usage: `/memory save <fact or note>`")
            if self.brain and "memory" in self.brain.modules:
                try:
                    await self.brain.modules["memory"].remember(
                        content=args,
                        importance=0.8,
                        metadata={"source": "whatsapp_command"},
                        tags=["@whatsapp", "@owner"]
                    )
                    return self._resp(f"💾 *Saved to memory*\n_{args}_")
                except Exception as e:
                    logger.error(f"[Router] Memory save error: {e}")
                    return self._resp(f"⚠️ Memory save failed: {e}")
            return self._resp("⚠️ Memory module not available.")

        elif action in ("recall", "search"):
            if not args:
                return self._resp("❓ Usage: `/memory recall <query>`")
            if self.brain and "memory" in self.brain.modules:
                try:
                    results = await self.brain.modules["memory"].recall(args, limit=5)
                    if not results:
                        return self._resp(f"🔍 No memories found for *{args}*")
                    lines = [f"🔍 *Memory Recall: '{args}'*\n"]
                    for i, r in enumerate(results, 1):
                        content = r.get("content", r) if isinstance(r, dict) else str(r)
                        lines.append(f"{i}. {str(content)[:120]}")
                    return self._resp("\n".join(lines))
                except Exception as e:
                    return self._resp(f"⚠️ Memory recall failed: {e}")
            return self._resp("⚠️ Memory module not available.")

        elif action == "forget":
            if not args:
                return self._resp("❓ Usage: `/memory forget <query>`")
            return self._resp(
                f"⚠️ Memory deletion is a sensitive operation.\n"
                f"Use the JARVIS dashboard to delete: *{args}*\n"
                f"_(WhatsApp memory deletion is disabled for safety)_"
            )

        elif action in ("list", "ls"):
            if self.brain and "memory" in self.brain.modules:
                try:
                    results = await self.brain.modules["memory"].recall("", limit=10)
                    if not results:
                        return self._resp("🧠 Memory is empty.")
                    lines = [f"🧠 *Recent Memories ({len(results)})*\n"]
                    for i, r in enumerate(results, 1):
                        content = r.get("content", r) if isinstance(r, dict) else str(r)
                        lines.append(f"{i}. {str(content)[:100]}")
                    return self._resp("\n".join(lines))
                except Exception as e:
                    return self._resp(f"⚠️ Memory list failed: {e}")
            return self._resp("⚠️ Memory module not available.")

        return self._resp("❓ Memory actions: `save`, `recall`, `forget`, `list`")

    # ── /mode ─────────────────────────────────────────────────────────────────

    async def _cmd_mode(self, mode: str) -> Dict:
        mode = mode.lower().strip()
        if not mode:
            return self._resp("❓ Usage: `/mode fleet` or `/mode single`")
        if mode == "fleet":
            os.environ["FLEET_MODE"] = "true"
            return self._resp("🚀 *Fleet Mode ACTIVE* — multiple agents collaborating")
        elif mode in ("single", "solo"):
            os.environ["FLEET_MODE"] = "false"
            return self._resp("🧠 *Single Agent Mode* — direct brain response")
        return self._resp(f"❓ Unknown mode `{mode}`. Options: `fleet`, `single`")

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _resp(text: str, emotion: str = "neutral") -> Dict:
        return {"response": text, "emotion": emotion, "intent": "whatsapp_command"}

    def _load_json(self, path: Path, default):
        try:
            if path.exists():
                return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
        return default

    def _save_json(self, path: Path, data):
        try:
            path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception as e:
            logger.error(f"[Router] JSON save error ({path}): {e}")

    @staticmethod
    def _help_text() -> str:
        return (
            "🤖 *JARVIS WhatsApp Command Bridge*\n\n"
            "*Agent Chat*\n"
            "• `@<agent> <message>` — one-shot message to an agent\n"
            "• `call @<agent>` — open focused session\n"
            "• `end session` — return to main brain\n\n"
            "*System*\n"
            "• `/status` — system health\n"
            "• `/agents` — list all 23 agents\n"
            "• `/session` — current session info\n"
            "• `/progress` — fleet task progress\n"
            "• `/mode fleet|single` — switch mode\n\n"
            "*Tasks*\n"
            "• `/task add <text>`\n"
            "• `/task list`\n"
            "• `/task done <id>`\n"
            "• `/task delete <id>`\n\n"
            "*Reminders*\n"
            "• `/remind HH:MM <text>`\n"
            "• `/remind list`\n"
            "• `/remind cancel <id>`\n\n"
            "*Memory*\n"
            "• `/memory save <fact>`\n"
            "• `/memory recall <query>`\n"
            "• `/memory list`\n"
            "• `/know <fact>` (shortcut)\n\n"
            "_Send a voice note to talk hands-free_ 🎙️"
        )

    # ── Health Guardian Commands ──────────────────────────────────────────────
    async def _cmd_health(self, args: str) -> Dict:
        today_str = datetime.date.today().isoformat()
        log = self.health_store.get_log(today_str)
        
        meals_count = len(log.get("meals", []))
        symptoms_str = ", ".join(log.get("symptoms", [])) or "None logged"
        mood = log.get("mood", "neutral")
        analysis = log.get("analysis_plan", "No analysis plan generated yet for today.")

        res = (
            f"🩺 *DAILY HEALTH MONITOR ({today_str})*\n\n"
            f"🍽️ *Meals Logged*: {meals_count} meals\n"
            f"🤒 *Symptoms*: {symptoms_str}\n"
            f"🎭 *Mood*: {mood}\n\n"
            f"📋 *Mother's Health Plan & Tips*:\n{analysis}"
        )
        return self._resp(res)

    async def _cmd_meals(self, args: str) -> Dict:
        today_str = datetime.date.today().isoformat()
        if args:
            # Manually add a meal text
            meal_record = {
                "time": datetime.datetime.now().strftime("%I:%M %p"),
                "items": [args],
                "portion_sizes": "Standard",
                "macros": {"calories": 0, "protein": 0, "carbs": 0, "fats": 0},
                "image_path": None
            }
            self.health_store.add_meal(today_str, meal_record)
            return self._resp(f"🍽️ Added meal: *{args}* to today's plan!")
        
        # List meals
        log = self.health_store.get_log(today_str)
        meals = log.get("meals", [])
        if not meals:
            return self._resp("🍽️ No meals logged today yet. Share a picture of your food to auto-log it!")
        
        lines = [f"🍽️ *Today's Meals ({today_str})*\n"]
        for i, m in enumerate(meals, 1):
            items_str = ", ".join(m.get("items", []))
            lines.append(f"{i}. [{m.get('time')}] {items_str} ({m.get('portion_sizes')})")
        return self._resp("\n".join(lines))

    async def _cmd_symptoms(self, args: str) -> Dict:
        today_str = datetime.date.today().isoformat()
        if args:
            # Add symptom
            self.health_store.add_symptom(today_str, args)
            return self._resp(f"🤒 Logged symptom: *{args}*. Added to daily tracker.")
        
        # List symptoms
        log = self.health_store.get_log(today_str)
        symptoms = log.get("symptoms", [])
        if not symptoms:
            return self._resp("🤒 No symptoms logged today. Stay healthy!")
        
        s_str = ", ".join(symptoms)
        return self._resp(f"🤒 *Today's Symptoms*: {s_str}")

