"""
NEXUS-X ULTIMATE Pipeline Runner
The A1-A8 cognitive processing engine
Bulletproof execution with stage-specific error handling
"""

import asyncio
import logging
import time
import random
import traceback
import re
from typing import Dict, List, Any, Optional

from core.fleet.manager import fleet_manager
from config.system_config import JarvisConfig
from core.social_filter import apply_social_filter
from nexus.cognition.predictive_gate import PredictiveGate, GateDecision
from nexus.agents.critic import CriticAgent, CriticVerdict
from brain.learning.learner import NexusLearner
from nexus.agents.evaluator_agent import EvaluatorAgent

logger = logging.getLogger("PipelineRunner")

TEACHING_TRIGGERS = ["idi nerchuko", "listen", "nexus, listen", "idi gurthupettuko"]
GREETING_WORDS = ["hi", "hello", "hey", "namaste", "namaskaram", "yo", "sup", "nuvvu ela", "ela unnav", "gm", "gn"]

# Greeting responses: English for English input, Tenglish for Tenglish input
GREETING_RESPONSES_ENGLISH = [
    "Hi Boss! All systems are online. What do you need?",
    "Hey Boss! NEXUS is ready. What's up?",
    "Hello! Everything is running smoothly. How can I help?",
    "Hey! All agents are active and standing by. What can I do for you?",
    "Hi there, Boss! Ready to go. What's on your mind?"
]
GREETING_RESPONSES_TENGLISH = [
    "Hi Boss! Ela unnav? Em cheyali?",
    "Hey Boss! Nexus ready ga unnadi. Em cheppu?",
    "Namaste Boss! Online ga unnanu. Em help kavali?",
    "Hey! Anni systems stable ga unnai. Em chesthunnav?",
    "Yo Boss! Arion ikkade unnadu. Cheppu!"
]
# Keep legacy constant pointing at English for any code that still references it
GREETING_RESPONSES = GREETING_RESPONSES_ENGLISH

# Simple chatter that should also go through the fast-path (no web research)
CHATTER_PHRASES = [
    "how are you", "how r u", "how are u", "how ru", "what's up", "wassup", "whats up",
    "you okay", "you ok", "u ok", "u okay", "emo unnav", "ela unnav", "bagunnava",
    "em chesthunnav", "emi chesthunnav", "chasthunav"
]

CHATTER_RESPONSES = [
    "Bagunna Boss! Anni systems stable ga unnai. Meeru em chesthunnaru?",
    "Nexus fit ga unnadu! LTM active, brain running smooth. Meeru?",
    "Anni okay Boss. Memory loaded, connections active. Em sahaayam kavali?",
    "Super ga unnanu Boss! Ready to roll. Em plan?",
    "Chusevu Boss — nenu bagunnanu! Meeru ela unnaru?"
]



