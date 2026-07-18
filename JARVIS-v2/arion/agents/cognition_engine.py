"""
arion/agents/cognition_engine.py
===================================
ARION 3.0 — Cognition Engine (A5 of owner pipeline)

The prefrontal cortex. Given all gathered context, decides:
  - What kind of response is needed (reply / comfort / deflect / ask / celebrate)
  - Whether this is a good moment to ask a curiosity question
  - Whether a causal-memory insight should be surfaced
  - Reasoning notes (logged internally, NOT sent to user)

Primary: rule-based (fast, reliable).
Optional: brief Ollama call for genuinely ambiguous situations (≤30 tokens).
Fallbacks instantly if Ollama times out.
"""

import asyncio
import json
import logging
from typing import Dict, Optional

from core.base_agent import BaseAgent
from core.message_bus import Channel, Message

try:
    import aiohttp
except ImportError:
    aiohttp = None

logger = logging.getLogger(__name__)


class CognitionEngine(BaseAgent):
    """
    A5 — Decides what ARION should DO, not just what it should SAY.

    Inputs  (via message.payload):
      semantic_text       str
      emotion             str
      emotion_intensity   float
      intent              dict   (from IntentEngine)
      brain_context       str    (from RAGEngine)
      causal_context      str    (from CausalMemoryGraph)
      conversation_length int
      deep_analysis       dict   (MessageAnalysis.to_dict())

    Outputs (response payload):
      recommended_action  str    reply | comfort | deflect | ask | celebrate
      curiosity_question  str    optional question to weave in
      insight             str    causal pattern insight to mention
      reasoning_notes     str    internal log — NOT injected into user reply
      should_use_ollama   bool   debugging flag
    """

    # Curiosity question banks by hidden_need
    CURIOSITY_BANK: Dict[str, list] = {
        "attentive response":            [],
        "grounding and calm presence":   [],  # Don't ask when grounding
        "emotional validation":          [],  # Don't ask when validating
        "clear, simple, honest answer":  ["which part feels unclear?"],
        "matching energy and engagement": ["what happened next?", "who else was there?"],
        "connection and full attention":  ["what's been on your mind lately?"],
        "space and no pressure":         [],  # Don't ask when giving space
    }

    # How often to potentially ask (every N owner messages)
    CURIOSITY_INTERVAL = 8

    def __init__(self, ollama_url: str = "http://localhost:11434",
                 model: str = "gemma3:1b"):
        super().__init__("CognitionEngine", [Channel.COGNITION])
        self.ollama_url = ollama_url
        self.model      = model            # Fast small model only
        self._msg_count = 0

    async def run_loop(self):
        while self.running:
            msg = await self.get_next_message(timeout=1.0)
            if msg:
                await self.handle_message(msg)

    async def handle_message(self, message: Message):
        if message.action == "reason_and_plan":
            result = await self._reason(message.payload)
            if message.requires_response:
                await self.respond_to(message, "cognition_result", result)

    # ── Core reasoning ────────────────────────────────────────────────────────

    async def _reason(self, payload: Dict) -> Dict:
        self._msg_count += 1

        emotion           = payload.get("emotion", "neutral")
        emotion_intensity = float(payload.get("emotion_intensity", 0.3))
        intent_info       = payload.get("intent", {})
        conv_length       = int(payload.get("conversation_length", 0))
        causal_ctx        = payload.get("causal_context", "")
        semantic_text     = payload.get("semantic_text", "")
        deep              = payload.get("deep_analysis", {})

        hidden_need       = deep.get("hidden_need", "attentive response")
        trajectory        = deep.get("emotion_trajectory", "stable")
        never_sarcastic   = deep.get("never_sarcastic", False)
        high_care         = deep.get("high_care_mode", False)
        intent_type       = intent_info.get("intent", "general")

        notes: list = []
        action        = "reply"
        curiosity_q   = ""
        insight       = ""

        # ── Rule 1: High distress → comfort first ─────────────────────────
        if (high_care or emotion in ("sadness", "anxiety", "distress", "grief")
                or emotion_intensity > 0.75):
            action = "comfort"
            notes.append(f"High emotion ({emotion}, {emotion_intensity:.1f}) → comfort mode")

        # ── Rule 2: Celebration triggers ──────────────────────────────────
        elif emotion in ("excitement", "joy") and emotion_intensity > 0.65:
            action = "celebrate"
            notes.append("Excitement detected → match energy")

        # ── Rule 3: Genuine question → direct answer ───────────────────────
        elif intent_type in ("question", "help_request", "clarification"):
            action = "reply"
            notes.append(f"Intent {intent_type} → direct reply")

        # ── Rule 4: Emotionally volatile → gentle grounding ───────────────
        elif trajectory == "emotionally_volatile":
            action = "comfort"
            notes.append("Volatile trajectory → grounding reply needed")

        # ── Rule 5: Deflect only on privacy hit (handled by PrivacyShield) ─
        # (We don't decide deflection here — PrivacyShield owns that)

        # ── Causal context → surface insight ──────────────────────────────
        if causal_ctx and len(causal_ctx) > 40:
            # Extract first useful line
            first_line = causal_ctx.strip().split("\n")[0]
            if "[CAUSAL]" in first_line or "[PATTERN]" in first_line:
                insight = first_line.replace("[CAUSAL]", "").replace("[PATTERN]", "").strip()
                notes.append("Causal pattern available for context")

        # ── Curiosity question — gated, infrequent, emotion-safe ──────────
        if (action not in ("comfort", "deflect")
                and not high_care
                and not never_sarcastic   # tone flag reused as "delicate mode"
                and emotion_intensity < 0.55
                and trajectory == "stable"
                and self._msg_count % self.CURIOSITY_INTERVAL == 0
                and conv_length >= 3):
            bank = self.CURIOSITY_BANK.get(hidden_need, [])
            if bank:
                curiosity_q = bank[self._msg_count // self.CURIOSITY_INTERVAL % len(bank)]
                notes.append(f"Curiosity window open → will offer: '{curiosity_q}'")

        # ── Optional Ollama call for genuinely ambiguous edge cases ───────
        if self._is_ambiguous(emotion, trajectory, intent_type, deep):
            ollama_hint = await self._quick_ollama_reason(semantic_text, emotion, hidden_need)
            if ollama_hint:
                notes.append(f"Ollama hint: {ollama_hint}")
                # Override action only if Ollama is very confident
                if "comfort" in ollama_hint.lower():
                    action = "comfort"
                elif "celebrate" in ollama_hint.lower():
                    action = "celebrate"

        return {
            "recommended_action": action,
            "curiosity_question": curiosity_q,
            "insight":            insight,
            "reasoning_notes":    " | ".join(notes),
            "should_use_ollama":  False,
        }

    def _is_ambiguous(self, emotion: str, trajectory: str,
                      intent_type: str, deep: Dict) -> bool:
        """
        Only call Ollama when rule-based reasoning is genuinely uncertain.
        Keeps it rare — max 1 in 20 messages.
        """
        if emotion == "neutral" and trajectory == "stable":
            return False
        # Mixed signals: positive emotion but heavy code-switching
        if (emotion in ("joy", "excitement") and
                len(deep.get("code_switches", [])) >= 2):
            return True
        # Subtext detected with normal emotion
        subtext = deep.get("subtext", "none detected")
        if subtext not in ("none detected", "") and emotion == "neutral":
            return True
        return False

    async def _quick_ollama_reason(self, text: str, emotion: str,
                                    hidden_need: str) -> Optional[str]:
        """
        Ultra-short Ollama call (max 25 tokens).
        Only for ambiguous cases. Returns one of:
        "reply" | "comfort" | "celebrate" | "ask"
        """
        if not aiohttp:
            return None
        try:
            prompt = (
                f"Message: \"{text[:100]}\"\n"
                f"Detected emotion: {emotion}\n"
                f"Hidden need: {hidden_need}\n"
                f"What is the ideal response type? Answer with ONE word: "
                f"reply, comfort, celebrate, or ask."
            )
            timeout = aiohttp.ClientTimeout(total=4)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"{self.ollama_url}/api/generate",
                    json={"model": self.model, "prompt": prompt,
                          "stream": False, "options": {"num_predict": 10}}
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("response", "").strip().lower()
        except Exception as e:
            logger.debug(f"[CognitionEngine] Ollama hint failed (OK): {e}")
        return None
