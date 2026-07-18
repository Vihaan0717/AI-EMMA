"""
NEXUS-X OMEGA Master Brain
The central intelligence - thinks like a human
"""

import asyncio
import json
import logging
import datetime
import traceback
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger('NexusBrain')


class ThinkingState(Enum):
    IDLE = "idle"
    LISTENING = "listening"
    UNDERSTANDING = "understanding"
    THINKING = "thinking"
    PLANNING = "planning"
    ACTING = "acting"
    SPEAKING = "speaking"
    LEARNING = "learning"
    HEALING = "healing"
    DREAMING = "dreaming"  # Memory consolidation


@dataclass
class Thought:
    """Represents a single thought/processing unit"""
    raw_input: str
    understood_meaning: str = ""
    intent: str = ""
    emotion_detected: str = "neutral"
    emotion_to_express: str = "neutral"
    language: str = "english"
    dialect: str = "general"
    memories_recalled: List = field(default_factory=list)
    plan: List[str] = field(default_factory=list)
    tools_needed: List[str] = field(default_factory=list)
    response_text: str = ""
    response_voice: Optional[bytes] = None
    confidence: float = 0.0
    processing_time: float = 0.0
    timestamp: str = field(
        default_factory=lambda: str(datetime.datetime.now())
    )


class NexusBrain:
    """
    The Master Brain of NEXUS-X OMEGA
    
    Processes everything like a human:
    1. SENSE   - Receive input from any source
    2. FEEL    - Detect emotion in input
    3. UNDERSTAND - Deep comprehension
    4. RECALL  - Relevant memories
    5. THINK   - Reason and plan
    6. DECIDE  - Choose best action
    7. ACT     - Execute plan with tools
    8. SPEAK   - Respond naturally
    9. LEARN   - Store experience
    10. GROW   - Self-improve
    """

    def __init__(self, modules: Dict):
        self.modules = modules
        self.state = ThinkingState.IDLE
        self.current_thought: Optional[Thought] = None
        self.thought_history: List[Thought] = []
        self.conversation_context: List[Dict] = []
        self.daily_stats = {
            "conversations": 0,
            "thoughts_processed": 0,
            "tools_used": 0,
            "memories_stored": 0,
            "errors_healed": 0,
            "self_improvements": 0,
            "emotions_understood": 0
        }
        logger.info("🧠 Master Brain initialized")

    async def run_forever(self):
        """Keep the brain thinking 24/7"""
        logger.info("🧠 Brain entering 24/7 thinking mode...")
        while True:
            try:
                # Proactive thinking when idle
                if self.state == ThinkingState.IDLE:
                    await self._idle_thinking()
                await asyncio.sleep(0.1)
            except Exception as e:
                logger.error(f"Brain error: {e}")
                await self._self_heal(str(e))

    async def process(
        self,
        raw_input: str,
        source: str = "text",
        sender: str = "user",
        context: Dict = None
    ) -> Dict[str, Any]:
        """
        MAIN PROCESSING PIPELINE
        The complete human-like thinking process
        """
        start_time = datetime.datetime.now()
        self.state = ThinkingState.UNDERSTANDING

        # Create a new thought
        thought = Thought(raw_input=raw_input)

        try:
            logger.info(f"🧠 Processing: '{raw_input[:60]}...'")

            # ── STEP 1: FEEL ──────────────────────────────────────
            self.state = ThinkingState.UNDERSTANDING
            thought.emotion_detected = await self._detect_emotion(
                raw_input
            )
            self.daily_stats["emotions_understood"] += 1

            # ── STEP 2: UNDERSTAND ────────────────────────────────
            thought.understood_meaning = await self._deep_understand(
                raw_input, thought.emotion_detected
            )
            thought.language, thought.dialect = (
                await self._detect_language(raw_input)
            )
            thought.intent = await self._classify_intent(
                raw_input, thought.understood_meaning
            )

            # ── STEP 3: RECALL MEMORIES ───────────────────────────
            self.state = ThinkingState.THINKING
            thought.memories_recalled = await self._recall_memories(
                raw_input, thought.intent
            )

            # ── STEP 4: THINK & PLAN ──────────────────────────────
            thought.plan = await self._create_plan(
                thought.understood_meaning,
                thought.intent,
                thought.memories_recalled,
                context or {}
            )

            # ── STEP 5: USE TOOLS IF NEEDED ───────────────────────
            self.state = ThinkingState.ACTING
            tool_results = {}
            if thought.tools_needed:
                tool_results = await self._use_tools(thought.tools_needed)
                self.daily_stats["tools_used"] += len(thought.tools_needed)

            # ── STEP 6: GENERATE RESPONSE ─────────────────────────
            self.state = ThinkingState.SPEAKING
            thought.response_text = await self._generate_response(
                thought, tool_results, context or {}
            )

            # ── STEP 7: STYLIZE RESPONSE ──────────────────────────
            thought.response_text = await self._stylize_response(
                thought.response_text,
                thought.language,
                thought.dialect,
                thought.emotion_to_express
            )

            # ── STEP 8: QUALITY CHECK ─────────────────────────────
            thought.response_text = await self._quality_check(
                thought.response_text, raw_input
            )

            # ── STEP 9: LEARN FROM THIS ───────────────────────────
            self.state = ThinkingState.LEARNING
            await self._learn_from_thought(thought, sender)
            self.daily_stats["memories_stored"] += 1

            # ── STEP 10: CALCULATE CONFIDENCE ────────────────────
            thought.confidence = self._calculate_confidence(thought)
            thought.processing_time = (
                datetime.datetime.now() - start_time
            ).total_seconds()

            # Update stats
            self.daily_stats["conversations"] += 1
            self.daily_stats["thoughts_processed"] += 1

            # Store in history
            self.thought_history.append(thought)
            self.conversation_context.append({
                "role": "user",
                "content": raw_input
            })
            self.conversation_context.append({
                "role": "assistant",
                "content": thought.response_text
            })

            # Keep context window manageable (last 20 turns)
            if len(self.conversation_context) > 40:
                self.conversation_context = (
                    self.conversation_context[-40:]
                )

            self.state = ThinkingState.IDLE
            logger.info(
                f"✅ Processed in {thought.processing_time:.2f}s "
                f"| Confidence: {thought.confidence:.0%}"
            )

            return {
                "response": thought.response_text,
                "emotion": thought.emotion_to_express,
                "intent": thought.intent,
                "language": thought.language,
                "confidence": thought.confidence,
                "processing_time": thought.processing_time,
                "memories_used": len(thought.memories_recalled)
            }

        except Exception as e:
            logger.error(f"❌ Brain processing error: {e}")
            logger.error(traceback.format_exc())
            await self._self_heal(str(e))
            self.state = ThinkingState.IDLE
            return {
                "response": self._get_error_response(
                    thought.language if thought else "english"
                ),
                "emotion": "apologetic",
                "intent": "error_recovery",
                "confidence": 0.1,
                "processing_time": 0.0
            }

    async def _detect_emotion(self, text: str) -> str:
        """Detect human emotion in text with high accuracy"""
        # Emotion word maps
        emotion_maps = {
            "joy": [
                "happy", "great", "awesome", "love", "wonderful",
                "excellent", "amazing", "fantastic", "good", "yay",
                "haha", "lol", "😊", "😄", "❤️", "superb",
                "khushi", "mast", "badhiya", "chala bagundi"
            ],
            "sadness": [
                "sad", "depressed", "unhappy", "cry", "tears",
                "lonely", "miss", "hurt", "pain", "hopeless",
                "dukha", "bade bura", "dil toota", "badha kastam"
            ],
            "anger": [
                "angry", "furious", "hate", "frustrated", "annoyed",
                "irritated", "mad", "rage", "terrible", "worst",
                "gussa", "kopa", "pedda kopa", "chala frustrated"
            ],
            "fear": [
                "scared", "afraid", "worried", "anxious", "nervous",
                "panic", "terror", "frighten", "stress", "tension",
                "bhaya", "tension ga", "worry", "nervous ga"
            ],
            "surprise": [
                "wow", "omg", "really", "seriously", "what",
                "unbelievable", "shocking", "never knew", "acha",
                "arre", "enthi", "ayyo", "oh my god"
            ],
            "love": [
                "love you", "miss you", "care", "heart", "darling",
                "dear", "sweetheart", "prema", "ishq", "pyaar"
            ],
            "confusion": [
                "confused", "don't understand", "what do you mean",
                "unclear", "explain", "how", "why", "entho",
                "artham kaledhu", "samajh nahi"
            ],
            "excitement": [
                "excited", "can't wait", "looking forward",
                "thrilled", "pumped", "eager", "ready", "let's go"
            ]
        }

        text_lower = text.lower()
        emotion_scores = {}

        for emotion, keywords in emotion_maps.items():
            score = sum(
                1 for kw in keywords if kw in text_lower
            )
            if score > 0:
                emotion_scores[emotion] = score

        if emotion_scores:
            detected = max(emotion_scores, key=emotion_scores.get)
            logger.debug(f"Emotion detected: {detected}")
            return detected

        return "neutral"

    async def _deep_understand(
        self, text: str, emotion: str
    ) -> str:
        """Deep semantic understanding of what user truly means"""
        if 'ai' not in self.modules:
            return text

        understanding_prompt = f"""You are a deep understanding engine.
Analyze this message and extract:
1. Literal meaning (what they said)
2. True intent (what they really want)
3. Emotional context (they feel: {emotion})
4. Any cultural nuances
5. What would be the PERFECT response focus

Message: "{text}"

Respond in JSON:
{{
  "literal": "what was literally said",
  "true_intent": "what they really need",
  "emotional_context": "their emotional state and needs",
  "cultural_notes": "any cultural context",
  "response_focus": "what the response should focus on"
}}"""

        try:
            result = await self.modules['ai'].generate(
                understanding_prompt,
                max_tokens=300,
                temperature=0.3
            )
            data = json.loads(result)
            return data.get('true_intent', text)
        except:
            return text

    async def _detect_language(self, text: str):
        """Detect language and dialect"""
        if 'language' in self.modules:
            return await self.modules['language'].detect(text)
        return "english", "general"

    async def _classify_intent(
        self, text: str, understood: str
    ) -> str:
        """Classify user intent with high accuracy"""
        if 'intent' in self.modules:
            # We already have IntentEngine loaded in modules
            intent_result = await self.modules['intent'].classify(text, understood)
            return intent_result.primary_intent

        # Fallback classification
        text_lower = text.lower()
        if any(w in text_lower for w in [
            "?", "what", "how", "why", "when", "where", "who",
            "enti", "ela", "enduku", "kya", "kyun", "kaise"
        ]):
            return "question"
        elif any(w in text_lower for w in [
            "create", "make", "build", "write", "generate",
            "banao", "likho", "create cheyyi"
        ]):
            return "creation"
        elif any(w in text_lower for w in [
            "search", "find", "look up", "research", "check",
            "dhundho", "search cheyyi", "find out"
        ]):
            return "research"
        elif any(w in text_lower for w in [
            "do", "run", "execute", "open", "close", "play",
            "karo", "cheyyi", "open cheyyi"
        ]):
            return "action"
        elif any(w in text_lower for w in [
            "remember", "recall", "forgot", "memory", "earlier",
            "last time", "previously", "yesterday"
        ]):
            return "memory_recall"
        elif any(w in text_lower for w in [
            "feel", "sad", "happy", "angry", "scared", "lonely",
            "help me", "support", "listen"
        ]):
            return "emotional_support"
        return "conversation"

    async def _recall_memories(
        self, text: str, intent: str
    ) -> List:
        """Recall relevant memories like a human"""
        if 'memory' not in self.modules:
            return []
        try:
            memories = await self.modules['memory'].recall(
                query=text,
                intent=intent,
                limit=5
            )
            return memories or []
        except Exception as e:
            logger.error(f"Memory recall error: {e}")
            return []

    async def _create_plan(
        self,
        understood: str,
        intent: str,
        memories: List,
        context: Dict
    ) -> List[str]:
        """Create multi-step plan like a human thinks"""
        plan = []

        intent_plans = {
            "question": [
                "search_memories",
                "search_knowledge",
                "formulate_answer",
                "add_examples"
            ],
            "creation": [
                "understand_requirements",
                "plan_structure",
                "generate_content",
                "review_quality"
            ],
            "research": [
                "search_web",
                "search_memories",
                "synthesize_info",
                "present_findings"
            ],
            "action": [
                "identify_tool",
                "prepare_parameters",
                "execute_safely",
                "confirm_result"
            ],
            "emotional_support": [
                "acknowledge_emotion",
                "show_empathy",
                "offer_support",
                "suggest_help"
            ],
            "memory_recall": [
                "search_episodic_memory",
                "search_semantic_memory",
                "reconstruct_context",
                "present_memory"
            ],
            "conversation": [
                "understand_topic",
                "recall_context",
                "formulate_natural_reply",
                "add_personality"
            ]
        }

        plan = intent_plans.get(intent, ["understand", "respond"])
        return plan

    async def _use_tools(
        self, tools_needed: List[str]
    ) -> Dict[str, Any]:
        """Use tools like human hands"""
        if 'tools' not in self.modules:
            return {}

        results = {}
        for tool_name in tools_needed:
            try:
                # Assuming tools module has a use method
                if hasattr(self.modules['tools'], 'use'):
                    result = await self.modules['tools'].use(tool_name)
                    results[tool_name] = result
                    logger.info(f"🔧 Tool '{tool_name}' used successfully")
            except Exception as e:
                logger.error(f"Tool error '{tool_name}': {e}")
                results[tool_name] = {"error": str(e)}

        return results

    async def _generate_response(
        self,
        thought: Thought,
        tool_results: Dict,
        context: Dict
    ) -> str:
        """Generate human-like response using LLM"""
        if 'ai' not in self.modules:
            return "I'm thinking... please wait."

        # Build memory context
        memory_context = ""
        if thought.memories_recalled:
            memory_context = "What I remember:\n"
            for m in thought.memories_recalled[:3]:
                if isinstance(m, dict):
                    memory_context += f"- {m.get('content', '')[:100]}\n"
                else:
                    memory_context += f"- {str(m)[:100]}\n"

        # Build tool context
        tool_context = ""
        if tool_results:
            tool_context = "Tool results:\n"
            for tool, result in tool_results.items():
                tool_context += f"- {tool}: {str(result)[:200]}\n"

        # Build conversation history
        conv_history = ""
        if self.conversation_context[-10:]:
            conv_history = "Recent conversation:\n"
            for turn in self.conversation_context[-6:]:
                role = turn.get('role', 'unknown')
                content = turn.get('content', '')[:100]
                conv_history += f"{role}: {content}\n"

        # Load persona
        persona_text = self._load_persona()

        # Master prompt - this is what makes it human
        master_prompt = f"""{persona_text}

You are NEXUS-X OMEGA - an extremely intelligent, emotionally aware AI assistant.
You think and respond EXACTLY like a smart human friend would.

RULES FOR HUMAN-LIKE RESPONSES:
1. Be natural - not robotic or formal unless needed
2. Match the user's energy and emotion
3. Show genuine understanding and empathy
4. Be direct and clear - no unnecessary padding
5. Use the detected language/dialect naturally
6. Remember context from conversation history
7. Be concise but complete
8. Show personality - wit, warmth, intelligence
9. Never say "As an AI" or "I cannot"
10. Always find a way to help

CURRENT CONTEXT:
- User's emotion: {thought.emotion_detected}
- Intent: {thought.intent}
- Language: {thought.language} ({thought.dialect})
- True meaning: {thought.understood_meaning}

{memory_context}
{tool_context}
{conv_history}

USER SAYS: "{thought.raw_input}"

Respond naturally, intelligently, and helpfully:"""

        response = await self.modules['ai'].generate(
            master_prompt,
            max_tokens=600,
            temperature=0.8
        )

        # Set response emotion
        thought.emotion_to_express = self._choose_response_emotion(
            thought.emotion_detected, thought.intent
        )

        return response.strip()

    def _choose_response_emotion(
        self, detected: str, intent: str
    ) -> str:
        """Choose appropriate response emotion"""
        emotion_map = {
            "joy": "happy",
            "sadness": "empathetic",
            "anger": "calm_understanding",
            "fear": "reassuring",
            "surprise": "engaged",
            "love": "warm",
            "confusion": "helpful_clear",
            "excitement": "enthusiastic",
            "neutral": "friendly"
        }
        return emotion_map.get(detected, "friendly")

    async def _stylize_response(
        self,
        response: str,
        language: str,
        dialect: str,
        emotion: str
    ) -> str:
        """Stylize response to match language and emotion"""
        if 'language' in self.modules:
            if hasattr(self.modules['language'], 'stylize'):
                return await self.modules['language'].stylize(
                    response, language, dialect, emotion
                )
        return response

    async def _quality_check(
        self, response: str, original_input: str
    ) -> str:
        """Quality check - make sure response is good"""
        if not response or len(response.strip()) < 2:
            return "I understand what you're saying. Let me think about this more carefully and get back to you."

        # Remove any AI-isms
        bad_phrases = [
            "As an AI language model",
            "As an AI assistant",
            "I cannot", "I am unable",
            "I don't have the ability",
            "I'm just an AI",
            "As a large language model"
        ]
        for phrase in bad_phrases:
            if phrase.lower() in response.lower():
                response = response.replace(phrase, "")

        # Ensure not too long
        if len(response) > 2000:
            response = response[:2000] + "..."

        return response.strip()

    async def _learn_from_thought(
        self, thought: Thought, sender: str
    ):
        """Learn from every interaction"""
        if 'memory' not in self.modules:
            return

        # Store the conversation
        await self.modules['memory'].store({
            "type": "conversation",
            "sender": sender,
            "input": thought.raw_input,
            "understood": thought.understood_meaning,
            "intent": thought.intent,
            "emotion": thought.emotion_detected,
            "response": thought.response_text,
            "confidence": thought.confidence,
            "timestamp": thought.timestamp,
            "language": thought.language
        })

        # Extract and store facts if any
        if thought.confidence > 0.7:
            await self._extract_and_store_facts(thought)

    async def _extract_and_store_facts(self, thought: Thought):
        """Extract learnable facts from the conversation"""
        if 'ai' not in self.modules:
            return

        fact_prompt = f"""Extract any important facts or information 
from this conversation that should be remembered long-term.

User said: "{thought.raw_input}"
Response: "{thought.response_text[:200]}"

Return JSON array of facts (empty array if none):
[{{"fact": "...", "category": "person/place/preference/knowledge"}}]"""

        try:
            result = await self.modules['ai'].generate(
                fact_prompt, max_tokens=200, temperature=0.2
            )
            facts = json.loads(result)
            for fact_data in facts:
                if hasattr(self.modules['memory'], 'store_fact'):
                    await self.modules['memory'].store_fact(fact_data)
        except:
            pass  # Facts extraction is best-effort

    def _calculate_confidence(self, thought: Thought) -> float:
        """Calculate confidence in the response"""
        score = 0.5

        if thought.understood_meaning != thought.raw_input:
            score += 0.1  # Deep understanding achieved
        if thought.memories_recalled:
            score += 0.1  # Memory backed
        if thought.intent != "conversation":
            score += 0.1  # Clear intent
        if len(thought.response_text) > 50:
            score += 0.1  # Substantial response
        if thought.emotion_detected != "neutral":
            score += 0.1  # Emotional awareness

        return min(1.0, score)

    def _load_persona(self) -> str:
        """Load persona configuration"""
        try:
            with open("config/persona_core.json", "r") as f:
                persona = json.load(f)
                return persona.get("system_prompt", "")
        except:
            return "You are NEXUS-X, an intelligent AI assistant."

    def _get_error_response(self, language: str) -> str:
        """Get appropriate error response"""
        responses = {
            "telugu": "Sorry, naku oka chinna problem vasindi. Meeru malli try cheyyandi!",
            "hindi": "Maafi karo, mujhe ek chhoti problem aayi. Phir se try karo!",
            "english": "I had a small hiccup but I'm healing myself. Please try again!"
        }
        return responses.get(language, responses["english"])

    async def _idle_thinking(self):
        """Think proactively when idle"""
        # Background tasks during idle
        await asyncio.sleep(5)

    async def _self_heal(self, error: str):
        """Self-heal when errors occur"""
        self.state = ThinkingState.HEALING
        self.daily_stats["errors_healed"] += 1
        logger.info(f"🔧 Self-healing from: {error[:100]}")

        if 'healer' in self.modules:
            await self.modules['healer'].heal(error)

        self.state = ThinkingState.IDLE
