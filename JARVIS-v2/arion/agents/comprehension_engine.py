import asyncio
import json
from core.base_agent import BaseAgent
from core.message_bus import Channel, Message

try:
    import aiohttp
except ImportError:
    aiohttp = None

class ComprehensionEngine(BaseAgent):
    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "qwen2.5-coder:7b"):
        super().__init__("ComprehensionEngine", [Channel.COMPREHENSION])
        self.ollama_url = ollama_url
        self.model = model
        self.is_paused = False
        self.circuit_broken = False
        self.last_failure_time = 0
        self.circuit_reset_timeout = 300 # 5 minutes

        # Common romanized Telugu phrases to clean English
        self.TELUGU_PHRASE_FALLBACK = {
            "enti": "what or what's up",
            "ela unnav": "how are you",
            "tinnava": "did you eat",
            "ekkada": "where",
            "eppudu": "when",
            "em chestunnav": "what are you doing",
            "peru enti": "what is the name",
            "cheppu": "tell me",
            "avunu": "yes",
            "kaadu": "no",
            "vacheyi": "come here",
            "poyyi": "go",
            "ledhu": "no or nothing",
            "teliyedu": "don't know",
            "nenu": "I or me",
            "nuvvu": "you"
        }

    async def run_loop(self):
        while self.running:
            msg = await self.get_next_message(timeout=1.0)
            if msg:
                await self.handle_message(msg)

    async def handle_message(self, message: Message):
        try:
            if message.action == "pause":
                self.is_paused = True
                print("[ComprehensionEngine] LLM calls PAUSED. Using rule-based fallback.")
            elif message.action == "resume":
                self.is_paused = False
                self.circuit_broken = False # Reset on manual resume
                print("[ComprehensionEngine] LLM calls RESUMED.")
                
            elif message.action == "build_semantic_bridge":
                # Agent 3: Semantic Bridge
                raw_text = message.payload.get("raw_text", "")
                decoded = message.payload.get("decoded_tokens", {})
                
                semantic_english = await self._build_semantic_english(raw_text, decoded)
                
                if message.requires_response:
                    await self.respond_to(message, "semantic_bridge_built", {"semantic_english": semantic_english})
        except Exception as e:
            print(f"[ComprehensionEngine] Error handling message {message.id}: {e}")
            if message.requires_response:
                # Basic fallback response to unblock the caller
                await self.respond_to(message, "semantic_bridge_built", {"semantic_english": message.payload.get("raw_text", "")})

    async def _build_semantic_english(self, raw_text: str, decoded: dict) -> str:

        """
        Agent 3: Semantic Bridge.
        Translates Romanized Dialect to clean English.
        """
        # --- Reset Circuit Breaker if timed out ---
        if self.circuit_broken and (time.time() - self.last_failure_time) > self.circuit_reset_timeout:
            self.circuit_broken = False
            print("[ComprehensionEngine] Circuit breaker reset. Attempting LLM again.")

        text_lower = raw_text.lower().strip().rstrip("?.,!")
        
        # ── Step 1: Try hardcoded phrase dictionary FIRST ─────────────────
        for phrase, meaning in self.TELUGU_PHRASE_FALLBACK.items():
            if phrase in text_lower:
                result = meaning
                if self._check_register_mismatch(raw_text, result):
                    result = result.replace("Father", "nanna").replace("Mother", "amma")
                    result = result.replace("Sister", "akka/chelli").replace("Brother", "anna")

                print(f"[ComprehensionEngine] Phrase match: '{raw_text}' -> '{result}'")
                return result
        
        # ── Step 2: Build from decoded tokens if available ────────────────
        if decoded:
            assembled = self._rule_based_fallback(raw_text, decoded)
            if assembled.lower() != raw_text.lower():
                # If we are paused or circuit is broken, return this immediately
                if self.is_paused or self.circuit_broken:
                    return assembled
        
        # ── Step 3: English Ratio Check ──────────────────────────────────
        english_words = {"hi","hello","hey","what","how","are","you","doing","bro","ok","yes","no"}
        word_set = set(text_lower.split())
        english_ratio = len(word_set & english_words) / max(len(word_set), 1)
        if english_ratio > 0.6:
            return raw_text
        
        # ── Step 4: LLM call as last resort (Bypass if paused) ───────────
        if self.is_paused or self.circuit_broken or not aiohttp:
            return self._rule_based_fallback(raw_text, decoded)

        # ... (LLM prompt building same) ...
        definitions = []
        for word, meta in decoded.items():
            meaning = meta.get("meaning", "")
            if meaning: definitions.append(f"  '{word}' = {meaning}")
        def_str = "\n".join(definitions) if definitions else "(no definitions)"

        messages = [
            {"role": "system", "content": "Translate Romanized Telugu/Hindi to English. Casual tone. Output ONLY translation."},
            {"role": "user", "content": f"Translate: \"{raw_text}\"\nKnown word meanings:\n{def_str}"}
        ]

        try:
            # LOWER TIMEOUT: 8s for faster failover
            timeout = aiohttp.ClientTimeout(total=8)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"{self.ollama_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "stream": False,
                        "options": {"temperature": 0.1, "num_predict": 50}
                    }
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        result = data.get("message", {}).get("content", "").strip()
                        
                        # Clean up meta-responses
                        if result and not any(b in result.lower() for b in ["i am", "as a", "translate"]):
                            return result
                    else:
                        raise Exception(f"Ollama status {resp.status}")
        except Exception as e:
            self.circuit_broken = True
            self.last_failure_time = time.time()
            error_type = type(e).__name__
            print(f"[ComprehensionEngine] LLM Error ({error_type}): {e}. Circuit BROKEN.")
            return self._rule_based_fallback(raw_text, decoded)

        return raw_text

    def _check_register_mismatch(self, original: str, translated: str) -> bool:
        """
        Detects if translation made casual input too formal.
        "hi nanna" → "hi Father" = register mismatch (Father too formal)
        """
        formal_indicators = ["Father", "Mother", "Brother", "Sister", "Sir", "Madam", "Greetings"]
        casual_indicators = ["hi", "hey", "haha", "bro", "ra", "da", "yaar"]
        
        original_is_casual = any(w in original.lower() for w in casual_indicators)
        translation_is_formal = any(w in translated for w in formal_indicators)
        
        return original_is_casual and translation_is_formal

    def _rule_based_fallback(self, raw_text: str, decoded: dict) -> str:
        """
        When LLM fails, assemble meaning from decoded tokens directly.
        """
        if not decoded:
            return raw_text
        
        meaning_parts = []
        words = raw_text.lower().split()
        
        for word in words:
            if word in decoded and decoded[word].get("meaning"):
                meaning_parts.append(decoded[word]["meaning"])
            else:
                meaning_parts.append(word)
        
        result = " ".join(meaning_parts).strip()
        print(f"[ComprehensionEngine] Rule fallback: '{raw_text}' → '{result}'", flush=True)
        return result if result else raw_text
