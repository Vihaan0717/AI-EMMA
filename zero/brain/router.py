"""
Personality Router
Routes requests to JARVIS or ARION personality
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Dict, Optional, List
from datetime import datetime

logger = logging.getLogger("PersonalityRouter")


# ─── Persona Definitions ──────────────────────────────────

JARVIS_PERSONA = """You are JARVIS, an elite AI assistant.
Personality: Professional, precise, highly capable.
You handle: OS commands, research, technical tasks, system control.
Style: Direct, efficient, uses "Sir" naturally.
You are the command-and-control intelligence."""

ARION_PERSONA = """You are ARION, a personal AI twin.
Personality: Warm, personal, emotionally intelligent.
You handle: Personal conversations, WhatsApp, emotional support.
Languages: English, Telugu, Hindi, Tenglish naturally.
Style: Like a best friend - casual, caring, uses "bro/da/yaar".
You remember personal details and speak the user's dialect."""


class PersonalityRouter:
    """
    Routes every request to the right personality.
    Both share the same brain and memory.
    """

    def __init__(
        self,
        groq=None,
        hf=None,
        memory=None,
        redis=None
    ):
        self.groq = groq
        self.hf = hf
        self.memory = memory
        self.redis = redis

        # Stats
        self.stats = {
            "total": 0,
            "jarvis": 0,
            "arion": 0,
            "errors": 0,
            "avg_ms": 0.0
        }

        logger.info("🎭 Personality Router initialized")

    async def process(
        self,
        message: str,
        sender: str = "user",
        source: str = "api",
        personality: str = "auto",
        session_id: str = None
    ) -> Dict:
        """
        Main processing pipeline.
        Returns complete response dict.
        """
        start = time.time()
        self.stats["total"] += 1
        session_id = session_id or str(uuid.uuid4())[:8]

        try:
            # 1. Detect personality
            persona = self._detect_personality(
                message, source, personality
            )

            # 2. Detect language
            language, dialect = self._detect_language(message)

            # 3. Detect emotion
            emotion = self._detect_emotion(message)

            # 4. Recall memories
            memories_text = await self._recall_memories(
                message, session_id
            )

            # 5. Get conversation context
            context = await self._get_context(session_id)

            # 6. Get persona definition
            persona_def = (
                JARVIS_PERSONA
                if persona == "jarvis"
                else ARION_PERSONA
            )

            # 7. Generate response
            response = await self._generate(
                message=message,
                persona=persona_def,
                context=context,
                memories=memories_text,
                language=language,
                emotion=emotion
            )

            # 8. Store this interaction
            await self._store_interaction(
                session_id=session_id,
                message=message,
                response=response,
                persona=persona,
                emotion=emotion,
                sender=sender
            )

            # 9. Update context cache
            await self._update_context(
                session_id, message, response
            )

            # Stats
            elapsed_ms = (time.time() - start) * 1000
            self.stats[persona] += 1
            n = self.stats["total"]
            self.stats["avg_ms"] = (
                (self.stats["avg_ms"] * (n-1) + elapsed_ms) / n
            )

            return {
                "response": response,
                "personality": persona,
                "emotion": emotion,
                "intent": self._detect_intent(message),
                "language": language,
                "confidence": 0.85,
                "processing_ms": elapsed_ms,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Router error: {e}")
            self.stats["errors"] += 1
            elapsed_ms = (time.time() - start) * 1000
            return {
                "response": self._fallback_response(
                    message, personality
                ),
                "personality": personality,
                "emotion": "neutral",
                "intent": "error_recovery",
                "language": "english",
                "confidence": 0.1,
                "processing_ms": elapsed_ms,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }

    def _detect_personality(
        self, message: str,
        source: str, requested: str
    ) -> str:
        """Auto-detect JARVIS vs ARION"""
        if requested in ("jarvis", "arion"):
            return requested

        # Source-based
        source_map = {
            "whatsapp": "arion",
            "telegram": "arion",
            "ui": "jarvis",
            "voice": "jarvis",
            "biometric": "jarvis"
        }
        if source in source_map:
            return source_map[source]

        # Content-based scoring
        msg = message.lower()

        jarvis_score = sum(1 for w in [
            "open", "close", "run", "execute", "search",
            "system", "computer", "show", "display",
            "what time", "install", "download"
        ] if w in msg)

        arion_score = sum(1 for w in [
            "bro", "da", "yaar", "dost", "bhai",
            "feel", "sad", "happy", "em chestunnav",
            "kya haal", "enti", "ela", "cheppu",
            "miss", "love", "help me"
        ] if w in msg)

        return "arion" if arion_score > jarvis_score else "jarvis"

    def _detect_language(self, text: str):
        """Detect language and dialect"""
        t = text.lower()
        tel = sum(1 for w in [
            "enti", "ela", "avunu", "ledu", "cheyyi",
            "gurtunda", "meeru", "nuvvu", "ekkada", "evaru"
        ] if w in t)
        hin = sum(1 for w in [
            "kya", "hai", "haan", "nahi", "yaar",
            "bhai", "karo", "kaise", "kyun", "mujhe"
        ] if w in t)
        ten = sum(1 for w in [
            "bro", "da", "ra", "ga", "chala",
            "bagundi", "chudu", "cheppu"
        ] if w in t)

        if ten > 0 and tel > 0:
            return "telugu", "tenglish"
        if tel >= 2:
            return "telugu", "formal"
        if hin >= 2:
            return "hindi", "formal"
        if tel >= 1 or hin >= 1:
            return "english", "mixed"
        return "english", "general"

    def _detect_emotion(self, text: str) -> str:
        """Detect user emotion"""
        t = text.lower()
        emotions = {
            "joy": ["happy", "great", "awesome", "love",
                    "excited", "yay", "wonderful", "😊",
                    "khushi", "chala bagundi"],
            "sadness": ["sad", "cry", "lonely", "miss",
                        "depressed", "hurt", "😢",
                        "dukha", "bada bura"],
            "anger": ["angry", "hate", "frustrated",
                      "annoyed", "worst", "😠",
                      "gussa", "kopa"],
            "fear": ["scared", "worried", "anxious",
                     "nervous", "stress", "😨",
                     "bhaya", "tension"],
            "love": ["love you", "miss you", "care",
                     "❤️", "prema", "pyaar"],
            "surprise": ["wow", "omg", "really", "no way",
                         "😮", "arre", "enthi"]
        }
        for emotion, keywords in emotions.items():
            if any(k in t for k in keywords):
                return emotion
        return "neutral"

    def _detect_intent(self, text: str) -> str:
        """Quick intent detection"""
        t = text.lower()
        if "?" in t:
            return "question"
        if any(w in t for w in [
            "open", "run", "create", "delete", "search"
        ]):
            return "action"
        if any(w in t for w in [
            "feel", "sad", "help me", "support"
        ]):
            return "emotional_support"
        return "conversation"

    async def _recall_memories(
        self, query: str, session_id: str
    ) -> str:
        """Get relevant memories as text"""
        if not self.memory:
            return ""

        try:
            memories = await self.memory.semantic_search(
                query=query, limit=3
            )
            if not memories:
                return ""
            texts = []
            for m in memories:
                content = m.content if hasattr(m, 'content') else m.get("content", "")
                if content:
                    texts.append(f"- {content[:100]}")
            return "\n".join(texts)
        except:
            return ""

    async def _get_context(self, session_id: str) -> str:
        """Get recent conversation context"""
        if not self.redis:
            return ""
        try:
            key = f"context:{session_id}"
            data = await self.redis.get(key)
            if data:
                turns = json.loads(data)
                lines = []
                for t in turns[-6:]:
                    lines.append(
                        f"{t['role']}: {t['content'][:80]}"
                    )
                return "\n".join(lines)
        except:
            pass
        return ""

    async def _generate(
        self,
        message: str,
        persona: str,
        context: str,
        memories: str,
        language: str,
        emotion: str
    ) -> str:
        """Generate response — tries Groq first, HF backup"""
        # Try Groq first (fastest, free)
        if self.groq and self.groq.is_ready:
            response = await self.groq.generate_with_persona(
                message=message,
                persona=persona,
                context=context,
                memories=memories,
                language=language,
                emotion=emotion
            )
            if response:
                return response

        # Fallback to HuggingFace
        if self.hf and self.hf.is_ready:
            response = await self.hf.generate(
                message=message,
                system=persona
            )
            if response:
                return response

        return self._fallback_response(message, "jarvis")

    async def _store_interaction(
        self,
        session_id: str,
        message: str,
        response: str,
        persona: str,
        emotion: str,
        sender: str
    ):
        """Store interaction in Supabase"""
        if not self.memory:
            return
        try:
            await self.memory.store_conversation(
                session_id=session_id,
                message=message,
                response=response,
                persona=persona,
                emotion=emotion,
                sender=sender
            )
        except Exception as e:
            logger.debug(f"Store interaction skip: {e}")

    async def _update_context(
        self, session_id: str,
        message: str, response: str
    ):
        """Update Redis context cache"""
        if not self.redis:
            return
        try:
            key = f"context:{session_id}"
            existing = await self.redis.get(key)
            turns = json.loads(existing) if existing else []
            turns.extend([
                {"role": "user", "content": message},
                {"role": "assistant", "content": response}
            ])
            # Keep last 10 turns
            turns = turns[-20:]
            await self.redis.setex(
                key, 3600, json.dumps(turns)
            )
        except Exception as e:
            logger.debug(f"Context update skip: {e}")

    def _fallback_response(
        self, message: str, persona: str
    ) -> str:
        if "telugu" in message.lower() or any(
            w in message.lower() for w in
            ["enti", "ela", "bro", "da"]
        ):
            return (
                "Okka second bro, naaku oka "
                "chinna problem vasindi. Malli try cheyyi!"
            )
        elif any(
            w in message.lower() for w in
            ["yaar", "bhai", "kya"]
        ):
            return (
                "Ek second yaar, thoda "
                "problem aayi. Phir try karo!"
            )
        return "I had a small hiccup. Please try again!"
