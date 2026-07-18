"""
NEXUS-X OMEGA Unified Intent Engine
Merges ARION + JARVIS-X intent detection
Deep multi-dimensional intent classification
"""

import asyncio
import json
import logging
import re
from typing import Dict, Tuple, List, Optional
from dataclasses import dataclass

logger = logging.getLogger('IntentEngine')


@dataclass
class IntentResult:
    primary_intent: str
    sub_intent: str
    emotion: str
    dialect: str
    language: str
    urgency: float
    confidence: float
    requires_tools: List[str]
    response_style: str
    is_question: bool
    is_command: bool
    is_emotional: bool


class IntentEngine:
    """
    Deep intent classification engine
    Understands what humans REALLY mean
    """

    def __init__(self):
        self.intent_patterns = self._load_intent_patterns()
        # Pre-compile intent patterns for performance
        for intent_data in self.intent_patterns.values():
            intent_data["compiled"] = [re.compile(p) for p in intent_data["patterns"]]

        self.emotion_patterns = self._load_emotion_patterns()
        # Pre-compile emotion markers for fast checking
        self.compiled_emotion_check = {
            emotion: re.compile("|".join(re.escape(k) for k in keywords))
            for emotion, keywords in self.emotion_patterns.items() if keywords
        }

        self.tool_triggers = self._load_tool_triggers()

        # Pre-compile tool triggers
        self.compiled_tool_triggers = {
            tool: re.compile("|".join(re.escape(t) for t in triggers))
            for tool, triggers in self.tool_triggers.items() if triggers
        }

        # Pre-compile structural patterns
        self._RE_QUESTION = re.compile(r'\?$|^(what|who|where|when|why|how|is|are|do|does|can|will)')
        self._RE_COMMAND = re.compile(r'^(open|close|run|create|make|delete|search|find|play|stop)')

        # Pre-cache language markers
        self.telugu_markers = [
            "enti", "ela", "evaru", "ekkada", "avunu",
            "ledu", "cheyyi", "annav", "unnav", "gurtunda",
            "kastam", "sare", "nakku", "meeru", "nuvvu"
        ]
        self.hindi_markers = [
            "kya", "hai", "hain", "karo", "mujhe", "tumhe",
            "kyun", "kaise", "yaar", "bhai", "acha", "theek",
            "nahi", "bilkul", "zaroor", "haan"
        ]
        self.tenglish_markers = [
            "bro", "da", "ra", "ga", "le", "enti bro",
            "chala", "bagundi", "chudu"
        ]

        # Pre-compile language markers for fast checking
        self.compiled_telugu_check = re.compile("|".join(re.escape(m) for m in self.telugu_markers))
        self.compiled_hindi_check = re.compile("|".join(re.escape(m) for m in self.hindi_markers))
        self.compiled_tenglish_check = re.compile("|".join(re.escape(m) for m in self.tenglish_markers))

        logger.info("🎯 Intent Engine initialized")

    def _load_intent_patterns(self) -> Dict:
        return {
            # Information seeking
            "question_factual": {
                "patterns": [
                    r"\bwhat is\b", r"\bwho is\b", r"\bwhere is\b",
                    r"\bwhen did\b", r"\bwhich\b", r"\bdefine\b",
                    r"\btell me about\b", r"\bexplain\b",
                    r"\benti\b", r"\bevaru\b", r"\bekkada\b",
                    r"\bkya hai\b", r"\bkaun hai\b"
                ],
                "response_style": "informative",
                "tools": []
            },
            "question_howto": {
                "patterns": [
                    r"\bhow (do|to|can|should)\b",
                    r"\bsteps to\b", r"\bguide\b",
                    r"\btutorial\b", r"\blearn\b",
                    r"\bela cheyali\b", r"\bkaise karna\b"
                ],
                "response_style": "instructional",
                "tools": ["search"]
            },
            "question_opinion": {
                "patterns": [
                    r"\bwhat do you think\b", r"\byour opinion\b",
                    r"\bdo you (like|prefer|think)\b",
                    r"\bbetter\b.*\bor\b", r"\bshould i\b"
                ],
                "response_style": "opinionated_friendly",
                "tools": []
            },

            # Creation & Generation
            "create_code": {
                "patterns": [
                    r"\bwrite (a |the |some |)code\b",
                    r"\bcreate (a |)(function|class|script|program)\b",
                    r"\bcode (for|to)\b", r"\bprogram\b",
                    r"\bdebug\b", r"\bfix (the |my |)(code|bug|error)\b",
                    r"\bimplement\b"
                ],
                "response_style": "technical_precise",
                "tools": ["code_gen", "search"]
            },
            "create_text": {
                "patterns": [
                    r"\bwrite (a |)(letter|email|essay|story|poem)\b",
                    r"\bdraft\b", r"\bcompose\b", r"\bgenerate text\b",
                    r"\bcreate content\b", r"\bwrite about\b"
                ],
                "response_style": "creative",
                "tools": ["write"]
            },
            "create_plan": {
                "patterns": [
                    r"\bplan\b", r"\bschedule\b", r"\borgani[sz]e\b",
                    r"\bstrategy\b", r"\broadmap\b",
                    r"\bhelp me (plan|organize)\b"
                ],
                "response_style": "structured",
                "tools": ["calendar", "write"]
            },

            # Research & Search
            "research": {
                "patterns": [
                    r"\bsearch\b", r"\bfind\b", r"\blook up\b",
                    r"\bresearch\b", r"\bnews\b", r"\blatest\b",
                    r"\bcurrent\b", r"\btoday\b",
                    r"\bdhundho\b", r"\bchedu\b", r"\bsearch cheyyi\b"
                ],
                "response_style": "factual_cited",
                "tools": ["search", "news"]
            },

            # System Actions
            "action_system": {
                "patterns": [
                    r"\bopen\b", r"\bclose\b", r"\brun\b",
                    r"\blaunch\b", r"\bstart\b", r"\bstop\b",
                    r"\bexecute\b", r"\binstall\b",
                    r"\bopen cheyyi\b", r"\bband karo\b"
                ],
                "response_style": "confirmational",
                "tools": ["os_control", "automation"]
            },
            "action_file": {
                "patterns": [
                    r"\b(create|make|delete|move|copy) (a |)(file|folder)\b",
                    r"\bsave\b", r"\bread (the |)(file|document)\b",
                    r"\bdownload\b", r"\bupload\b"
                ],
                "response_style": "confirmational",
                "tools": ["file_ops"]
            },
            "action_web": {
                "patterns": [
                    r"\bbrowse\b", r"\bgo to\b", r"\bvisit\b",
                    r"\bwebsite\b", r"\burl\b", r"\bclick\b",
                    r"\bform\b", r"\bfill\b"
                ],
                "response_style": "confirmational",
                "tools": ["browser"]
            },

            # Memory & Personal
            "memory_recall": {
                "patterns": [
                    r"\bdo you remember\b", r"\bwhat did (i|we) say\b",
                    r"\blast time\b", r"\bpreviously\b",
                    r"\byou (said|told)\b", r"\brecall\b",
                    r"\bgurtunda\b", r"\byaad hai\b"
                ],
                "response_style": "personal_warm",
                "tools": ["memory_search"]
            },
            "personal_info": {
                "patterns": [
                    r"\bmy (name|age|birthday|phone)\b",
                    r"\bremember (that|this|my)\b",
                    r"\bsave (this|that)\b", r"\bnote (that|this)\b",
                    r"\bi (am|like|prefer|hate|love|want)\b"
                ],
                "response_style": "personal_warm",
                "tools": ["memory_store"]
            },

            # Emotional Support
            "emotional_support": {
                "patterns": [
                    r"\bi (feel|am feeling|felt)\b",
                    r"\bi('m| am) (sad|depressed|angry|worried|scared)\b",
                    r"\bnobody (cares|understands)\b",
                    r"\bhelp me (feel|cope)\b",
                    r"\blisten to me\b", r"\bi need (support|help)\b",
                    r"\bdukha\b", r"\bbure feel\b", r"\btension\b"
                ],
                "response_style": "empathetic_warm",
                "tools": []
            },
            "casual_chat": {
                "patterns": [
                    r"\bhey\b", r"\bhello\b", r"\bhi\b",
                    r"\bsup\b", r"\bwassup\b", r"\bhow are you\b",
                    r"\bela unnav\b", r"\bkya haal\b"
                ],
                "response_style": "casual_friendly",
                "tools": []
            },

            # Math & Logic
            "math_calc": {
                "patterns": [
                    r"\bcalculate\b", r"\bsolve\b", r"\bmath\b",
                    r"\b\d+\s*[\+\-\*\/]\s*\d+\b",
                    r"\bpercentage\b", r"\bconvert\b"
                ],
                "response_style": "precise",
                "tools": ["calculator"]
            },

            # Time & Calendar
            "time_calendar": {
                "patterns": [
                    r"\bwhat time\b", r"\bwhat date\b",
                    r"\bschedule\b", r"\bmeeting\b",
                    r"\bremind(er)?\b", r"\balarm\b",
                    r"\btomorrow\b", r"\btoday\b"
                ],
                "response_style": "precise",
                "tools": ["calendar", "clock"]
            }
        }

    def _load_emotion_patterns(self) -> Dict:
        return {
            "joy": [
                "haha", "lol", "happy", "great", "awesome",
                "love", "wonderful", "excited", "yay",
                "😊", "😄", "❤️", "🎉",
                "khushi", "mast", "badhiya", "chala bagundi"
            ],
            "sadness": [
                "sad", "cry", "tears", "depressed", "lonely",
                "hopeless", "miss you", "hurt", "heartbreak",
                "😢", "😭", "💔",
                "dukha", "kastam", "bada bura", "rona"
            ],
            "anger": [
                "angry", "furious", "hate", "frustrated",
                "annoyed", "rage", "worst", "terrible",
                "😠", "😡",
                "gussa", "kopa", "chala frustrated"
            ],
            "fear": [
                "scared", "afraid", "worried", "anxious",
                "nervous", "panic", "stress", "terror",
                "😨", "😰",
                "bhaya", "darr", "tension ga", "worry"
            ],
            "surprise": [
                "wow", "omg", "really", "no way", "seriously",
                "unbelievable", "shocked", "whoa",
                "😮", "😲",
                "arre", "enthi", "ayyo", "acha"
            ],
            "love": [
                "love you", "miss you", "darling", "sweetheart",
                "care", "precious", "my dear",
                "❤️", "🥰", "😍",
                "prema", "pyaar", "ishq"
            ],
            "disgust": [
                "disgusting", "gross", "eww", "yuck",
                "horrible", "nasty", "awful",
                "🤢", "🤮"
            ],
            "neutral": []
        }

    def _load_tool_triggers(self) -> Dict:
        return {
            "search": [
                "search", "find", "look up", "google",
                "research", "news", "dhundho"
            ],
            "calculator": [
                "calculate", "compute", "math", "solve",
                "+", "-", "*", "/", "percent"
            ],
            "file_ops": [
                "file", "folder", "directory", "save",
                "read", "write", "delete", "create"
            ],
            "os_control": [
                "open", "close", "run", "launch",
                "start", "stop", "install", "execute"
            ],
            "browser": [
                "browse", "website", "url", "http",
                "click", "form", "webpage"
            ],
            "calendar": [
                "schedule", "meeting", "reminder",
                "alarm", "event", "tomorrow", "appointment"
            ],
            "memory_search": [
                "remember", "recall", "earlier", "previously",
                "last time", "gurtunda", "yaad"
            ]
        }

    async def classify(
        self,
        text: str,
        understood: str = None
    ) -> IntentResult:
        """
        Full intent classification
        Returns comprehensive IntentResult
        """
        text_lower = text.lower()
        analyze_text = (understood or text).lower()

        # Detect primary intent using pre-compiled patterns
        intent_scores: Dict[str, float] = {}
        for intent_name, intent_data in self.intent_patterns.items():
            score = 0.0
            for cp in intent_data["compiled"]:
                if cp.search(text_lower):
                    score += 1.0
            if score > 0:
                intent_scores[intent_name] = score

        # Get best intent
        if intent_scores:
            primary_intent = max(
                intent_scores, key=intent_scores.get
            )
            confidence = min(
                intent_scores[primary_intent] / 3.0, 1.0
            )
        else:
            primary_intent = "casual_chat"
            confidence = 0.5

        intent_data = self.intent_patterns.get(primary_intent, {})

        # Detect emotion
        emotion = self._detect_emotion(text_lower)

        # Detect language and dialect
        language, dialect = self._detect_language(text_lower)

        # Calculate urgency
        urgency = self._calculate_urgency(text_lower, emotion)

        # Get required tools
        tools = intent_data.get("tools", [])
        tools += self._detect_additional_tools(text_lower)
        tools = list(set(tools))  # Deduplicate

        # Classify structural type using pre-compiled patterns
        is_question = bool(self._RE_QUESTION.search(text_lower))
        is_command = bool(self._RE_COMMAND.search(text_lower))
        is_emotional = emotion not in ["neutral"]

        return IntentResult(
            primary_intent=primary_intent,
            sub_intent=self._get_sub_intent(text_lower, primary_intent),
            emotion=emotion,
            dialect=dialect,
            language=language,
            urgency=urgency,
            confidence=confidence,
            requires_tools=tools,
            response_style=intent_data.get("response_style", "casual_friendly"),
            is_question=is_question,
            is_command=is_command,
            is_emotional=is_emotional
        )

    def _detect_emotion(self, text: str) -> str:
        """Detect dominant emotion"""
        scores: Dict[str, int] = {}
        for emotion, keywords in self.emotion_patterns.items():
            # Fast check if any keyword from this emotion is present
            if emotion in self.compiled_emotion_check and not self.compiled_emotion_check[emotion].search(text):
                continue

            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                scores[emotion] = score
        if scores:
            return max(scores, key=scores.get)
        return "neutral"

    def _detect_language(self, text: str) -> Tuple[str, str]:
        """Detect language and dialect"""
        tel_score = sum(1 for m in self.telugu_markers if m in text) if self.compiled_telugu_check.search(text) else 0
        hin_score = sum(1 for m in self.hindi_markers if m in text) if self.compiled_hindi_check.search(text) else 0
        ten_score = sum(1 for m in self.tenglish_markers if m in text) if self.compiled_tenglish_check.search(text) else 0

        if ten_score > 0 and tel_score > 0:
            return "telugu", "tenglish"
        elif tel_score > hin_score and tel_score >= 2:
            return "telugu", "formal"
        elif hin_score > tel_score and hin_score >= 2:
            return "hindi", "formal"
        elif hin_score >= 1 or tel_score >= 1:
            return "english", "mixed"
        return "english", "general"

    def _calculate_urgency(self, text: str, emotion: str) -> float:
        """Calculate how urgent the request is"""
        urgency = 0.5
        urgent_words = [
            "urgent", "emergency", "asap", "immediately",
            "right now", "help", "please", "critical"
        ]
        if any(w in text for w in urgent_words):
            urgency += 0.3
        if emotion in ["fear", "anger", "sadness"]:
            urgency += 0.2
        if "!" in text:
            urgency += 0.1
        return min(1.0, urgency)

    def _get_sub_intent(self, text: str, primary: str) -> str:
        """Get more specific sub-intent"""
        sub_intents = {
            "create_code": {
                "fix": ["fix", "debug", "error", "bug"],
                "generate": ["write", "create", "generate"],
                "explain": ["explain", "how does", "what does"]
            },
            "research": {
                "news": ["news", "latest", "current"],
                "fact": ["fact", "true", "real", "actual"],
                "comparison": ["vs", "versus", "compare", "difference"]
            }
        }
        subs = sub_intents.get(primary, {})
        for sub, keywords in subs.items():
            if any(kw in text for kw in keywords):
                return sub
        return "general"

    def _detect_additional_tools(self, text: str) -> List[str]:
        """Detect additional tools needed using pre-compiled triggers"""
        needed = []
        for tool, pattern in self.compiled_tool_triggers.items():
            if pattern.search(text):
                needed.append(tool)
        return needed
