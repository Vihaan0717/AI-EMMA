import json
import asyncio
from typing import Dict, Any, Tuple
import re
from rapidfuzz import process, fuzz
from core.base_agent import BaseAgent
from core.message_bus import Channel, Message

try:
    from lingua import Language, LanguageDetectorBuilder
except ImportError:
    LanguageDetectorBuilder = None
    Language = None

try:
    import argostranslate.translate
except ImportError:
    argostranslate = None

class LanguageEngine(BaseAgent):
    PROTECTED_ENGLISH = {
        # Time words
        "earlier", "later", "before", "after", "now", "then",
        "today", "tomorrow", "yesterday", "morning", "evening",
        "night", "week", "month", "year", "time", "hour", "minute",
        
        # Common verbs
        "remember", "forget", "know", "think", "feel", "want",
        "need", "have", "had", "has", "been", "was", "were",
        "sent", "send", "get", "got", "go", "went", "come",
        "came", "see", "saw", "say", "said", "tell", "told",
        "do", "did", "does", "done", "doing",
        
        # Question words
        "what", "when", "where", "who", "why", "how", "which",
        
        # Common adjectives/adverbs
        "good", "bad", "nice", "great", "okay", "fine", "really",
        "very", "just", "only", "already", "still", "again",
        
        # Pronouns
        "you", "your", "mine", "ours", "they", "them", "their",
        "this", "that", "these", "those", "us", "me", "he", "she", "it", "my", "we",
        
        # Conjunctions/prepositions  
        "and", "but", "or", "so", "because", "while",
        "the", "a", "an", "in", "on", "at", "to", "for",
        "with", "from", "about", "into", "through", "by", "if", "as", "is", "are"
    }

    def __init__(self):
        super().__init__("LanguageEngine", [Channel.LANGUAGE])
        self.detector = None
        self.Language = None
        self.vocab_te = self._load_json("arion/config/vocabulary_telugu.json")
        self.vocab_hi = self._load_json("arion/config/vocabulary_hindi.json")
        self._te_words = self._flatten_vocab(self.vocab_te)
        self._hi_words = self._flatten_vocab(self.vocab_hi)

    def _flatten_vocab(self, vocab: dict) -> list:
        words = []
        for cat, entries in vocab.items():
            if cat == "meta": continue
            if isinstance(entries, dict):
                words.extend(entries.keys())
        return words

    def _load_json(self, path: str) -> dict:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    async def run_loop(self):
        # Deferred initialization
        if LanguageDetectorBuilder and not self.detector:
            print("[LanguageEngine] Initializing Language Detector...")
            self.Language = Language
            self.detector = LanguageDetectorBuilder.from_languages(
                Language.ENGLISH, Language.HINDI, Language.TELUGU
            ).build()
            print("[LanguageEngine] Language Detector Ready.")

        while self.running:
            msg = await self.get_next_message(timeout=1.0)
            if msg:
                await self.handle_message(msg)

    async def handle_message(self, message: Message):
        if message.action == "detect_language":
            text = message.payload.get("text", "")
            lang = self._detect(text)
            if message.requires_response:
                await self.respond_to(message, "language_detected", {"language": lang})
                
        elif message.action == "normalize_script":
            text = message.payload.get("text", "")
            normalized_data = self._normalize_script(text)
            if message.requires_response:
                await self.respond_to(message, "script_normalized", normalized_data)
                
        elif message.action == "stylize_dialect":
            text = message.payload.get("text", "")
            dialect = message.payload.get("dialect", "general")
            emotion = message.payload.get("emotion", "neutral")
            
            stylized = self._stylize_dialect(text, dialect, emotion)
            
            if message.requires_response:
                await self.respond_to(message, "dialect_stylized", {"stylized_text": stylized})
                
        elif message.action == "translate_to_english":
            text = message.payload.get("text", "")
            source_lang = message.payload.get("source_lang", "auto")
            if source_lang == "auto":
                source_lang = self._detect(text)
            
            translated = await self._translate(text, source_lang, "en")
            if message.requires_response:
                await self.respond_to(message, "translated_text", {"text": translated, "source_lang": source_lang})
                
        elif message.action == "culturalize":
            # Takes english text and injects cultural slang based on target lang/dialect/religion
            # For simplicity, we just pass it through in this mockup, maybe with slight appends
            text = message.payload.get("text", "")
            target_lang = message.payload.get("target_lang", "en")
            
            culturalized = text # Mock implementation
            if message.requires_response:
                await self.respond_to(message, "culturalized_text", {"text": culturalized})

    def _detect(self, text: str) -> str:
        if not self.detector: return "en"
        lang = self.detector.detect_language_of(text)
        if lang == Language.TELUGU: return "te"
        return "en"

    TELUGU_PHRASES = {
        "yala vunnaru":         "yala_vunnaru",
        "yala vundhe":          "yala_vundhe", 
        "yala unnav":           "yala_unnav",
        "ela vunnaru":          "yala_vunnaru",
        "ela vundhe":           "yala_vundhe",
        "ela unnav":            "yala_unnav",
        "ame chasthunav":       "em_chesthunnav",
        "ame chesthunnav":      "em_chesthunnav",
        "em chasthunav":        "em_chesthunnav",
        "em chesthunnav":       "em_chesthunnav",
        "ippudu em":            "ippudu_em",
        "okay ga":              "okay_ga",
        "bore ga":              "bore_ga",
        "happy ga":             "happy_ga",
        "sad ga":               "sad_ga",
    }

    HINDI_PHRASES = {
        "kya kar raha":         "kya_kar_raha",
        "kya chal raha":        "kya_chal_raha",
        "kaise ho":             "kaise_ho",
        "theek hai":            "theek_hai",
    }

    def _normalize_script(self, text: str) -> dict:
        """
        Agent 1: Normalizer.
        Takes messy Romanized text and fuzzy-matches against canonical dictionaries.
        Fixed: No duplicate tokens. Priority for multi-word phrases.
        """
        text_lower = text.lower()
        te_score = 0
        hi_score = 0
        extracted_phrases = []
        
        # ── Step 1: Extract known phrases FIRST ─────────────────────────────
        working_text = text_lower
        
        for phrase, canonical in self.TELUGU_PHRASES.items():
            if phrase in working_text:
                extracted_phrases.append(canonical)
                working_text = working_text.replace(phrase, " ")
                te_score += 2  # Phrase match = stronger signal
        
        for phrase, canonical in self.HINDI_PHRASES.items():
            if phrase in working_text:
                extracted_phrases.append(canonical)
                working_text = working_text.replace(phrase, " ")
                hi_score += 2
        
        # ── Step 2: Tokenize remaining words ────────────────────────────────
        remaining_words = re.findall(r'\b\w+\b', working_text)
        seen = set()
        word_tokens = []
        
        for w in remaining_words:
            if w in seen:
                continue
            seen.add(w)
            
            # ── Step 2.1: Skip single/double chars ───────────────────────────
            # Never fuzzy match very short tokens
            if len(w) <= 2:
                word_tokens.append(w)
                if w in self._te_words: te_score += 0.5
                if w in self._hi_words: hi_score += 0.5
                continue
            
            # ── Step 2.2: Skip protected English words ───────────────────────
            if w in self.PROTECTED_ENGLISH:
                word_tokens.append(w)
                continue
            
            # ── Step 2.3: Skip words with English suffixes ────────────────────
            english_suffixes = (
                "ing", "tion", "ness", "ment", "ful", "less",
                "ous", "ive", "ble", "er", "est", "ed", "ly"
            )
            if (len(w) > 5 and w.endswith(english_suffixes)
                    and w not in self._te_words
                    and w not in self._hi_words):
                word_tokens.append(w)
                continue

            # Exact match
            if w in self._te_words:
                word_tokens.append(w)
                te_score += 1
                continue
            if w in self._hi_words:
                word_tokens.append(w)
                hi_score += 1
                continue
            
            # Fuzzy match — only for longer words (5+ chars)
            if len(w) >= 5:
                te_match = process.extractOne(
                    w,
                    [v for v in self._te_words if ' ' not in v and len(v) >= 4],
                    scorer=fuzz.WRatio
                )
                hi_match = process.extractOne(
                    w,
                    [v for v in self._hi_words if ' ' not in v and len(v) >= 4],
                    scorer=fuzz.WRatio
                )
                
                best_match = None
                best_score = 0
                is_te = False
                
                FUZZY_THRESHOLD = 80
                if te_match and te_match[1] >= FUZZY_THRESHOLD:
                    best_match = te_match[0]
                    best_score = te_match[1]
                    is_te = True
                
                if (hi_match and hi_match[1] >= FUZZY_THRESHOLD
                        and hi_match[1] > best_score):
                    best_match = hi_match[0]
                    best_score = hi_match[1]
                    is_te = False
                
                if best_match:
                    word_tokens.append(best_match)
                    if is_te: te_score += 1
                    else: hi_score += 1
                    print(f"[LanguageEngine] Fuzzy: '{w}' -> '{best_match}' ({best_score:.0f}%)", flush=True)
                    continue
            
            # Unknown word — keep as-is
            word_tokens.append(w)
        
        # ── Step 3: Combine phrase tokens + word tokens ──────────────────────
        all_tokens = extracted_phrases + word_tokens
        
        script = "general"
        if te_score > hi_score and te_score > 0:
            script = "romanized_telugu"
        elif hi_score > te_score and hi_score > 0:
            script = "romanized_hindi"
        
        total = max(len(all_tokens), 1)
        matched = te_score + hi_score
        confidence = round(min(matched / total, 1.0), 2)
        
        result = {
            "cleaned": " ".join(all_tokens),
            "script": script,
            "confidence": confidence,
            "tokens": all_tokens
        }
        
        print(f"[LanguageEngine] Normalized: '{text}' -> '{result['cleaned']}' | script={script} | tokens={all_tokens} | conf={confidence}", flush=True)
        return result

    GODAVARI_STYLIZATION = {
        # ── Questions ─────────────────────────────────────────────────
        "what are you doing":        "em chesthunnav",
        "what are you doing now":    "ippudu em chesthunnav",
        "what's going on":           "em scene",
        "what happened":             "em ayyindhi",
        "what's up":                 "em chesthunnav",
        "how are you":               "ela unnav",
        "are you okay":              "okay ga unnava",
        "how is your mother":        "amma ela vundhi",
        "how is mom":                "amma ela vundhi",
        "how is your sister":        "chelli ela vundhi",
        "how is your younger sister":"chelli ela vundhi",
        "how is your older sister":  "akka ela vundhi",
        "how is your father":        "nanna ela vunnaru",
        "how is your family":        "family ela vunnaru",
        "how is your health":        "health ela vundhi",
        "are they okay":             "vallu okay ga unnaraa",
        "is she okay":               "aye okay ga undha",
        "is he okay":                "aayana okay ga unnara",
        
        # ── Answers / Statements ──────────────────────────────────────
        "i don't know":              "naaku thelidu",
        "i don't know man":          "naaku thelidu ra",
        "you tell me":               "nuvve cheppu",
        "tell me":                   "cheppu",
        "nothing much":              "emi ledu",
        "nothing":                   "emi ledu",
        "i'm good":                  "nenu okay ga unna",
        "i'm tired":                 "tired ga unna",
        "i'm bored":                 "bore ga undi",
        "i'm busy":                  "busy ga unna",
        "i'm sleeping":              "padukuntunna",
        "let's go":                  "paddam ra",
        "that's crazy":              "scene ra adhi",
        "seriously":                 "seriousgaa?",
        "no way":                    "ledu ra",
        "of course":                 "ayyo obviously",
        "same here":                 "naku kuda same ra",
        "i understand":              "artham ayyindhi",
        "take care":                 "jagratha ra",
        "get well soon":             "twaraga koluko ra",
        
        # ── Fillers & Reactions ───────────────────────────────────────
        "oh wow":                    "arey woww",
        "oh no":                     "arey no ra",
        "that's nice":               "baundhi ra adhi",
        "good for you":              "baundhi ra niku",
        "what to do":                "em cheyyali ra",
        "it happens":                "ayyela untundi",
        "don't worry":               "tension padakku",
        "chill out":                 "chill cheyyira",
        "come on":                   "ra ra ra",
        "okay okay":                 "sare sare",
        "haha":                      "haha 😂",
        "lmao":                      "🤣🤣",
        
        # ── Agreements / Disagreements ────────────────────────────────
        "yeah":                      "avunu ra",
        "yes":                       "avunu",
        "no":                        "ledu",
        "maybe":                     "ayyela untundi",
        "okay":                      "sare ra",
        "alright":                   "sare",
        "understood":                "artham ayyindhi",
        "sure":                      "sare ra okke",

        # ── Common LLM response patterns ──────────────────────────────
        "just chillin":          "ila ey unna",
        "just chilling":         "ila ey unna", 
        "chillin":               "ila ey unna",
        "not much":              "emi ledu",
        "nothing much":          "emi ledu ra",
        "what about you":        "nuvvu cheppu",
        "what about u":          "nuvvu cheppu",
        "how about you":         "nuvvu cheppu",
        "u?":                    "nuvvu?",
        "you?":                  "nuvvu?",
        "tell me":               "cheppu ra",
        "no worries":            "tension padakku ra",
        "that's good":           "baundhi ra",
        "cool":                  "scene ra",
        "goodnight":             "shubharaatri ra",
        "good morning":          "subhodayam ra",
        "bye":                   "sare ra, maatladdam",
    }

    HINDI_STYLIZATION = {
        "what are you doing": "kya kar raha hai",
        "what's up": "kya chal raha hai",
        "nothing": "kuch nahi",
        "going to sleep": "so raha hu",
        "let's go": "chalo yaa",
        "that's crazy": "kya scene hai",
        "I'm bored": "bore ho raha hu",
        "bro": "bhai",
        "okay": "thik hai yaar"
    }

    def _stylize_dialect(self, text: str, dialect: str, emotion: str) -> str:
        """
        Agent 6: Dialect Stylizer
        Reverses Semantic Bridge. Replaces standard English phrases with Dialect.
        Fixed: Longest-match-first logic for accuracy.
        """
        if "telugu" not in dialect.lower() and "hindi" not in dialect.lower():
            return text
            
        map_to_use = self.GODAVARI_STYLIZATION if "telugu" in dialect.lower() else self.HINDI_STYLIZATION
        
        result = text
        text_lower = text.lower()
        
        # ── Sort by length DESC so longer phrases match before sub-phrases ──
        sorted_map = sorted(
            map_to_use.items(), 
            key=lambda x: len(x[0]), 
            reverse=True
        )
        
        # Phrase replacement
        for eng, slang in sorted_map:
            if eng in text_lower:
                # Case insensitive replace using re for safety
                result = re.sub(re.escape(eng), slang, result, flags=re.IGNORECASE)
                text_lower = result.lower() # Update for next iteration
                
        # ── Emotion fillers (add once, at end) ──────────────────────────────
        EMOTION_FILLERS = {
            "telugu": {
                "playful":    " ra 😂",
                "sad":        "", # Prefix, handled below
                "excited":    " ra!! 🔥",
                "frustrated": " ra yaar 😤",
                "happy":      " bagundhile 😊"
            }
        }
        
        if "telugu" in dialect.lower():
            filler = EMOTION_FILLERS["telugu"].get(emotion, "")
            if emotion == "sad" and not result.lower().startswith("ayyo"):
                result = "ayyo, " + result
            elif filler and not result.endswith(filler.strip()):
                result = result.rstrip(" .") + filler
        
        return result[0].upper() + result[1:] if result else result

    async def _translate(self, text: str, source: str, target: str) -> str:
        if source == target or not argostranslate: return text
        def _doc_translate():
            try:
                # Requires argos packages installed
                return argostranslate.translate.translate(text, source, target)
            except Exception:
                return text
        return await asyncio.to_thread(_doc_translate)
