"""
Orchestrator — The central brain of ARION.

Features:
  - Emotion detector (Signals like haha, wtf, etc.)
  - Person Context Integration (Fetches relationship/style before replying)
  - Style Mirroring & Social Adaptation
  - Manual slang learning & Owner feedback
"""

import asyncio
import json
import re
import time
import uuid
from typing import Dict, Any, Optional, List

from core.message_bus import Channel, Message, Priority, MessageBus
from core.base_agent import BaseAgent

try:
    import aiohttp
except ImportError:
    aiohttp = None

from agents.privacy_shield import PrivacyShield
from agents.curiosity_engine import CuriosityEngine
from agents.connection_insight_engine import ConnectionInsightEngine
from brain.rag_engine import RAGEngine
from brain.reinforcement_engine import ReinforcementEngine

# ── ARION 3.0 cognitive imports ─────────────────────────────────────────────
try:
    from agents.deep_language_engine import DeepLanguageCore
except Exception as _dle_err:
    DeepLanguageCore = None  # type: ignore
    print(f"[Orchestrator] DeepLanguageCore unavailable: {_dle_err}")

try:
    from brain.causal_memory_graph import CausalMemoryGraph
except Exception as _cmg_err:
    CausalMemoryGraph = None  # type: ignore
    print(f"[Orchestrator] CausalMemoryGraph unavailable: {_cmg_err}")


# ── Emotion detector (lightweight, no external deps) ─────────────────────────
_EMOTION_MAP = {
    "happy":     ["😊","haha","lol","lmao","😂","great","love","baagundi","kiraak","bindaas"],
    "frustrated":["ugh","wtf","annoying","pissed","frustrated","chutiya","baigan","naaku"],
    "sad":       ["😢","miss","lonely","sad","hurt","pain","bore"],
    "excited":   ["wow","omg","yesss","🎉","finally","can't wait","🔥","fire","super"],
    "sarcastic": ["sure","obviously","great job","etakaaram","pushpam","brilliant"],
}

def _detect_emotion(text: str) -> str:
    tl = text.lower()
    for emotion, signals in _EMOTION_MAP.items():
        if any(s in tl for s in signals):
            return emotion
    return ""