class PipelineRunner:
    """
    Executes the 8-stage cognitive pipeline:
    A1: Language Detection & Normalization
    A2: Memory Recall (Tiered)
    A3: Comprehension (Semantic Understanding)
    A4: Intent & Dialect Classification
    A5: Reasoning & Planning
    A6: Generation (Personalized)
    A7: Quality & Safety Check
    A8: Personality & Dialect Stylization
    A16: Psychological & Philosophical Analysis
    A17: Collaborative Boardroom Debate
    """

    def __init__(self, brain):
        self.brain = brain
        self.modules = brain.modules
        self.stats = {
            "total_processed": 0,
            "stage_failures": {},
            "avg_latency": 0.0
        }
        # Thalamic gate is still in core or could be moved
        from core.brain_gates import ThalamicGate
        self.thalamus = ThalamicGate()
        
        # New Predictive Gate & Critic
        self.predictive_gate = PredictiveGate(None, self.modules.get("ai")) 
        self.critic = CriticAgent(self.modules.get("ai"))
        self.learner = NexusLearner()
        self.evaluator = EvaluatorAgent()
        self.last_interaction = {}

    async def process(self, raw_input: str, source: str, sender: str, context: Dict) -> Dict[str, Any]:
        """Execute the full A1-A8 pipeline"""
        start_time = time.time()
        
        # Initial context for the pipeline
        pipeline_data = {
            "raw_input": raw_input,
            "source": source,
            "sender": sender,
            "context": context or {},
            "personality": context.get("personality", "jarvis"),
            "stages_completed": []
        }

        # ── FEEDBACK LOOP: Evaluate previous interaction ─────
        if self.last_interaction:
            await self.evaluator.evaluate_feedback(raw_input, self.last_interaction)

        try:
            # ── A1: Language ───────────────────────────────────────
            pipeline_data = await self._stage_a1_language(pipeline_data)
            pipeline_data = await self.thalamus.process(pipeline_data)

            # ── GREETING FAST-PATH (Instant Short-Circuit) ────────
            cleaned_input = raw_input.lower().strip()
            
            # Technical keywords that should NEVER be treated as a simple greeting
            tech_keywords = ["code", "java", "python", "script", "how to", "debug", "math", "search", "who", "what"]
            has_tech_intent = any(tk in cleaned_input for tk in tech_keywords)
            
            # Precise greeting check: either exact match or starts with a greeting followed by space/end
            is_precise_greeting = False
            for g in GREETING_WORDS:
                if cleaned_input == g or cleaned_input.startswith(g + " "):
                    is_precise_greeting = True
                    break
            
            is_greeting = (
                (is_precise_greeting or "jarvis" == cleaned_input or "jarivs" == cleaned_input) and
                not has_tech_intent and
                len(cleaned_input) < 50 # Greetings aren't usually long essays
            )
            
            if is_greeting:
                logger.info("[Pipeline] Common greeting/chatter detected. Activating INSTANT-PATH.")
                
                # Use language-matched greeting — English in → English out
                detected_lang = pipeline_data.get("language", "english")
                if detected_lang == "tenglish":
                    response = random.choice(GREETING_RESPONSES_TENGLISH)
                else:
                    # Default English (or Telugu-script input → unlikely for a plain "Hi")
                    response = random.choice(GREETING_RESPONSES_ENGLISH)
                
                latency = time.time() - start_time
                return {
                    "response": response,
                    "bubbles": [response],
                    "emotion": "happy",
                    "intent": "greeting",
                    "language": pipeline_data.get("language", "tenglish"),
                    "dialect": pipeline_data.get("dialect", "general"),
                    "processing_time": latency,
                    "stages": ["language", "thalamus", "instant-path"]
                }

            # ── CHATTER FAST-PATH (How are you? etc.) ─────────────
            is_chatter = any(phrase in cleaned_input for phrase in CHATTER_PHRASES)
            if is_chatter:
                logger.info("[Pipeline] Simple chatter detected. Activating CHATTER FAST-PATH.")
                response = random.choice(CHATTER_RESPONSES)
                latency = time.time() - start_time
                return {
                    "response": response,
                    "bubbles": [response],
                    "emotion": "happy",
                    "intent": "chatter",
                    "language": pipeline_data.get("language", "tenglish"),
                    "dialect": pipeline_data.get("dialect", "general"),
                    "processing_time": latency,
                    "stages": ["language", "thalamus", "instant-path"]
                }

            # Short-circuit if learning event
            if pipeline_data.get("is_learning_event"):
                pipeline_data = await self._stage_a8_personality(pipeline_data)
                return {
                    "response": pipeline_data.get("response_text", ""),
                    "bubbles": pipeline_data.get("bubbles", [pipeline_data.get("response_text", "")]),
                    "emotion": "proud",
                    "intent": "learning",
                    "language": pipeline_data.get("language", "english"),
                    "dialect": pipeline_data.get("dialect", "general"),
                    "processing_time": time.time() - start_time,
                    "stages": pipeline_data["stages_completed"]
                }
            
            # ── A2: Memory ─────────────────────────────────────────
            pipeline_data = await self._stage_a2_memory(pipeline_data)
            
            # ── A2.5: Predictive Gate 🛡️ ──────────────────────────
            gate_res = await self.predictive_gate.evaluate(
                pipeline_data["normalized_text"], 
                pipeline_data.get("memories", [])
            )
            pipeline_data["gate_result"] = gate_res.to_dict()
            
            if gate_res.decision == GateDecision.REJECT:
                pipeline_data["response_text"] = f"I cannot confirm that information based on my current world model, Sir. (Reason: {gate_res.reason})"
                return await self._stage_a8_personality(pipeline_data)
            elif gate_res.decision == GateDecision.REQUIRE_VERIFICATION:
                pipeline_data["research_needed"] = True
            elif gate_res.decision == GateDecision.REQUIRE_HUMAN:
                pipeline_data["response_text"] = "This request is highly unexpected and conflicts with my core knowledge. I'm escalating this to the Boss for manual review."
                return await self._stage_a8_personality(pipeline_data)
            
            # ── A3: Comprehension (Working Memory) ─────────────────
            pipeline_data = await self._stage_a3_comprehension(pipeline_data)
            
            # ── A4: Intent ─────────────────────────────────────────
            pipeline_data = await self._stage_a4_intent(pipeline_data)
            
            # ── A5: Reasoning ──────────────────────────────────────
            pipeline_data = await self._stage_a5_reasoning(pipeline_data)
            
            # ── A6: Generation ─────────────────────────────────────
            pipeline_data = await self._stage_a6_generation(pipeline_data)
            
            # ── A7: Quality ────────────────────────────────────────
            pipeline_data = await self._stage_a7_quality(pipeline_data)
            
            # ── A8: Personality ────────────────────────────────────
            pipeline_data = await self._stage_a8_personality(pipeline_data)
            
            # ── A16: Psyche ────────────────────────────────────────
            if hasattr(self.brain, 'psyche'):
                psyche_data = await self.brain.psyche.analyze_psyche(pipeline_data["raw_input"], pipeline_data)
                pipeline_data["psyche"] = psyche_data
                pipeline_data["stages_completed"].append("A16")
                
            # ── A17: Boardroom ─────────────────────────────────────
            # Trigger ONLY for truly complex tasks, not greetings or chatter
            is_complex = len(pipeline_data["raw_input"]) > 300 and not is_greeting
            if (pipeline_data.get("reasoning_mode") == "associative" and is_complex) or "discuss" in pipeline_data["raw_input"].lower():
                from core.fleet.boardroom import boardroom
                debate_topic = pipeline_data["raw_input"]
                transcript = await boardroom.run_debate(debate_topic, max_rounds=1)
                # Injected 'Voices' into the response
                voices = "\n".join([f"({t['agent']}): {t['content'][:100]}..." for t in transcript])
                pipeline_data["response_text"] += f"\n\n[Internal Fleet Consensus]:\n{voices}"
                pipeline_data["stages_completed"].append("A17")

            latency = time.time() - start_time
            self._update_stats(latency)
            
            return {
                "response": pipeline_data.get("response_text", ""),
                "bubbles": pipeline_data.get("bubbles", [pipeline_data.get("response_text", "")]),
                "personality": pipeline_data.get("personality", "jarvis"),
                "emotion": pipeline_data.get("emotion_to_express", "neutral"),
                "intent": pipeline_data.get("intent", "general"),
                "language": pipeline_data.get("language", "english"),
                "dialect": pipeline_data.get("dialect", "general"),
                "processing_time": latency,
                "stages": pipeline_data["stages_completed"]
            }
            
            # Store for feedback loop
            self.last_interaction = {
                "query": raw_input,
                "answer": result["response"]
            }
            
            return result

        except Exception as e:
            logger.error(f"Pipeline crashed: {e}")
            logger.error(traceback.format_exc())
            return self._handle_pipeline_failure(e, pipeline_data)

    # ═══════════════════════════════════════════════════
    # STAGE IMPLEMENTATIONS
    # ═══════════════════════════════════════════════════

    async def _stage_a1_language(self, data: Dict) -> Dict:
        """A1: Detect language and normalize script"""
        try:
            text = data["raw_input"]
            # ── DYNAMIC LANGUAGE DETECTION ──────────────────────
            lang = "english"
            dialect = "general"
            
            # Detect Telugu script
            has_telugu_script = bool(re.search(r'[\u0c00-\u0c7f]', text))
            
            # Detect Tenglish markers (Romanized Telugu - comprehensive list)
            tenglish_markers = [
                # Pronouns / Address
                "neeku", "meeku", "naaku", "maaku", "vaallu", "vaadu", "aame",
                # Common verbs
                "unnav", "unnaru", "unnana", "chesav", "chesthav", "chesthunnav",
                "chesaav", "thalusa", "thelusa", "telusa", "thelusu", "velladu",
                "cheppadu", "cheppu", "cheppara", "chesthunna", "chasthunav",
                "paduthunna", "chudaali", "chudavu", "cheyaali", "cheyyandi",
                # Filler / Question words
                "enti", "ela", "avuna", "nijama", "bagundhi", "em", "emo",
                "ekkada", "enduku", "evaru", "epraju", "evaraina",
                # Responses
                "ante", "ikkade", "akkade", "okka", "anni", "antha", "ila",
                "adi", "idi", "ivi", "avunu", "ledu", "ayya", "ayindi",
                # Casual markers (NOTE: "jarvis"/"boss"/"bro" intentionally excluded
                # — they appear in plain English and cause false Tenglish classification)
                "ra", "da", "ga", "le", "anna", "annaya", "amma",
                "machaa", "machi",
                # Greetings
                "bagunnava", "bagunna", "inthaki", "meeru", "nuvvu",
            ]
            has_tenglish = any(word in text.lower().split() for word in tenglish_markers)
            # Also check for partial matches in common stems
            tenglish_stems = ["thalus", "thelus", "unnav", "unnaru", "chesty", "chesth", "avun"]
            if not has_tenglish:
                has_tenglish = any(stem in text.lower() for stem in tenglish_stems)
            
            if has_telugu_script:
                lang = "telugu"
            elif has_tenglish:
                lang = "tenglish"
            
            # Explicit language request check
            if "telugu lo" in text.lower() or "in telugu" in text.lower():
                lang = "telugu"
            
            if "language_engine" in self.modules:
                mod_lang, mod_dialect = await self.modules["language_engine"].detect(text)
                # Allow module to override if it's more confident
                if mod_lang != "english": lang = mod_lang
            
            # Use ScholarAgent to refine dialect and register
            if "scholar" in self.modules:
                term_info = await self.modules["scholar"].classify_term(text, "initial_detection")
                dialect = term_info.dialect
                data["register"] = term_info.register

            data.update({
                "language": lang,
                "dialect": dialect,
                "normalized_text": text.strip()
            })

            # TEACHING MODE (A1 STUDENT LOGIC)
            is_learning_event = any(trigger in text.lower() for trigger in TEACHING_TRIGGERS)
            if is_learning_event:
                # Format: "Nexus, listen, 'Kaiku' means 'Why' in Hyderabad slang"
                parts = text.split("means")
                if len(parts) == 2:
                    phrase = parts[0].split(",")[-1].strip().replace("'", "").replace('"', "")
                    meaning_full = parts[1].strip()
                    # Further split meaning for context if possible
                    meaning = meaning_full.split(" in ")[0].strip()
                    dialect_found = "General"
                    if " in " in meaning_full:
                        dialect_found = meaning_full.split(" in ")[1].replace("slang", "").strip()
                    
                    learn_res = self.learner.learn(phrase, meaning, "slang", dialect_found)
                    data["response_text"] = learn_res
                    data["is_learning_event"] = True
                    data["stages_completed"].append("A1-STUDENT")
                else:
                    data["response_text"] = "I'm listening, Sir. What should I learn? (Format: 'Phrase means Meaning')"
                    data["is_learning_event"] = True

            data["stages_completed"].append("A1")
        except Exception as e:
            self._log_stage_error("A1", e)
            data.update({"language": "english", "dialect": "general", "normalized_text": data["raw_input"]})
        return data

    async def _stage_a2_memory(self, data: Dict) -> Dict:
        """A2: Recall relevant memories from 7 tiers"""
        try:
            if "memory" in self.modules:
                memories = await self.modules["memory"].recall(
                    data["normalized_text"], 
                    limit=5
                )
                data["memories"] = memories
            else:
                data["memories"] = []
            data["stages_completed"].append("A2")
        except Exception as e:
            self._log_stage_error("A2", e)
            data["memories"] = []
        return data

    async def _stage_a3_comprehension(self, data: Dict) -> Dict:
        """A3: Deep semantic understanding with Working Memory limit"""
        try:
            text = data["normalized_text"]
            
            # BIOLOGICAL LIMIT: Enforce 4-chunk limit for active reasoning
            # We treat each memory or key context piece as a 'chunk'
            memories = data.get("memories", [])
            active_chunks = memories[:4] # Enforce biological limit
            data["memories"] = active_chunks
            
            if len(text) > 30 or "?" in text:
                if "ai" in self.modules:
                    # Provide only limited chunks to the AI to prevent distraction
                    context_snippet = "\n".join([m.get("content", "")[:200] for m in active_chunks])
                    prompt = f"Context:\n{context_snippet}\n\nUnderstand the true intent: '{text}'"
                    understanding = await self.modules["ai"].generate(prompt, max_tokens=100, use_fast=True)
                    data["deep_understanding"] = understanding
            
            if "deep_understanding" not in data:
                data["deep_understanding"] = text
                
            data["stages_completed"].append("A3")
        except Exception as e:
            self._log_stage_error("A3", e)
            data["deep_understanding"] = data["normalized_text"]
        return data

    async def _stage_a4_intent(self, data: Dict) -> Dict:
        """A4: Classify intent and response style"""
        try:
            text = data["normalized_text"]
            # Simple heuristic or AI-based
            intent = "conversation"
            if "?" in text: intent = "question"
            elif any(cmd in text.lower() for cmd in ["open", "run", "do"]): intent = "action"
            
            data["intent"] = intent
            data["stages_completed"].append("A4")
        except Exception as e:
            self._log_stage_error("A4", e)
            data["intent"] = "conversation"
        return data

    async def _stage_a5_reasoning(self, data: Dict) -> Dict:
        """
        A5: Reasoning and planning
        Dual-Mode: Executive Control (Hank/Atlas) vs Associative (Arion/Cleo)
        """
        try:
            intent = data.get("intent", "conversation")
            text = data.get("normalized_text", "")
            
            # MODE TOGGLE (Executive vs Associative)
            if intent in ["action", "code", "math", "fact"]:
                data["reasoning_mode"] = "executive"
                data["plan"] = ["generate_precise_response", "validate_facts"]
            elif intent in ["creative", "conversation"] or len(text) > 100:
                data["reasoning_mode"] = "associative"
                data["plan"] = ["brainstorm_connections", "stylize_narrative"]
            else:
                data["reasoning_mode"] = "habitual"
                data["plan"] = ["direct_response"]
            
            # Associative search (DMN analog)
            if data["reasoning_mode"] == "associative":
                # Spread activation in neural graph if available
                if "hebbian" in self.modules:
                    # Mock associative spread for now
                    pass
            
            data["stages_completed"].append("A5")
        except Exception as e:
            self._log_stage_error("A5", e)
            data["plan"] = ["generate_response"]
        return data

    async def _stage_a6_generation(self, data: Dict) -> Dict:
        """A6: Generate personalized response"""
        try:
            # Check if Fleet Mode is enabled
            if JarvisConfig.FLEET_MODE:
                # Use Fleet Manager for Peer-Review Loop
                # Decide which doer based on intent
                if data["intent"] == "action":
                    doer = "hank"
                elif data["intent"] == "question" and len(data["raw_input"]) > 100:
                    doer = "atlas"  # Deep questions go to researcher
                else:
                    doer = "arion"  # General chat and simple questions go to Arion
                # Skip heavy fleet logic for simple greetings
                if data.get("intent") == "greeting":
                    logger.info("Fleet: Skipping peer-review for greeting.")
                    ai_res = await self.modules["ai"].generate(f"You are {data['personality'].upper()}. Respond briefly to: {data['raw_input']}", use_fast=True)
                    data["response_text"] = ai_res
                else:
                    fleet_result = await fleet_manager.execute_task(
                        data["raw_input"], 
                        doer_id=doer, 
                        language=data.get("language", "english")
                    )
                    data["response_text"] = fleet_result["response"]
                    data["fleet_stats"] = {
                        "score": fleet_result["score"],
                        "feedback": fleet_result["feedback"],
                        "latency": fleet_result["latency_ms"]
                    }
                    logger.info(f"Fleet Generation Complete: {doer} (Score: {fleet_result['score']})")
            elif "ai" in self.modules:
                # Construct prompt with all context
                persona = data["personality"]
                prompt = self._build_generation_prompt(data)
                
                # Update system prompt to enforce language matching
                system_prompt = f"You are NEXUS ({persona.upper()}). MATCH THE USER'S LANGUAGE: {data['language'].upper()}."
                if data['language'] == 'telugu':
                    system_prompt += " Respond in TELUGU SCRIPT. NO ENGLISH TRANSLATIONS."
                elif data['language'] == 'tenglish':
                    system_prompt += " Respond in MIXED TELUGU+ENGLISH (Tenglish). NO ENGLISH TRANSLATIONS."
                
                response = await self.modules["ai"].generate(
                    prompt, 
                    max_tokens=500,
                    system=system_prompt
                )
                data["response_text"] = response
            else:
                data["response_text"] = "I'm currently unable to think deeply, but I'm here."
                
            data["stages_completed"].append("A6")
        except Exception as e:
            self._log_stage_error("A6", e)
            data["response_text"] = "Something went wrong in my thinking process."
        return data

    async def _stage_a7_quality(self, data: Dict) -> Dict:
        """A7: Quality and Safety check — also blocks any script-leakage."""
        try:
            # Filter AI-isms
            response = data.get("response_text", "")
            bad_phrases = ["as an ai", "i don't have feelings", "i am an ai"]
            for phrase in bad_phrases:
                if phrase in response.lower():
                    response = response.replace(phrase, "")
            
            # ── SCRIPT LEAKAGE GUARD (Relaxed) ──────────────────────────────────
            # Only strip if we are in strict English mode and there's significant leakage.
            lang = data.get("language", "english")
            if lang == "english":
                # Check for Indic script leakage in English mode
                has_script_leakage = bool(re.search(r'[\u0900-\u0DFF]', response))
                if has_script_leakage:
                    # Only strip if the response has a high percentage of non-Latin characters
                    indic_chars = len(re.findall(r'[\u0900-\u0DFF]', response))
                    if indic_chars > len(response) * 0.3: # More than 30% leakage
                        logger.warning(f"[A7] Heavy script leakage detected in English response! Stripping.")
                        response = re.sub(r'[\u0900-\u0DFF]+', '', response)
                        response = re.sub(r'\s{2,}', ' ', response).strip()
            
            # Safe fallback if stripping made the message too short
            if not response.strip() or len(response) < 5:
                if lang == "tenglish":
                    response = "Boss, meeru cheppindi ardham aindi. Can you repeat that?"
                else:
                    response = "I understood you, Boss. Could you please rephrase that?"
            # ─────────────────────────────────────────────────────────────

            data["response_text"] = response.strip()
            data["stages_completed"].append("A7")
        except Exception as e:
            self._log_stage_error("A7", e)
        return data

    async def _stage_a8_personality(self, data: Dict) -> Dict:
        """A8: Stylization and humanization"""
        try:
            # Apply dialect and persona-specific filters
            response = data.get("response_text", "")
            
            # Apply Social Filter (WHO + HOW) — must be awaited!
            sender_name = data.get("sender", "unknown")
            social_data = await apply_social_filter(
                response, 
                sender_name, 
                context=data.get("raw_input", "")
            )
            
            # Apply Scholar Social Filter refinement
            if "scholar" in self.modules:
                advice = self.modules["scholar"].get_social_filter_advice(sender_name, response)
                if advice != "Appropriate":
                    logger.warning(f"Scholar Advice: {advice}")
                    # In a full setup, we'd regenerate or fix the response here

            response = social_data.get("adapted_response", response)
            data["social_intelligence"] = social_data
            data["bubbles"] = social_data.get("bubbles", [response])
            
            data["response_text"] = response
            data["stages_completed"].append("A8")
        except Exception as e:
            self._log_stage_error("A8", e)
        return data

    # ═══════════════════════════════════════════════════
    # HELPERS
    # ═══════════════════════════════════════════════════

    def _sanitize_memory_for_language(self, memories: list, lang: str) -> str:
        """Strip script that conflicts with expected response language."""
        import re
        results = []
        for m in memories[:5]:
            content = m.get("content", "")[:350]
            if lang in ("english", "tenglish"):
                # Remove Telugu script characters — they confuse the LLM into switching to Telugu
                content = re.sub(r'[\u0c00-\u0c7f]+', '', content).strip()
                # Remove Hindi Devanagari too
                content = re.sub(r'[\u0900-\u097f]+', '', content).strip()
            if content:
                results.append(f"- {content}")
        return "\n".join(results) if results else "No relevant memories found."

    def _build_generation_prompt(self, data: Dict) -> str:
        """Build the master prompt for A6"""
        persona = data["personality"]
        memories = data.get("memories", [])
        lang = data.get("language", "english")

        # Sanitize memory content based on target language
        mem_str = self._sanitize_memory_for_language(memories, lang)

        # ── MOTHER PERSONA INJECTION ──────────────────────────────────────────
        mother_directive = ""
        if persona == "mother" or persona == "amma":
            lang = "tenglish"  # force Tenglish for mother
            try:
                import json
                with open("config/mother_persona.json", "r", encoding="utf-8") as f:
                    config = json.load(f)
                    mother_directive = (
                        f"\n[MOTHER PERSONA INSTRUCTIONS]:\n"
                        f"- Tone Guidelines: {config.get('tone_instructions')}\n"
                        f"- Affectionate Terms to use: {', '.join(config.get('affectionate_terms', []))}\n"
                        f"- Typical Mother Expressions: {', '.join(config.get('scolding_phrases', []))}\n"
                        f"Adopt this personality. Address the user as your child (Kanna/Kannayya/Babu)."
                    )
            except Exception:
                pass

        lang_directive = {
            "telugu": "RESPOND IN TELUGU SCRIPT ONLY. No English. No Hindi.",
            "tenglish": "RESPOND IN TENGLISH — Telugu+English mixed ONLY. No Telugu script. No Hindi. No translations in brackets.",
            "english": "RESPOND IN ENGLISH ONLY. No Telugu. No Hindi. No translations.",
        }.get(lang, "RESPOND IN ENGLISH ONLY.")

        return f"""You are NEXUS acting as {persona.upper()}.
{mother_directive}

╔══ LANGUAGE RULE (HIGHEST PRIORITY) ══╗
║ {lang_directive}
║ The memory below may be in Telugu — IGNORE the script, use the INFORMATION.
╚═══════════════════════════════════════╝

[LONG-TERM MEMORY — Use this knowledge if relevant]:
{mem_str}

[UNDERSTANDING OF USER'S QUESTION]: {data.get('deep_understanding', '')}

[USER INPUT]: {data['raw_input']}

Respond as {persona.upper()} naturally. Use the memory above to give an informed answer. {lang_directive}"""

    def _log_stage_error(self, stage: str, error: Exception):
        logger.warning(f"Stage {stage} failed: {error}")
        self.stats["stage_failures"][stage] = self.stats["stage_failures"].get(stage, 0) + 1

    def _update_stats(self, latency: float):
        self.stats["total_processed"] += 1
        self.stats["avg_latency"] = (self.stats["avg_latency"] * (self.stats["total_processed"] - 1) + latency) / self.stats["total_processed"]

    def _handle_pipeline_failure(self, error: Exception, data: Dict) -> Dict:
        """Fallback response if entire pipeline fails"""
        return {
            "response": "Boss, oka chinna issue vasindi. Malli try cheyyi!",
            "emotion": "confused",
            "intent": "error",
            "processing_time": 0.0,
            "stages": data.get("stages_completed", [])
        }

