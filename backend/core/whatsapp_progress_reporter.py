"""
WhatsApp Progress Reporter
==========================
Background async loop that watches for completed fleet tasks,
finishing background jobs, and reminder fires — then pushes
proactive notifications to the owner's WhatsApp JID.

Start it via:
    reporter = WhatsAppProgressReporter(bridge, brain)
    asyncio.create_task(reporter.start())
"""

import asyncio
import datetime
import json
import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger("WhatsAppProgressReporter")

# How often to poll internal queues (seconds)
_POLL_INTERVAL = float(os.getenv("WA_PROGRESS_POLL_INTERVAL", "5"))

# File where progress reporter writes events to notify (shared memory)
_PROGRESS_EVENTS_FILE = Path("data/wa_progress_events.json")

# Reminders data file (same one WhatsAppCommandRouter writes)
_REMIND_FILE = Path("data/wa_reminders.json")


class WhatsAppProgressReporter:
    """
    Proactive push notification engine for WhatsApp.

    Hooks into:
      - Fleet manager task completion events
      - Reminder file (fires when current time matches)
      - External events written to data/wa_progress_events.json
      - Brain module health changes
    """

    def __init__(self, bridge, brain=None):
        """
        bridge : WhatsAppBridge instance (for _enqueue_outgoing)
        brain  : NexusBrain instance (for fleet/module access)
        """
        self.bridge = bridge
        self.brain = brain
        self.running = False
        self._admin_jid: Optional[str] = None
        self._seen_events: set = set()
        _PROGRESS_EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        if not _PROGRESS_EVENTS_FILE.exists():
            _PROGRESS_EVENTS_FILE.write_text("[]")

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    async def start(self):
        """Launch all background polling loops."""
        self.running = True
        self._admin_jid = self._resolve_admin_jid()
        if not self._admin_jid:
            logger.warning("[ProgressReporter] ADMIN_NUMBER not set — push notifications disabled.")
            return

        logger.info(
            f"[ProgressReporter] Started. Pushing to {self._admin_jid} "
            f"every {_POLL_INTERVAL}s"
        )
        # Run all loops concurrently
        await asyncio.gather(
            self._loop_event_file(),
            self._loop_reminders(),
            self._loop_fleet_tasks(),
            return_exceptions=True,
        )

    def stop(self):
        self.running = False

    # ── Push Helper ───────────────────────────────────────────────────────────

    async def push(self, text: str):
        """Send a proactive WhatsApp message to the admin."""
        if not self._admin_jid:
            logger.debug("[ProgressReporter] No admin JID — skipping push")
            return
        try:
            await self.bridge._enqueue_outgoing(self._admin_jid, text=text, media_path=None)
            logger.info(f"[ProgressReporter] Pushed: {text[:60]}...")
        except Exception as e:
            logger.error(f"[ProgressReporter] Push failed: {e}")

    # ── External Event File Loop ───────────────────────────────────────────────

    async def _loop_event_file(self):
        """
        Other parts of the system can drop events into data/wa_progress_events.json
        in this format:
            { "id": "unique_id", "message": "text to send", "sent": false }
        This loop picks them up and pushes them to WhatsApp.
        """
        while self.running:
            try:
                events = self._load_events()
                changed = False
                for event in events:
                    eid = event.get("id", "")
                    if event.get("sent") or eid in self._seen_events:
                        continue
                    msg = event.get("message", "")
                    if msg:
                        await self.push(msg)
                        event["sent"] = True
                        self._seen_events.add(eid)
                        changed = True
                if changed:
                    self._save_events(events)
            except Exception as e:
                logger.debug(f"[ProgressReporter] Event file error: {e}")
            await asyncio.sleep(_POLL_INTERVAL)

    # ── Reminder Loop ──────────────────────────────────────────────────────────

    async def _loop_reminders(self):
        """
        Watches data/wa_reminders.json for reminders whose time has come
        and pushes a WhatsApp notification.
        """
        _fired: set = set()
        while self.running:
            try:
                now = datetime.datetime.now()
                current_hhmm = now.strftime("%H:%M")
                reminders = self._load_json(_REMIND_FILE, [])
                changed = False
                for r in reminders:
                    if not r.get("active", True):
                        continue
                    rid = r.get("id")
                    fire_key = f"{rid}_{current_hhmm}"
                    if fire_key in _fired:
                        continue
                    if r.get("time", "") == current_hhmm:
                        await self.push(
                            f"⏰ *REMINDER #{rid}*\n"
                            f"_{r.get('text', '')}_\n\n"
                            f"_Reply `/remind cancel {rid}` to dismiss_"
                        )
                        _fired.add(fire_key)
                        changed = True
                        # Keep only last 200 fired keys to avoid memory growth
                        if len(_fired) > 200:
                            _fired = set(list(_fired)[-100:])
            except Exception as e:
                logger.debug(f"[ProgressReporter] Reminder loop error: {e}")
            await asyncio.sleep(30)  # Check every 30s

    # ── Fleet Task Loop ────────────────────────────────────────────────────────

    async def _loop_fleet_tasks(self):
        """
        Watches fleet_manager for newly completed tasks and pushes results.
        Uses a simple 'seen' set so each task result is pushed only once.
        """
        _notified: set = set()
        while self.running:
            try:
                from core.fleet.manager import fleet_manager
                if hasattr(fleet_manager, "get_completed_tasks"):
                    completed = fleet_manager.get_completed_tasks()
                    for task in completed:
                        tid = task.get("id") or task.get("task_id")
                        if not tid or tid in _notified:
                            continue
                        _notified.add(tid)
                        agent = task.get("agent", "fleet")
                        result_snippet = str(task.get("result", ""))[:200]
                        await self.push(
                            f"✅ *Task Complete* — by *{agent.upper()}*\n"
                            f"📌 {task.get('description', 'Background task')}\n"
                            f"💬 {result_snippet}"
                        )
                elif hasattr(fleet_manager, "task_log"):
                    # Fallback: scan task_log for done items
                    for tid, task in list(fleet_manager.task_log.items()):
                        if task.get("status") == "done" and tid not in _notified:
                            _notified.add(tid)
                            await self.push(
                                f"✅ *Task Done* (ID: {tid})\n"
                                f"_{str(task.get('description', ''))[:120]}_"
                            )
            except Exception as e:
                logger.debug(f"[ProgressReporter] Fleet loop error: {e}")
            await asyncio.sleep(_POLL_INTERVAL * 2)  # Check every 10s by default

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _resolve_admin_jid() -> Optional[str]:
        """Constructs the WhatsApp JID for the admin from env."""
        admin = os.getenv("ADMIN_NUMBER", "").strip()
        if not admin:
            return None
        if "@" not in admin:
            admin = f"{admin}@c.us"
        return admin

    def _load_events(self):
        return self._load_json(_PROGRESS_EVENTS_FILE, [])

    def _save_events(self, data):
        try:
            _PROGRESS_EVENTS_FILE.write_text(
                json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
            )
        except Exception as e:
            logger.error(f"[ProgressReporter] Save events error: {e}")

    @staticmethod
    def _load_json(path: Path, default):
        try:
            if path.exists():
                return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
        return default


# ── Module-level helper for other parts of the system ─────────────────────────

def push_progress_event(message: str, event_id: Optional[str] = None):
    """
    Drop-in helper any module can call to push a WhatsApp notification.
    Does NOT require a running reporter — just writes to the event file.

    Usage:
        from core.whatsapp_progress_reporter import push_progress_event
        push_progress_event("✅ Research complete: Found 12 papers on LLMs")
    """
    import uuid
    path = _PROGRESS_EVENTS_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        events = []
        if path.exists():
            events = json.loads(path.read_text(encoding="utf-8"))
        events.append({
            "id": event_id or str(uuid.uuid4()),
            "message": message,
            "sent": False,
            "created": datetime.datetime.now().isoformat(),
        })
        path.write_text(json.dumps(events, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        logger.warning(f"[push_progress_event] Failed: {e}")