class Orchestrator(BaseAgent):
    def __init__(self, config: dict):
        super().__init__("Orchestrator", [Channel.ORCHESTRATOR])
        self.ollama_url   = config.get("ollama_url", "http://localhost:11434")
        self.model        = config.get("model_name", "llama3")
        self.max_history  = config.get("max_memory_history", 20)
        self.proxy_file   = self._resolve_path("data/proxy_list.json")

        self.conversations: Dict[str, List[Dict[str, str]]] = {}
        self.active_proxy_list: Dict[str, dict] = {}
        self._load_proxy_list()

        self.persona  = self._load_json("config/persona_core.json")
        self.identity = self._load_json("config/owner_identity.json")
        self.cip      = self._load_json("config/cultural_intelligence.json")

        # ── LINGUISTIC INTELLIGENCE LAYER ──
        self.vocab_te = self._load_json("config/vocabulary_telugu.json")
        self.vocab_hi = self._load_json("config/vocabulary_hindi.json")
        self.conv_examples = self._load_json_list("config/conversation_examples.json")
        self._te_all_words = self._build_word_index(self.vocab_te)
        self._hi_all_words = self._build_word_index(self.vocab_hi)
        print(f"[Orchestrator] Loaded {len(self._te_all_words)} Telugu + {len(self._hi_all_words)} Hindi vocabulary words.", flush=True)

        # ── Specialized Engines ──────────────────────────────────────────────
        try:
            self.privacy_shield = PrivacyShield()
            print("[Orchestrator] Privacy Shield calibrated.", flush=True)
        except Exception as e:
            print(f"[Orchestrator] ERROR calibrating Privacy Shield: {e}", flush=True)
            self.privacy_shield = None

        # ── NEW: Brain Architecture mapping (Hippocampus & Cortex) ──────
        try:
            self.rag_engine = RAGEngine(
                chroma_path=self._resolve_path(config.get("db_paths", {}).get("chroma", "arion/data/chromadb"))
            )
            self.reinforcement_engine = ReinforcementEngine()
            print("[Orchestrator] Brain Architecture mapping active.", flush=True)
        except Exception as e:
            print(f"[Orchestrator] Brain Init Error: {e}", flush=True)
            self.rag_engine = None
            self.reinforcement_engine = None

        self.curiosity_engine = CuriosityEngine()
        self.OWNER_JID = "919154716156@c.us"

        self.connection_insight_engine = ConnectionInsightEngine()

        # ── ARION 3.0: Deep Language Core (inline — no bus round-trip) ────
        self.deep_lang: Optional[object] = None
        if DeepLanguageCore:
            try:
                cfg_dir = self._resolve_path("config")
                db_path = self._resolve_path("arion/data/pragmatics.db")
                if not __import__('os').path.isdir(cfg_dir):
                    cfg_dir = "arion/config"
                self.deep_lang = DeepLanguageCore(
                    config_dir=cfg_dir,
                    db_path=db_path,
                )
                print("[Orchestrator] Deep Language Core initialized. ✓", flush=True)
            except Exception as _e:
                print(f"[Orchestrator] DeepLanguageCore init failed: {_e}", flush=True)

        # ── ARION 3.0: Causal Memory Graph (inline SQLite) ─────────────────
        self.causal_graph: Optional[object] = None
        if CausalMemoryGraph:
            try:
                causal_db = self._resolve_path("arion/data/causal_memory.db")
                self.causal_graph = CausalMemoryGraph(causal_db)
                print("[Orchestrator] Causal Memory Graph initialized. ✓", flush=True)
            except Exception as _e:
                print(f"[Orchestrator] CausalMemoryGraph init failed: {_e}", flush=True)

        self._response_counter: int = 0   # triggers reflection every N turns

    def _resolve_path(self, path: str) -> str:
        """Try path as-is, then with arion/ prefix."""
        import os
        if os.path.exists(path): return path
        alt = f"arion/{path}"
        if os.path.exists(alt): return alt
        return path

    def _load_json(self, path: str) -> dict:
        import os
        candidates = [path, f"arion/{path}"]
        for p in candidates:
            if os.path.exists(p):
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        return json.load(f)
                except Exception:
                    pass
        return {}

    def _load_json_list(self, path: str) -> list:
        import os
        candidates = [path, f"arion/{path}"]
        for p in candidates:
            if os.path.exists(p):
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        return json.load(f)
                except Exception:
                    pass
        return []

    def _build_word_index(self, vocab: dict) -> dict:
        """Flatten nested vocabulary into {word: meaning} for fast lookup."""
        index = {}
        for category, entries in vocab.items():
            if category == "meta":
                continue
            if isinstance(entries, dict):
                for word, meaning in entries.items():
                    index[word.lower()] = meaning
        return index

    def _detect_dialect(self, text: str) -> str:
        """Detect dialect using the FULL vocabulary word lists."""
        tl = text.lower()
        words = set(re.split(r'[\s,?.!]+', tl))

        te_hits = sum(1 for w in words if w in self._te_all_words)
        hi_hits = sum(1 for w in words if w in self._hi_all_words)

        # Also check multi-word phrases
        for phrase in self._te_all_words:
            if ' ' in phrase and phrase in tl:
                te_hits += 2
        for phrase in self._hi_all_words:
            if ' ' in phrase and phrase in tl:
                hi_hits += 2

        if te_hits > hi_hits and te_hits >= 1:
            return "telugu"
        elif hi_hits > te_hits and hi_hits >= 1:
            return "hindi"
        return "general"

    def _get_vocab_context(self, text: str, dialect: str) -> str:
        """Find relevant vocabulary entries + example conversations for prompt injection."""
        tl = text.lower()
        parts = []

        vocab = self._te_all_words if dialect == "telugu" else self._hi_all_words if dialect == "hindi" else {}

        # 1. Find words from the user's message that match our vocabulary
        matched = []
        for word, meaning in vocab.items():
            if word in tl:
                matched.append(f"{word} = {meaning}")
        if matched:
            parts.append("DETECTED WORDS: " + " | ".join(matched[:15]))

        # 2. Provide relevant response vocabulary (greetings, slang, sarcasm)
        source = self.vocab_te if dialect == "telugu" else self.vocab_hi if dialect == "hindi" else {}
        useful_cats = ["greetings", "joy_slang", "joy_vibes", "yatakaram_sarcasm", "sarcastic_comebacks", "daily_actions", "fillers_connectors", "feelings_moods"]
        response_words = []
        for cat in useful_cats:
            entries = source.get(cat, {})
            if isinstance(entries, dict):
                for w, m in list(entries.items())[:5]:
                    response_words.append(f"{w} ({m})")
        if response_words:
            parts.append("SLANG DICTIONARY (Use these naturally if they fit, do not force them): " + " | ".join(response_words[:20]))

        # 3. Find matching conversation examples
        examples = [ex for ex in self.conv_examples
                    if ex.get("lang") == dialect]
        if examples:
            # Pick up to 2 relevant examples
            best = examples[:2]
            for ex in best:
                parts.append(f"EXAMPLE - User: \"{ex['user']}\" -> Reply: \"{ex['reply']}\"")

        return "\n".join(parts) if parts else ""

    def _load_proxy_list(self):
        try:
            with open(self.proxy_file, "r", encoding="utf-8") as f:
                self.active_proxy_list = json.load(f)
        except Exception:
            self.active_proxy_list = {}

    def _save_proxy_list(self):
        try:
            with open(self.proxy_file, "w", encoding="utf-8") as f:
                json.dump(self.active_proxy_list, f, indent=2)
        except:
            pass

    # ── Main loop ────────────────────────────────────────────────────────────

    async def run_loop(self):
        while self.running:
            msg = await self.get_next_message(timeout=0.5)
            if msg:
                try:
                    await asyncio.wait_for(self.handle_message(msg), timeout=120.0)
                except asyncio.TimeoutError:
                    print(f"[Orchestrator] Recovery (timeout after 120s).")
                except Exception as e:
                    import traceback
                    print(f"[Orchestrator] Error: {e}\n{traceback.format_exc()}")

    async def handle_message(self, message: Message):
        if message.action == "process_input":
            await self._process_input(message)

    # ── Core pipeline ────────────────────────────────────────────────────────

    async def _process_input(self, msg: Message):
        payload  = msg.payload
        text     = payload.get("text", "").strip()
        contact  = payload.get("contact") or payload.get("from", "unknown")
        source   = payload.get("source", "whatsapp")
        is_owner = payload.get("is_owner", False) or payload.get("isOwner", False)
        is_group = payload.get("isGroup") == "true" or payload.get("isGroup") is True
        jid      = payload.get("jid", "")

        print(f"[Orchestrator] Message Received: [{source}] {contact} | owner={is_owner} | len={len(text)}", flush=True)

        if is_group or not text:
            return

        # 1. Nuclear slang shield (no memory written for these)
        shadow_reply = await self._check_nuclear_slang_shield(text)
        if shadow_reply:
            await self._send_response(source, contact, shadow_reply, payload)
            return

        # 2. Owner feedback shortcut: "feedback: tone was too formal"
        if is_owner and text.lower().startswith("feedback:"):
            await self._handle_owner_feedback(text, contact, source, payload)
            return

        # 3. Slang learning
        if is_owner and text.lower().startswith("learn slang"):
            await self._handle_manual_learning(text)
            return

        # 4. Knowledge Ingestion: "learn Interstellar"
        if is_owner and text.lower().startswith("learn"):
            await self._handle_learn_command(text, contact, source, payload)
            return

        # 5. Proactive Knowledge Detection: If long content (>1000 chars), ask to ingest
        if is_owner and len(text) > 1000:
            await self._send_response(source, contact, "Ra, check this out. It's a big block of text. Should I ingest this into my knowledge vault? (Reply with 'learn' to do it)", payload)
            # We don't return here, we still process it as a conversation turn so ARION sees it.

        print(f"[Orchestrator] [{source}] {contact} (owner={is_owner}): {text}")

        if source == "whatsapp" and not is_owner:
            await self._process_proxy_reply(text, contact, source, jid, payload)
        else:
            await self._process_owner_message(text, contact, source, payload)

    async def _check_nuclear_slang_shield(self, text: str) -> Optional[str]:
        text_lower = text.lower()
        burns = {
            "puka":     "Enna ra? Puka! 😂 Poyyi pani chusko.",
            "dengey":   "Nuvve dengei ra pichoda. 👍",
            "modda":    "Modda! Ne bondha ra. 😂",
            "chutiya":  "Haule! Chutiyapan bandh kar. ✋",
            "nee amma": "Ne abba ni adugu. 😂"
        }
        for key, reply in burns.items():
            if key in text_lower:
                return reply
        return None

    async def _handle_owner_feedback(self, text: str, contact: str, source: str, payload: dict):
        """Routes owner feedback to MemoryManager's procedural layer."""
        feedback_text = text[len("feedback:"):].strip()
        if not feedback_text:
            return
        await self.send(
            to_channel=Channel.MEMORY,
            action="store_feedback",
            payload={
                "contact":   contact,
                "feedback":  feedback_text,
                "context":   "",
                "timestamp": time.time(),
            }
        )
        await self._send_response(source, contact, "✅ Noted. I'll adjust.", payload)

    async def _handle_manual_learning(self, text: str):
        match = re.search(r"word\s+(.+?)\s+means\s+(.+)", text, re.IGNORECASE)
        if match:
            word    = match.group(1).strip()
            meaning = match.group(2).strip()
            await self.send(
                to_channel=Channel.MEMORY,
                action="learn_slang",
                payload={"word": word, "meaning": meaning}
            )
            await self.send(
                to_channel=Channel.WHATSAPP,
                action="send_whatsapp",
                payload={"target": "919154716156@c.us", "text": f"✅ Indexed: {word}."}
            )

    # ── Routing ──────────────────────────────────────────────────────────────

    async def _process_owner_message(self, text: str, contact: str, source: str, payload: dict):
        # ── A0: Deep Language Analysis (ARION 3.0) ────────────────────────
        deep_analysis = None
        if self.deep_lang:
            try:
                conv_ctx = {
                    "relationship": "owner",
                    "topic":        None,
                    "emotion":      None,
                    "formality":    0.1,
                    "last_message_was_emotional": False,
                }
                deep_analysis = await asyncio.wait_for(
                    self.deep_lang.analyze(text, conv_ctx), timeout=2.0
                )
                print(f"[Pipeline] A0 → emotion={deep_analysis.emotion_primary} "
                      f"intensity={deep_analysis.emotion_intensity:.2f} "
                      f"need='{deep_analysis.hidden_need}' "
                      f"script={deep_analysis.detected_script}", flush=True)
            except asyncio.TimeoutError:
                print("[Pipeline] A0 → DeepLang timeout (OK — proceeding)", flush=True)
            except Exception as _e:
                print(f"[Pipeline] A0 → DeepLang error: {_e}", flush=True)

        # Agent 1: Normalize
        norm_req = Message(from_agent="Orch", to_channel=Channel.LANGUAGE, action="normalize_script", payload={"text": text}, requires_response=True)
        norm_res = await asyncio.wait_for(self.bus.request(norm_req, timeout=5.0), timeout=6.0)
        norm_payload = norm_res.payload if norm_res else {"cleaned": text, "script": "general", "tokens": []}

        # Agent 2: Decode Slang
        decode_req = Message(from_agent="Orch", to_channel=Channel.MEMORY, action="decode_slang", payload={"tokens": norm_payload.get("tokens", []), "cleaned_text": norm_payload.get("cleaned", text)}, requires_response=True)
        decode_res = await asyncio.wait_for(self.bus.request(decode_req, timeout=5.0), timeout=6.0)
        decoded_map = decode_res.payload.get("decoded", {}) if decode_res else {}

        # Fallback: Local decode if A2 empty
        if not decoded_map and norm_payload.get("tokens"):
            print("[Orchestrator] A2 empty, using local vocab fallback", flush=True)
            decoded_map = await self._decode_tokens_locally(norm_payload.get("tokens", []))

        # Agent 3: Semantic Bridge
        bridge_req = Message(from_agent="Orch", to_channel=Channel.COMPREHENSION, action="build_semantic_bridge", payload={"raw_text": text, "decoded_tokens": decoded_map}, requires_response=True)
        bridge_res = await asyncio.wait_for(self.bus.request(bridge_req, timeout=20.0), timeout=25.0)
        semantic_english = bridge_res.payload.get("semantic_english", text) if bridge_res else text

        # Agent 4: Intent + Style
        intent_info = await self._get_tiered_intent(semantic_english)
        tier = int(intent_info.get("tier", 2))
        emotion = intent_info.get("emotion", "neutral")
        
        # Dialect prioritization: A1 detected script wins if confidence is high enough
        a1_script = norm_payload.get("script", "general")
        a4_dialect = intent_info.get("dialect_to_reply_in", "general")
        a1_confidence = norm_payload.get("confidence", 0.0)

        if a1_script != "general" and a1_confidence >= 0.30:
            dialect = a1_script
            print(f"[Pipeline] Dialect: using A1 detection '{dialect}' (conf={a1_confidence}) over A4='{a4_dialect}'", flush=True)
        else:
            dialect = a4_dialect

        style = intent_info.get("response_style", "casual")

        conv_key = f"owner_{source}"
        history  = self.conversations.get(conv_key, [])

        # ── NEW: Get relevant known context ──────────────────────────────────
        # ── NEW: Brain Architecture Logic (Hippocampus & Synaptic) ──────────
        brain_context = ""
        behavior_notes = ""
        
        if self.rag_engine:
            # ── Agent 4.5: Memory Question Detection ─────────────────────────
            is_memory_q = self._is_memory_question(semantic_english)
            memory_context = ""
            
            if is_memory_q:
                memory_results = await self.rag_engine.retrieve(
                    query=semantic_english,
                    memory_types=["episodic", "working", "semantic"],
                    n_results=5,
                    min_relevance=0.45
                )
                if memory_results:
                    memory_context = self.rag_engine.format_memories_for_prompt(memory_results, max_chars=400)
                    print(f"[RAG] Memory question detected. Found {len(memory_results)} relevant memories.", flush=True)
                else:
                    memory_context = "[HONEST: No memory found for this. Admit it naturally.]"
                    print(f"[RAG] Memory question — nothing found in {len(self.rag_engine.collections)} collections.", flush=True)

            # Standard RAG context (always run for persona awareness)
            raw_results = await self.rag_engine.query(semantic_english)
            brain_context = self.rag_engine.get_context_string(raw_results)
            
            # Combine if memory results found
            if memory_context:
                brain_context = f"{memory_context}\n\n{brain_context}"
            
        if self.reinforcement_engine:
            behavior_notes = self.reinforcement_engine.get_behavior_instructions()

        # ── A4.8: Causal Memory Context (ARION 3.0) ───────────────────────
        causal_context = ""
        if self.causal_graph:
            try:
                causal_context = self.causal_graph.get_context_for_message(
                    person=contact,
                    message=semantic_english,
                    current_emotion=emotion,
                )
                if causal_context:
                    print(f"[Pipeline] A4.8 → causal context found ({len(causal_context)} chars)", flush=True)
            except Exception as _e:
                print(f"[Pipeline] A4.8 → causal query error: {_e}", flush=True)

        # ── NEW: Curiosity check ──────────────────────────────────────────────
        conv_length = len(history)
        curious_question = self.curiosity_engine.should_ask(
            semantic_english=semantic_english,
            profile=self.reinforcement_engine.profile if self.reinforcement_engine else {},
            conversation_length=conv_length,
            current_emotion=emotion
        )

        # ── NEW: Connection Insight ──────────────────────────────────────────
        conn_insight = await self.connection_insight_engine.get_insight_if_ready(
            semantic_english=semantic_english,
            owner_emotion=emotion,
            profile=self.reinforcement_engine.profile if self.reinforcement_engine else {},
            conversation_length=conv_length
        )

        # ── A5: Cognition Engine (ARION 3.0) ─────────────────────────────
        cognition_action   = "reply"
        cognition_question = ""
        cognition_insight  = ""
        cognition_notes    = ""
        try:
            cog_req = Message(
                from_agent="Orch",
                to_channel=Channel.COGNITION,
                action="reason_and_plan",
                payload={
                    "semantic_text":       semantic_english,
                    "emotion":             emotion,
                    "emotion_intensity":   deep_analysis.emotion_intensity if deep_analysis else 0.3,
                    "intent":              intent_info,
                    "brain_context":       brain_context[:500] if brain_context else "",
                    "causal_context":      causal_context,
                    "conversation_length": conv_length,
                    "deep_analysis":       deep_analysis.to_dict() if deep_analysis else {},
                },
                requires_response=True,
            )
            cog_res = await asyncio.wait_for(
                self.bus.request(cog_req, timeout=5.0), timeout=6.0
            )
            if cog_res:
                cog_payload        = cog_res.payload
                cognition_action   = cog_payload.get("recommended_action", "reply")
                cognition_question = cog_payload.get("curiosity_question", "")
                cognition_insight  = cog_payload.get("insight", "")
                cognition_notes    = cog_payload.get("reasoning_notes", "")
                # Cognition curiosity overrides CuriosityEngine if present
                if cognition_question:
                    curious_question = cognition_question
                if cognition_insight:
                    conn_insight = cognition_insight
                print(f"[Pipeline] A5 → action={cognition_action} notes='{cognition_notes[:60]}'", flush=True)
        except (asyncio.TimeoutError, Exception) as _ce:
            print(f"[Pipeline] A5 → CognitionEngine unavailable: {_ce}", flush=True)

        # ── NEW: Check for permission grant ──────────────────────────────────
        perm = self.privacy_shield.parse_owner_permission_command(text)
        if perm:
            self.privacy_shield._grant_permission(perm["contact"], perm["topic"])
            await self._send_response(source, contact, f"✅ Got it. {perm['contact']} can now ask about {perm['topic']}.", payload)
            return

        history.append({"role": "user", "content": semantic_english})

        # STORE incoming text
        await self._store_turn(
            contact=contact, role="user", content=text,
            tier=tier, emotion=emotion, intent=intent_info.get("intent", ""), dialect=dialect
        )

        print(f"[Pipeline] A1 → script='{norm_payload.get('script')}' tokens={norm_payload.get('tokens')} confidence={norm_payload.get('confidence')}", flush=True)
        print(f"[Pipeline] A2 → decoded={list(decoded_map.keys())}", flush=True)
        print(f"[Pipeline] A3 → semantic='{semantic_english}'", flush=True)
        print(f"[Pipeline] A4 → intent='{intent_info.get('intent')}' emotion='{emotion}' dialect='{dialect}'", flush=True)

        owner_name = self.identity.get('name', 'Owner')
        texting_style = self.identity.get('texting_style', {}).get('close_friend', 'casual, slang, emojis')

        recent_conv_summary = self._build_conversation_summary(history)

        # Agent 5 (Ollama): Core Brain — now enriched with 3.0 cognitive layers
        system_prompt = (
            f"Respond as a real close friend texting {owner_name}.\n"
            f"Texting style: {texting_style}.\n"
        )

        # ── A0 deep analysis injection ────────────────────────────────────
        if deep_analysis:
            system_prompt += f"\n{deep_analysis.to_prompt_fragment()}\n"

        # ── A5 cognition notes ────────────────────────────────────────────
        if cognition_action == "comfort":
            system_prompt += "\n[COGNITION] Priority: comfort and emotional presence first. Keep reply warm and brief.\n"
        elif cognition_action == "celebrate":
            system_prompt += "\n[COGNITION] Priority: match their excitement and celebrate with them!\n"

        # ── A4.8 causal context ───────────────────────────────────────────
        if causal_context:
            system_prompt += f"\n{causal_context}\n"

        if behavior_notes:
            system_prompt += f"\nBEHAVIOR ADAPTATION:\n{behavior_notes}\n"

        if brain_context:
            system_prompt += f"\nRELEVANT CONTEXT (Use naturally):\n{brain_context}\n"
        else:
            system_prompt += (
                "\nYou're still learning about this person. If asked about their life, admit you're not sure yet.\n"
            )

        if conn_insight:
            system_prompt += (
                f"\nSPONTANEOUS INSIGHT (Mention this naturally if it fits the vibe):\n"
                f"{conn_insight}\n"
            )

        if recent_conv_summary:
            system_prompt += (
                f"\nRECENT CONVERSATION:\n"
                f"{recent_conv_summary}\n"
                "Use this to understand what topic is being discussed.\n"
            )

        if curious_question:
            system_prompt += (
                f"\nOPPORTUNITY: You can naturally ask this if conversation flows there: "
                f"\"{curious_question}\" — Only if it fits. Don't force it.\n"
            )

        system_prompt += (
            "\nCRITICAL RULES:\n"
            "- You are NEW. You don't know details about this person's life yet.\n"
            "- Talk like a real person. Short, casual, natural.\n"
            "- NEVER say 'digital twin', 'at your service', 'As an AI'.\n"
            "- If asked about family members: say something like 'dunno ra, tu hi bata' or 'naaku thelidu, cheppu'.\n"
            "- NEVER invent: family status, health details, work details, locations.\n"
            "- When unsure: respond with curiosity, not fabrication. Example: 'amma okay ga undha? nuvve cheppu ra'.\n"
            f"- Keep it {intent_info.get('length', 'short')}. Tone: {emotion}. Style: {style}.\n"
        )

        response = await self._call_ollama(system_prompt, history)
        if not response:
            fallbacks = {
                "question":      "naaku ippudu answer raaledu ra, malli try chestha",
                "greeting":      "hey ra 👋",
                "casual_check_in": "ikkade unna ra, connection issue ayyindhi 😅",
            }
            intent_type = intent_info.get("intent", "general")
            response = fallbacks.get(intent_type, "ra oka second ⏳")

        # Agent 6: Dialect Stylizer
        if "general" not in dialect.lower() and "english" not in dialect.lower():
            style_req = Message(from_agent="Orch", to_channel=Channel.LANGUAGE, action="stylize_dialect", payload={"text": response, "dialect": dialect, "emotion": emotion}, requires_response=True)
            style_res = await asyncio.wait_for(self.bus.request(style_req, timeout=5.0), timeout=6.0)
            if style_res:
                stylized = style_res.payload.get("stylized_text", "")
                if stylized and stylized.lower() != response.lower():
                    response = stylized
                    print(f"[Pipeline] A6 → stylized successfully", flush=True)
                else:
                    print(f"[Pipeline] A6 → no changes made, response staying in English", flush=True)

        print(f"[Pipeline] A5 → raw_response='{response[:60]}'", flush=True)
        print(f"[Pipeline] A6 → final='{response[:60]}'", flush=True)

        print(f"[Orchestrator] [Owner {dialect}] -> {response[:50]}", flush=True)
        history.append({"role": "assistant", "content": response})
        self.conversations[conv_key] = history[-self.max_history:]

        await self._store_turn(
            contact=contact, role="assistant", content=response,
            tier=tier, emotion="", intent="", dialect=dialect
        )

        await self._send_response(source, contact, response, payload)

        # ── A8: Reflection Engine (fire-and-forget) ───────────────────────
        self._response_counter += 1
        high_emotion = deep_analysis and deep_analysis.emotion_intensity > 0.65
        if high_emotion or self._response_counter % 10 == 0:
            asyncio.create_task(self._fire_reflection(
                contact=contact,
                user_text=text,
                arion_reply=response,
                emotion=emotion,
                emotion_intensity=deep_analysis.emotion_intensity if deep_analysis else 0.3,
                hidden_need=deep_analysis.hidden_need if deep_analysis else "unknown",
                topic=intent_info.get("intent", "general"),
                response_style=style,
            ))

        # ── A9: Goal Engine (fire-and-forget) ─────────────────────────────
        asyncio.create_task(self._fire_goal_update(
            contact=contact,
            message=semantic_english,
            emotion=emotion,
            topic=intent_info.get("intent", "general"),
        ))

        # ── Reinforcement (legacy — kept for backward compatibility) ──────
        if self.reinforcement_engine:
            pass  # Future: explicit feedback integration

    # ── ARION 3.0: Fire-and-forget helpers ─────────────────────────────────

    async def _fire_reflection(self, contact: str, user_text: str,
                                arion_reply: str, emotion: str,
                                emotion_intensity: float, hidden_need: str,
                                topic: str, response_style: str):
        """Send post-response data to ReflectionEngine (non-blocking)."""
        try:
            await self.send(
                to_channel=Channel.REFLECTION,
                action="post_response_learn",
                payload={
                    "contact":           contact,
                    "user_text":         user_text,
                    "arion_reply":       arion_reply,
                    "emotion":           emotion,
                    "emotion_intensity": emotion_intensity,
                    "hidden_need":       hidden_need,
                    "topic":             topic,
                    "response_style":    response_style,
                    "timestamp":         time.time(),
                }
            )
        except Exception as _e:
            print(f"[Orchestrator] A8 reflection fire failed: {_e}", flush=True)

    async def _fire_goal_update(self, contact: str, message: str,
                                 emotion: str, topic: str):
        """Send context to GoalEngine for goal tracking (non-blocking)."""
        try:
            await self.send(
                to_channel=Channel.GOAL,
                action="update_goals",
                payload={
                    "contact":   contact,
                    "message":   message,
                    "emotion":   emotion,
                    "topic":     topic,
                    "timestamp": time.time(),
                }
            )
        except Exception as _e:
            print(f"[Orchestrator] A9 goal update failed: {_e}", flush=True)

    async def _process_proxy_reply(
        self, text: str, contact: str, source: str, jid: str, payload: dict
    ):
        # Agent 1: Normalize
        norm_req = Message(from_agent="Orch", to_channel=Channel.LANGUAGE, action="normalize_script", payload={"text": text}, requires_response=True)
        norm_res = await asyncio.wait_for(self.bus.request(norm_req, timeout=5.0), timeout=6.0)
        norm_payload = norm_res.payload if norm_res else {"cleaned": text, "script": "general", "tokens": []}

        # Agent 2: Decode Slang
        decode_req = Message(from_agent="Orch", to_channel=Channel.MEMORY, action="decode_slang", payload={"tokens": norm_payload.get("tokens", []), "cleaned_text": norm_payload.get("cleaned", text)}, requires_response=True)
        decode_res = await asyncio.wait_for(self.bus.request(decode_req, timeout=5.0), timeout=6.0)
        decoded_map = decode_res.payload.get("decoded", {}) if decode_res else {}

        # Agent 3: Semantic Bridge
        bridge_req = Message(from_agent="Orch", to_channel=Channel.COMPREHENSION, action="build_semantic_bridge", payload={"raw_text": text, "decoded_tokens": decoded_map}, requires_response=True)
        bridge_res = await asyncio.wait_for(self.bus.request(bridge_req, timeout=20.0), timeout=25.0)
        semantic_english = bridge_res.payload.get("semantic_english", text) if bridge_res else text

        # Agent 4: Intent + Style
        intent_info = await self._get_tiered_intent(semantic_english)
        tier = int(intent_info.get("tier", 1))
        emotion = intent_info.get("emotion", "neutral")
        dialect = intent_info.get("dialect_to_reply_in", norm_payload.get("script", "general"))
        style = intent_info.get("response_style", "casual")

        # Context Fetching
        person_ctx = await self._get_person_ctx(contact)
        relationship = person_ctx.get("relationship", "stranger")
        style_notes = person_ctx.get("style", "")
        
        conv_key = f"proxy_{contact}"
        history  = self.conversations.get(conv_key, [])
        history.append({"role": "user", "content": semantic_english})

        await self._store_turn(
            contact=contact, role="user", content=text,
            tier=tier, emotion=emotion, intent=intent_info.get("intent", ""), dialect=dialect
        )

        print(f"[Pipeline Proxy] A1 → script='{norm_payload.get('script')}' tokens={norm_payload.get('tokens')}", flush=True)
        print(f"[Pipeline Proxy] A2 → decoded={list(decoded_map.keys())}", flush=True)
        print(f"[Pipeline Proxy] A3 → semantic='{semantic_english}'", flush=True)

        # ── NEW: Privacy Shield Interception ──────────────────────────────────
        privacy_result = self.privacy_shield.check(
            text=text,
            semantic=semantic_english,
            contact=contact,
            is_owner=False
        )

        if not privacy_result["safe"]:
            # Send deflection
            deflection = privacy_result.get("deflection", "naaku thelidu ra 😂")
            await self._send_response(source, contact, deflection, payload)

            # Alert owner
            if privacy_result.get("notify_owner"):
                alert = self.privacy_shield.build_owner_alert(privacy_result)
                await self.send(
                    to_channel=Channel.WHATSAPP,
                    action="send_whatsapp",
                    payload={"target": self.OWNER_JID, "text": alert}
                )

            print(f"[PrivacyShield] 🔒 Tier {privacy_result['tier']} block | {contact} asked about '{privacy_result['matched_keyword']}'", flush=True)
            return

        owner_name = self.identity.get('name', 'Owner')
        # Agent 5: Core Brain (Sanitized)
        system_prompt = (
            f"Respond as a real person {owner_name} in a chat with {contact}.\n"
            f"Style: {self.identity.get('texting_style', {}).get(relationship, 'casual')}.\n"
            "Rules:\n"
            "- Talk like a real person. Short, casual phrases.\n"
            "- NEVER say 'digital twin', 'AI', 'at your service', 'How can I assist'.\n"
            f"USER INFO: Relationship: {relationship}. {style_notes}\n"
            f"Reply in plain English. MATCH TONE: {emotion}. MATCH STYLE: {style}. Length: {intent_info.get('length', 'short')}.\n"
        )

        response_text = await self._call_ollama_raw(system_prompt, history)
        if not response_text:
            response_text = "👍"

        # Agent 6: Dialect Stylizer
        if "general" not in dialect.lower() and "english" not in dialect.lower():
            style_req = Message(from_agent="Orch", to_channel=Channel.LANGUAGE, action="stylize_dialect", payload={"text": response_text, "dialect": dialect, "emotion": emotion}, requires_response=True)
            style_res = await asyncio.wait_for(self.bus.request(style_req, timeout=5.0), timeout=6.0)
            if style_res:
                response_text = style_res.payload.get("stylized_text", response_text)

        print(f"[Pipeline Proxy] A5+A6 → final='{response_text[:40]}'", flush=True)

        print(f"[Orchestrator] [Proxy {dialect}] -> {response_text[:30]}")
        history.append({"role": "assistant", "content": response_text})
        self.conversations[conv_key] = history[-self.max_history:]

        await self._store_turn(
            contact=contact, role="assistant", content=response_text,
            tier=tier, emotion="", intent="", dialect=dialect
        )

        # High-emotion memory
        if emotion and tier >= 4:
            await self.send(
                to_channel=Channel.MEMORY, action="store_emotion",
                payload={"contact": contact, "content": text, "emotion": emotion, "intensity": "high", "timestamp": time.time()}
            )

        if "media" in payload:
            await self.send(
                to_channel=Channel.MEMORY, action="write_vault",
                payload={"path": f"People/{contact}/Media_Log.md", "content": f"| {time.strftime('%Y-%m-%d %H:%M')} | media | {payload.get('mimetype', '')} |"}
            )

        await self.send(to_channel=Channel.WHATSAPP, action="send_whatsapp", payload={"target": jid if jid else contact, "text": response_text})
        notify = f"🧠 [{dialect.upper()} Tier {tier}] {contact}: \"{text}\"\n[You]: \"{response_text}\""
        await self.send(to_channel=Channel.WHATSAPP, action="send_whatsapp", payload={"target": "919154716156@c.us", "text": notify})

    # ── Memory helper ─────────────────────────────────────────────────────────

    async def _get_person_ctx(self, contact: str) -> dict:
        try:
            bus = MessageBus()
            req = Message(
                from_agent="Orch", to_channel=Channel.MEMORY,
                action="get_person_ctx", payload={"contact": contact},
                requires_response=True
            )
            res = await asyncio.wait_for(bus.request(req, timeout=5.0), timeout=6.0)
            return res.payload if res else {}
        except:
            return {}

    async def _store_turn(
        self, contact: str, role: str, content: str,
        tier: int, emotion: str, intent: str, dialect: str
    ):
        """
        Fire-and-forget write to MemoryManager working memory.
        MemoryManager decides whether to also write episodic vault files
        based on tier threshold.
        """
        await self.send(
            to_channel=Channel.MEMORY,
            action="store_conversation",
            payload={
                "id":        f"{int(time.time()*1000)}_{contact}_{role}",
                "contact":   contact,
                "role":      role,
                "content":   content,
                "timestamp": time.time(),
                "tier":      tier,
                "emotion":   emotion,
                "intent":    intent,
                "dialect":   dialect,
            }
        )

    # ── Tools ────────────────────────────────────────────────────────────────

    async def _get_tiered_intent(self, text: str) -> dict:
        try:
            bus = MessageBus()
            req = Message(
                from_agent="Orch", to_channel=Channel.INTENT,
                action="extract_intent", payload={"text": text},
                requires_response=True
            )
            res = await asyncio.wait_for(bus.request(req, timeout=20.0), timeout=21.0)
            return res.payload if res else {}
        except:
            return {}

    async def _decode_tokens_locally(self, tokens: list) -> dict:
        """
        Fallback: If MemoryManager decode_slang returns empty,
        look up tokens directly against loaded vocab dicts.
        Zero network calls. Always available.
        """
        decoded = {}
        for token in tokens:
            token_lower = token.lower()
            # Check Telugu vocab
            if token_lower in self._te_all_words:
                decoded[token_lower] = {
                    "meaning": self._te_all_words[token_lower],
                    "language": "telugu",
                    "emotion": "neutral"
                }
                continue
            # Check Hindi vocab
            if token_lower in self._hi_all_words:
                decoded[token_lower] = {
                    "meaning": self._hi_all_words[token_lower],
                    "language": "hindi", 
                    "emotion": "neutral"
                }
        return decoded

    def _is_memory_question(self, semantic_english: str) -> bool:
        """
        Detects if owner is asking ARION to recall something.
        """
        memory_signals = [
            "do you remember", "remember when", "what did i",
            "what was the", "i told you", "i sent you",
            "we talked about", "you said", "earlier",
            "last time", "before", "yesterday", "that thing"
        ]
        sem = semantic_english.lower()
        return any(signal in sem for signal in memory_signals)

    def _build_conversation_summary(self, history: list, max_turns: int = 3) -> str:
        """
        Builds a compact recent conversation context.
        Shows ARION what was just being discussed.
        """
        if not history:
            return ""
        recent = history[-(max_turns * 2):] # Last N turns (user+assistant pairs)
        if not recent:
            return ""
        lines = []
        for turn in recent:
            role = "Owner" if turn["role"] == "user" else "You"
            content = turn["content"][:80] # Truncate long messages
            lines.append(f"{role}: {content}")
        return "\n".join(lines)


    async def _call_ollama(
        self, system_prompt: str, history: List[Dict[str, str]]
    ) -> Optional[str]:
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history[-self.max_history:])
        return await self._ollama_request(messages)

    async def _call_ollama_raw(
        self, system_prompt: str, history: List[Dict[str, str]]
    ) -> Optional[str]:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": f"Reply to: {history[-1]['content']}"}
        ]
        return await self._ollama_request(messages)

    async def _ollama_request(self, messages: List[Dict[str, str]], retries: int = 2) -> Optional[str]:
        if not aiohttp:
            print("[Orchestrator] aiohttp not installed!", flush=True)
            return None
            
        for attempt in range(retries + 1):
            try:
                timeout = aiohttp.ClientTimeout(total=45)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.post(
                        f"{self.ollama_url}/api/chat",
                        json={"model": self.model, "messages": messages, "stream": False},
                    ) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            return data.get("message", {}).get("content", "").strip()
                        else:
                            print(f"[Orchestrator] Ollama HTTP {resp.status} (attempt {attempt + 1})", flush=True)

            except (aiohttp.ClientConnectorError, asyncio.TimeoutError) as e:
                print(f"[Orchestrator] Ollama connection error - {type(e).__name__} (attempt {attempt + 1}/{retries + 1})", flush=True)
                if attempt < retries:
                    await asyncio.sleep(3) # Wait 3s before retry
            except Exception as e:
                print(f"[Orchestrator] Ollama Error: {e}", flush=True)
                break
        return None

    async def _send_response(
        self, source: str, contact: str, text: str, original_payload: dict
    ):
        if source == "whatsapp":
            await self.send(
                to_channel=Channel.WHATSAPP,
                action="send_whatsapp",
                payload={"target": original_payload.get("jid", contact), "text": text}
            )
        elif source == "voice":
            await self.send(
                to_channel=Channel.VOICE,
                action="speak",
                payload={"text": text}
            )

    # ────── Knowledge & Learning ──────────────────────────────────────────
    async def _handle_learn_command(self, text: str, contact: str, source: str, payload: dict):
        """
        Owner tells ARION to learn something specific.
        Syntax: 
          - "learn [domain] [title]" (Wikipedia fallback)
          - "learn [domain] [title]: [content]"
          - "learn [domain] [title]\n[content]"
        """
        raw_clean = text.replace("learn", "").strip()
        
        # Split by first colon or newline to separate title/domain from content
        parts = re.split(r'[:\n]', raw_clean, maxsplit=1)
        header = parts[0].strip()
        provided_content = parts[1].strip() if len(parts) > 1 else ""

        words = header.lower().split()
        if not words:
            await self._send_response(source, contact, "em learn cheyyali ra? 'learn movie Interstellar' ani cheppu", payload)
            return

        domain_keywords = {
            "movie": "movies_series", "series": "movies_series", "book": "books",
            "anime": "anime", "song": "music", "philosophy": "philosophy",
            "science": "science_biology_math", "tech": "computer_science_tech"
        }
        
        domain = "general"
        title_words = []
        for word in words:
            if word in domain_keywords: domain = domain_keywords[word]
            else: title_words.append(word)
        
        title = " ".join(title_words).strip().title()
        if not title:
            await self._send_response(source, contact, "Title correctly cheppu ra.", payload)
            return

        # Use provided content if available, else fallback to Wikipedia
        content = provided_content
        source_type = "manual_content"
        
        if not content:
            await self._send_response(source, contact, f"sare ra, '{title}' ni fetch chesi queue chestha 📚", payload)
            content = await self._fetch_wikipedia(title)
            source_type = "owner_request"
        else:
            await self._send_response(source, contact, f"sare ra, '{title}' contents ni immediate memory ingestion ki pampistunna. 🧠", payload)

        await self.send(
            to_channel=Channel.SCHEDULER,
            action="add_to_queue",
            payload={
                "title": title,
                "domain": domain,
                "content": content,
                "source_type": source_type,
                "priority": 9 # High priority triggers immediate ingestion
            }
        )
        
        await self.send(
            to_channel=Channel.SCHEDULER,
            action="add_to_queue",
            payload={
                "title": title,
                "domain": domain,
                "content": content,
                "source_type": "owner_request",
                "priority": 9
            }
        )

    async def _fetch_wikipedia(self, title: str) -> str:
        """Fetches the summary of a Wikipedia page."""
        try:
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title.replace(' ', '_')}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("extract", "")
        except: pass
        return ""

    # ────── Stubs for future API integrations ──────────────────────────
    async def _fetch_tmdb(self, title: str) -> str: return ""
    async def _fetch_anilist(self, title: str) -> str: return ""
    async def _fetch_genius(self, title: str) -> str: return ""
