"""
arion/agents/reflection_engine.py
=====================================
ARION 3.0 — Reflection Engine (A8 — fire-and-forget)

Triggered AFTER every response is sent.
Does NOT block the pipeline — runs as an async task.

What it does on every trigger:
  1. Stores the exchange in CausalMemoryGraph
  2. Infers implicit outcome by comparing incoming vs. outgoing emotion intensity
  3. On high-emotion events OR every 10th message → writes a reflection note
     to the Obsidian vault at Brain/Patterns/

Over time, this creates a living log of:
  "X was emotional → ARION said Y → X became calmer (worked)"
  "X was anxious → ARION said Z → X got more anxious (failed)"
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

from core.base_agent import BaseAgent
from core.message_bus import Channel, Message

logger = logging.getLogger(__name__)


class ReflectionEngine(BaseAgent):
    """
    A8 — Post-response learner and pattern writer.

    Payload expected:
      contact           str   — WhatsApp JID or Telegram ID
      user_text         str   — the message ARION received
      arion_reply       str   — the reply ARION sent
      emotion           str   — detected emotion
      emotion_intensity float
      hidden_need       str   — from DeepLanguageEngine
      topic             str
      response_style    str
      prev_intensity    float — emotion intensity of PREVIOUS message (used for outcome inference)
      timestamp         float
    """

    # Reflection note written to vault every N messages or on high-emotion
    NOTE_INTERVAL       = 10
    HIGH_EMOTION_THRESH = 0.65

    def __init__(self, config: Dict):
        super().__init__("ReflectionEngine", [Channel.REFLECTION])
        self.vault_path  = Path(config.get("vault_path", "data/obsidian_vault"))
        self.patterns_dir = self.vault_path / "Brain" / "Patterns"
        self.patterns_dir.mkdir(parents=True, exist_ok=True)

        # Lazy import — CausalMemoryGraph may not be ready at import time
        self._causal: Optional[object] = None
        self._causal_path = config.get("db_paths", {}).get(
            "causal_memory", "arion/data/causal_memory.db"
        )

        self._msg_counter: Dict[str, int] = {}   # per-person counter
        self._prev_intensity: Dict[str, float] = {}  # track emotion delta

    def _get_causal(self):
        if self._causal is None:
            try:
                from brain.causal_memory_graph import CausalMemoryGraph
                self._causal = CausalMemoryGraph(self._causal_path)
            except Exception as e:
                logger.warning(f"[ReflectionEngine] CausalMemoryGraph unavailable: {e}")
        return self._causal

    async def run_loop(self):
        while self.running:
            msg = await self.get_next_message(timeout=1.0)
            if msg:
                await self.handle_message(msg)

    async def handle_message(self, message: Message):
        if message.action == "post_response_learn":
            # Run in executor so SQLite writes don't block the event loop
            await asyncio.get_event_loop().run_in_executor(
                None, self._learn, message.payload
            )

    # ── Core learning (sync, runs in thread executor) ─────────────────────────

    def _learn(self, payload: Dict):
        contact         = payload.get("contact", "unknown")
        user_text       = payload.get("user_text", "")
        arion_reply     = payload.get("arion_reply", "")
        emotion         = payload.get("emotion", "neutral")
        emotion_intensity = float(payload.get("emotion_intensity", 0.3))
        hidden_need     = payload.get("hidden_need", "unknown")
        topic           = payload.get("topic", "general")
        response_style  = payload.get("response_style", "natural")

        # ── 1. Infer implicit outcome from emotion trajectory ─────────────
        prev = self._prev_intensity.get(contact, emotion_intensity)
        if emotion_intensity < prev - 0.1:
            outcome = "positive"
        elif emotion_intensity > prev + 0.1:
            outcome = "negative"
        else:
            outcome = "neutral"
        self._prev_intensity[contact] = emotion_intensity

        # ── 2. Record in causal graph ─────────────────────────────────────
        causal = self._get_causal()
        if causal:
            try:
                causal.record_exchange(
                    person=contact,
                    user_message=user_text,
                    arion_reply=arion_reply,
                    emotion=emotion,
                    emotion_intensity=emotion_intensity,
                    topic=topic,
                    response_style=response_style,
                )
                # Update the PREVIOUS exchange outcome using current emotion direction
                causal.update_exchange_outcome(contact, outcome)
                if outcome == "negative":
                    causal.record_negative_outcome(contact)
                logger.debug(f"[ReflectionEngine] Exchange recorded: {outcome} for {contact}")
            except Exception as e:
                logger.warning(f"[ReflectionEngine] CausalGraph write failed: {e}")

        # ── 3. Increment counter, decide if we should write a vault note ───
        cnt = self._msg_counter.get(contact, 0) + 1
        self._msg_counter[contact] = cnt

        should_write = (
            emotion_intensity >= self.HIGH_EMOTION_THRESH
            or cnt % self.NOTE_INTERVAL == 0
        )
        if should_write:
            self._write_vault_note(
                contact=contact,
                user_text=user_text,
                arion_reply=arion_reply,
                emotion=emotion,
                emotion_intensity=emotion_intensity,
                hidden_need=hidden_need,
                topic=topic,
                outcome=outcome,
            )

    def _write_vault_note(self, contact: str, user_text: str,
                           arion_reply: str, emotion: str,
                           emotion_intensity: float, hidden_need: str,
                           topic: str, outcome: str):
        """
        Write a Markdown reflection note to Brain/Patterns/.
        These accumulate into a searchable log of what works.
        """
        now        = datetime.now()
        date_str   = now.strftime("%Y-%m-%d")
        time_str   = now.strftime("%H:%M")
        contact_id = contact.split("@")[0]
        fname      = f"Reflection_{contact_id}_{date_str}_{now.strftime('%H%M%S')}.md"
        fpath      = self.patterns_dir / fname

        outcome_icon = {"positive": "✅", "negative": "❌", "neutral": "➖"}.get(outcome, "❓")

        content = f"""---
date: {date_str}
time: {time_str}
person: {contact_id}
emotion: {emotion}
intensity: {emotion_intensity:.2f}
topic: {topic}
outcome: {outcome}
tags: [reflection, {emotion}, {topic}]
---

# Reflection — {contact_id} — {date_str} {time_str}

**Emotion detected:** {emotion} (intensity: {emotion_intensity:.1%})
**Hidden need:** {hidden_need}
**Topic:** {topic}
**Outcome of ARION's reply:** {outcome_icon} {outcome}

## What they said
> {user_text[:300] if user_text else '(no text)'}

## What ARION replied
> {arion_reply[:300] if arion_reply else '(no reply)'}

## What this means
{"Their emotion level DROPPED after ARION's reply → approach WORKED ✅" if outcome == "positive" else
 "Their emotion level ROSE after ARION's reply → approach may have FAILED ❌" if outcome == "negative" else
 "Emotion stayed stable → neutral outcome ➖"}

{"⚠️ HIGH EMOTION EVENT — ARION must file this pattern carefully." if emotion_intensity >= 0.7 else ""}

---
*Auto-generated by ReflectionEngine — ARION 3.0*
"""
        try:
            fpath.write_text(content, encoding="utf-8")
            logger.info(f"[ReflectionEngine] Wrote note → {fpath.name}")
        except Exception as e:
            logger.error(f"[ReflectionEngine] Vault write failed: {e}")
