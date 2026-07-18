"""
arion/agents/deep_language_engine.py
=====================================
ARION 3.0 — Deep Language Engine (A0 of the cognitive pipeline)

Phonetic clustering + Cultural Pragmatics + Code-Switch detection.
Runs as a proper BaseAgent on Channel.DEEP_LANGUAGE.
The Orchestrator also instantiates DeepLanguageCore directly for inline
sub-millisecond use without bus round-trips.

Key principle: don't just tokenize — UNDERSTAND.
  "tinnava" → who said it, to whom, when, about what → REAL meaning.
"""

import re
import json
import sqlite3
import asyncio
import logging
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, List, Tuple, Any
from datetime import datetime
from collections import defaultdict

from core.base_agent import BaseAgent
from core.message_bus import Channel, Message

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
#  DATA STRUCTURE — MessageAnalysis
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class MessageAnalysis:
    """
    Complete deep analysis of a single message.
    Everything the Orchestrator needs to craft a perfect reply.
    """
    raw_text:            str   = ""
    detected_script:     str   = "english"
    code_switches:       List[Dict] = field(default_factory=list)
    phonetic_matches:    List[Dict] = field(default_factory=list)
    normalized_text:     str   = ""
    surface_meaning:     str   = ""
    deep_meaning:        str   = ""
    subtext:             str   = ""
    hidden_need:         str   = "attentive response"
    emotion_primary:     str   = "neutral"
    emotion_secondary:   str   = "neutral"
    emotion_intensity:   float = 0.3
    emotion_trajectory:  str   = "stable"
    formality_level:     float = 0.3
    intimacy_signal:     str   = "neutral"
    recommended_dialect: str   = "english"
    recommended_tone:    str   = "natural"
    words_to_use:        List[str] = field(default_factory=list)
    words_to_avoid:      List[str] = field(default_factory=list)
    optimal_length:      str   = "match_theirs"
    never_sarcastic:     bool  = False
    high_care_mode:      bool  = False

    def to_dict(self) -> Dict:
        return asdict(self)

    def to_prompt_fragment(self) -> str:
        """
        Compact block injected directly into the Ollama system prompt.
        Keeps token cost low while giving LLM critical behavioural guidance.
        """
        if not self.raw_text:
            return ""
        parts = [
            "[DEEP ANALYSIS]",
            f"Hidden need: {self.hidden_need}",
            f"Emotion: {self.emotion_primary} (intensity={self.emotion_intensity:.1f}, trajectory={self.emotion_trajectory})",
            f"Script: {self.detected_script}",
            f"Reply dialect: {self.recommended_dialect}",
            f"Tone: {self.recommended_tone}",
        ]
        if self.words_to_use:
            parts.append(f"Use naturally: {', '.join(self.words_to_use[:5])}")
        if self.words_to_avoid:
            parts.append(f"Avoid: {', '.join(self.words_to_avoid[:5])}")
        if self.never_sarcastic:
            parts.append("CRITICAL: NEVER be sarcastic in this reply.")
        if self.high_care_mode:
            parts.append("CRITICAL: Full care and warmth — this person needs support.")
        if self.subtext and self.subtext not in ("none detected", ""):
            parts.append(f"Subtext: {self.subtext}")
        if self.code_switches:
            impls = [s.get("implication", "") for s in self.code_switches if s.get("implication")]
            if impls:
                parts.append(f"Language signals: {'; '.join(impls)}")
        parts.append("[/DEEP ANALYSIS]")
        return "\n".join(parts)


# ══════════════════════════════════════════════════════════════════════════════
#  PHONETIC NORMALIZER
# ══════════════════════════════════════════════════════════════════════════════

class PhoneticNormalizer:
    """
    Solves the core problem: Telugu/Hindi typed in English has 50 valid
    spellings per word. "tinnava" = "tinnawa" = "tinnabba" = "tinava"
    We map ALL variants to one canonical form.
    """

    CLUSTERS: Dict[str, List[str]] = {
        # ── Telugu food / care ────────────────────────────────────────────
        "tinnava":   ["tinnava","tinnawa","tinnabba","tinava","tinnav","tinnaava","tinavaa"],
        "cheppadu":  ["cheppadu","ceppadu","chepadu","cheppādu","cheppatu"],
        "vastav":    ["vastav","vastaav","vastaavu","vastavu","vastaava"],
        "ledu":      ["ledu","ledhu","lēdu","leduu","ledhuu"],
        "unnav":     ["unnav","unnavu","unnaav","unnāvu","unav","unnawa"],
        "chuddam":   ["chuddam","chudam","chooddam","chuuddam"],
        "ante":      ["ante","antey","antē","anti","antee"],
        "kaadu":     ["kaadu","kadu","kādu","kaadhu","kādhu"],
        "ayyindi":   ["ayyindi","ayindi","ayyindhi","ayyindee","aindi"],
        "cheyyadu":  ["cheyyadu","cheyyaadu","ceyadu","cheyyādhu"],
        "padindi":   ["padindi","paddindi","padindhi","padindee"],
        "ikkade":    ["ikkade","ikkadey","ikkadee","ikade"],
        "akkade":    ["akkade","akkadey","akade","akkadee"],
        "eppudu":    ["eppudu","eppuduu","epudu","eppudhuu"],
        "cheyyi":    ["cheyyi","cheyi","cheyyy","cheyyii","chei"],
        "aipoindi":  ["aipoindi","aipoyindi","aipoindhi","aypoyindi"],
        "telisi":    ["telisi","telisii","thelisi","telisindi"],
        "manchidi":  ["manchidi","manchidhi","manchidee","manchi"],
        "baagundi":  ["baagundi","bagundi","bāgundi","bagundhi"],
        "cheppu":    ["cheppu","chepu","cheppuu"],
        "velladu":   ["velladu","velaadu","veladu","vellādu"],
        "padukko":   ["padukko","paduko","padukkoo"],
        "nidra":     ["nidra","nidhra","nidhara"],
        "thelusa":   ["thelusa","telusa","thelisaa","telisaa"],
        # ── Telugu address / slang ────────────────────────────────────────
        "rey":       ["rey","re","ree","reyy"],
        "ra":        ["ra","raa"],
        "machha":    ["machha","macha","machaa","maccha","mach"],
        "enti":      ["enti","entii","entey","ente"],
        "entira":    ["entira","entiiraa","entiraa"],
        "evadu":     ["evadu","evaduu","evaru"],
        "emaindi":   ["emaindi","emaindhi","emaaindi"],
        "daruvu":    ["daruvu","daruvuu","daruvvu"],
        "pani":      ["pani","panee","paniii"],
        "chala":     ["chala","chalaa","chaala"],
        "cheppandi": ["cheppandi","cheppandhi","chepandi"],
        "okate":     ["okate","okaate","okatey"],
        "aithe":     ["aithe","aithey","aitheee","ithe"],
        "appudu":    ["appudu","appuduu","appudhu"],
        "kaani":     ["kaani","kaanii","kaanee","kani"],
        "okka":      ["okka","okkka","oka"],
        # ── Hindi common ─────────────────────────────────────────────────
        "khaana":    ["khaana","khana","khanaa","khaanaa","khāna"],
        "theek":     ["theek","thik","teek","thikk"],
        "accha":     ["accha","aacha","acha","achha","achcha"],
        "nahi":      ["nahi","nahin","nai","nahii","nahī"],
        "bol":       ["bol","boll","bole","boluu","bolo"],
        "yaar":      ["yaar","yar","yarr","yarre","yaara"],
        "bhai":      ["bhai","bhaai","bhaiii"],
        "matlab":    ["matlab","matalab","mtlb"],
        "areh":      ["areh","arre","are","arey"],
        "kya":       ["kya","kyaa"],
        "bas":       ["bas","baas","bass"],
        "abhi":      ["abhi","abhe","abhii"],
        "karo":      ["karo","karro","kro"],
        "haan":      ["haan","han","haann","haa"],
        "kyun":      ["kyun","kyunn","kyuun","kyu"],
    }

    def __init__(self):
        self._map: Dict[str, str] = {}
        for canonical, variants in self.CLUSTERS.items():
            for v in variants:
                self._map[v.lower().strip("?!., ")] = canonical

        self._rules: List[Tuple[str, str]] = [
            (r'([bcdfghjklmnpqrstvwxyz])\1+', r'\1'),
            (r'aa', 'a'),
            (r'oo', 'u'),
            (r'ee', 'i'),
            (r'w', 'v'),
            (r'dh', 'd'),
            (r'(?<![aeiou])th(?![aeiou])', 't'),
        ]

    def normalize(self, word: str) -> str:
        clean = word.lower().strip("?!., ")
        if clean in self._map:
            return self._map[clean]
        simplified = clean
        for pat, rep in self._rules:
            simplified = re.sub(pat, rep, simplified)
            if simplified in self._map:
                return self._map[simplified]
        return word

    def normalize_text(self, text: str) -> str:
        return " ".join(self.normalize(w) for w in text.split())

    def find_matches(self, text: str, vocab: Dict) -> List[Dict]:
        matches = []
        tokens = text.lower().split()
        for i, token in enumerate(tokens):
            clean = token.strip("?!., ")
            canonical = self.normalize(clean)
            if clean in vocab:
                matches.append({"position": i, "original": token,
                                 "canonical": clean, "match_type": "exact",
                                 "data": vocab[clean]})
            elif canonical != clean and canonical in vocab:
                matches.append({"position": i, "original": token,
                                 "canonical": canonical, "match_type": "phonetic",
                                 "data": vocab[canonical]})
        return matches


# ══════════════════════════════════════════════════════════════════════════════
#  PRAGMATICS ENGINE
# ══════════════════════════════════════════════════════════════════════════════

class PragmaticsEngine:
    """
    Knows WHY a word is used — not just what it means.
    "tinnava" from mom → NEVER sarcastic, pure care.
    "tinnava" from best friend at 11pm → definitely teasing.
    """

    CORE_RULES: List[Dict] = [
        # ── rey / ra ─────────────────────────────────────────────────────
        {"word": "rey", "priority": 10,
         "require": {"relationship": ["close_friend","best_friend","sibling_male","cousin_male"]},
         "block":   {"relationship": ["mother","father","elder","boss","teacher","formal"]},
         "tone": "warm_casual", "emoji_ok": True, "never_sarcastic": False, "high_care_mode": False,
         "meaning": "hey / bro (affectionate masculine address)"},
        {"word": "rey", "priority": 12,
         "require": {"relationship": ["close_friend","best_friend"],
                     "emotion": ["frustration","mild_anger","disappointment"]},
         "tone": "firm_but_friendly", "emoji_ok": False, "never_sarcastic": False, "high_care_mode": False,
         "meaning": "hey seriously / come on man (mild concern + firmness)"},
        {"word": "ra", "priority": 10,
         "require": {"relationship": ["best_friend","childhood_friend"],
                     "formality_max": 0.2},
         "tone": "ultra_casual", "emoji_ok": True, "never_sarcastic": False, "high_care_mode": False,
         "meaning": "come on / hey (most intimate masculine form)"},
        # ── tinnava ───────────────────────────────────────────────────────
        {"word": "tinnava", "priority": 15,
         "require": {"relationship": ["mother","grandmother","parent","caring_elder"]},
         "tone": "pure_care", "emoji_ok": False, "never_sarcastic": True, "high_care_mode": True,
         "meaning": "Did you eat? (genuine parental care — NEVER make this sarcastic)"},
        {"word": "tinnava", "priority": 10,
         "require": {"relationship": ["close_friend","best_friend"],
                     "time": ["late_night","night"],
                     "topic": ["food","drinks","party","outing"]},
         "tone": "playful_teasing", "emoji_ok": True, "never_sarcastic": False, "high_care_mode": False,
         "meaning": "You ate? (playful teasing about late-night behaviour)"},
        {"word": "tinnava", "priority": 8,
         "require": {},
         "tone": "caring", "emoji_ok": False, "never_sarcastic": True, "high_care_mode": False,
         "meaning": "Did you eat? (caring check-in — default safe interpretation)"},
        # ── machha ────────────────────────────────────────────────────────
        {"word": "machha", "priority": 10,
         "require": {"relationship": ["friend","acquaintance","peer","colleague_friendly"]},
         "tone": "friendly_casual", "emoji_ok": True, "never_sarcastic": False, "high_care_mode": False,
         "meaning": "bro / dude"},
        # ── enti ──────────────────────────────────────────────────────────
        {"word": "enti", "priority": 10,
         "require": {"emotion": ["neutral","curious","playful"]},
         "tone": "casual_question", "emoji_ok": True, "never_sarcastic": False, "high_care_mode": False,
         "meaning": "what? (curious or casual)"},
        {"word": "enti", "priority": 12,
         "require": {"emotion": ["frustration","exasperation","mild_anger"]},
         "tone": "mild_frustration", "emoji_ok": False, "never_sarcastic": False, "high_care_mode": False,
         "meaning": "Seriously? / What is this? (mild exasperation — needs acknowledgment)"},
        # ── yaar ─────────────────────────────────────────────────────────
        {"word": "yaar", "priority": 10,
         "require": {"relationship": ["friend","peer","close"]},
         "tone": "friendly_hindi", "emoji_ok": True, "never_sarcastic": False, "high_care_mode": False,
         "meaning": "friend / buddy (warm Hindi address)"},
        {"word": "yaar", "priority": 11,
         "require": {"emotion": ["mild_distress","complaint","venting","sadness"]},
         "tone": "seeking_sympathy", "emoji_ok": False, "never_sarcastic": True, "high_care_mode": False,
         "meaning": "man... (seeking sympathy — match their low energy first)"},
        # ── areh ─────────────────────────────────────────────────────────
        {"word": "areh", "priority": 10,
         "require": {"emotion": ["surprise","realization","mild_shock"]},
         "tone": "expressive_surprise", "emoji_ok": True, "never_sarcastic": False, "high_care_mode": False,
         "meaning": "oh wow / hey wait (Hindi surprise marker)"},
        # ── accha ─────────────────────────────────────────────────────────
        {"word": "accha", "priority": 10,
         "require": {"emotion": ["neutral","understanding","acknowledgment"]},
         "tone": "acknowledgment", "emoji_ok": False, "never_sarcastic": False, "high_care_mode": False,
         "meaning": "okay / I see / alright"},
        {"word": "accha", "priority": 11,
         "require": {"emotion": ["sarcasm","doubt","skepticism"]},
         "tone": "skeptical", "emoji_ok": False, "never_sarcastic": False, "high_care_mode": False,
         "meaning": "Oh really? (skeptical — validate skepticism without being dismissive)"},
        # ── cheppu ───────────────────────────────────────────────────────
        {"word": "cheppu", "priority": 10,
         "require": {"relationship": ["close","friend","best_friend"]},
         "tone": "inviting_open", "emoji_ok": False, "never_sarcastic": False, "high_care_mode": False,
         "meaning": "tell me / go ahead (inviting them to share — give full attention)"},
        # ── daruvu ───────────────────────────────────────────────────────
        {"word": "daruvu", "priority": 10,
         "require": {"emotion": ["admiration","playful","teasing"]},
         "tone": "playful_compliment", "emoji_ok": True, "never_sarcastic": False, "high_care_mode": False,
         "meaning": "you're smooth / skilled (playful compliment or teasing)"},
    ]

    TONE_TO_EMOTION: Dict[str, str] = {
        "warm_casual": "joy", "pure_care": "care", "playful_teasing": "playfulness",
        "firm_but_friendly": "mild_concern", "seeking_sympathy": "mild_distress",
        "ultra_casual": "comfort", "friendly_hindi": "warmth",
        "expressive_surprise": "surprise", "mild_frustration": "frustration",
    }

    def __init__(self, db_path: str):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS learned_pragmatic_rules (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                word         TEXT NOT NULL,
                relationship TEXT,
                time_of_day  TEXT,
                topic        TEXT,
                emotion      TEXT,
                appropriate  INTEGER DEFAULT 1,
                tone         TEXT,
                meaning      TEXT,
                confidence   REAL DEFAULT 0.8,
                usage_count  INTEGER DEFAULT 0,
                source       TEXT DEFAULT 'owner_feedback',
                created_at   TEXT DEFAULT (datetime('now'))
            );
            CREATE INDEX IF NOT EXISTS idx_pr_word ON learned_pragmatic_rules(word);
            CREATE TABLE IF NOT EXISTS word_usage_graph (
                word         TEXT,
                co_word      TEXT,
                frequency    INTEGER DEFAULT 1,
                emotion      TEXT,
                relationship TEXT,
                PRIMARY KEY (word, co_word, relationship)
            );
        """)
        conn.commit()
        conn.close()

    def analyze(self, word: str, ctx: Dict) -> Dict:
        w = word.lower().strip()
        scored: List[Tuple[float, Dict]] = []
        for rule in self.CORE_RULES:
            if rule["word"] != w:
                continue
            score = self._score(rule, ctx)
            if score > 0:
                scored.append((score, rule))
        scored.extend(self._query_learned(w, ctx))
        if not scored:
            return {"meaning": None, "tone": "neutral",
                    "never_sarcastic": False, "high_care_mode": False,
                    "emoji_ok": True, "confidence": 0.0}
        scored.sort(key=lambda x: x[0], reverse=True)
        _, best = scored[0]
        return {
            "meaning":         best.get("meaning", ""),
            "tone":            best.get("tone", "neutral"),
            "never_sarcastic": best.get("never_sarcastic", False),
            "high_care_mode":  best.get("high_care_mode", False),
            "emoji_ok":        best.get("emoji_ok", True),
            "confidence":      min(1.0, scored[0][0] / 15.0),
        }

    def _score(self, rule: Dict, ctx: Dict) -> float:
        score = float(rule.get("priority", 10))
        for key, vals in rule.get("block", {}).items():
            if ctx.get(key) in vals:
                return 0.0
        for key, vals in rule.get("require", {}).items():
            if key == "formality_max":
                if ctx.get("formality", 1.0) <= vals:
                    score += 3.0
                else:
                    score -= 5.0
            elif isinstance(vals, list):
                if ctx.get(key) in vals:
                    score += 3.0
                else:
                    score -= 1.0
        return max(0.0, score)

    def _query_learned(self, word: str, ctx: Dict) -> List[Tuple[float, Dict]]:
        try:
            conn = sqlite3.connect(self.db_path)
            rows = conn.execute("""
                SELECT tone, meaning, confidence, usage_count, relationship, emotion
                FROM learned_pragmatic_rules
                WHERE word = ? AND appropriate = 1
                ORDER BY confidence DESC, usage_count DESC LIMIT 5
            """, (word,)).fetchall()
            conn.close()
        except Exception:
            return []
        results = []
        for tone, meaning, conf, usage, rel, emo in rows:
            score = conf * max(1, usage) * 0.2
            if rel and ctx.get("relationship") == rel:
                score += 2.0
            if emo and ctx.get("emotion") == emo:
                score += 1.5
            results.append((score, {"tone": tone, "meaning": meaning,
                                     "never_sarcastic": False, "high_care_mode": False,
                                     "emoji_ok": True, "confidence": conf}))
        return results

    def learn(self, word: str, ctx: Dict, outcome: Dict):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT INTO learned_pragmatic_rules
            (word, relationship, time_of_day, topic, emotion,
             appropriate, tone, meaning, confidence, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0.9, 'owner_feedback')
        """, (word, ctx.get("relationship"), ctx.get("time_of_day"),
               ctx.get("topic"), ctx.get("emotion"),
               int(outcome.get("appropriate", True)),
               outcome.get("tone", "neutral"), outcome.get("meaning", "")))
        conn.commit()
        conn.close()
        logger.info(f"[Pragmatics] Learned rule: '{word}' → {outcome}")

    def update_word_graph(self, word: str, co_words: List[str],
                          emotion: str, relationship: str):
        if not co_words:
            return
        try:
            conn = sqlite3.connect(self.db_path)
            for co in co_words[:10]:
                conn.execute("""
                    INSERT INTO word_usage_graph (word, co_word, frequency, emotion, relationship)
                    VALUES (?, ?, 1, ?, ?)
                    ON CONFLICT(word, co_word, relationship)
                    DO UPDATE SET frequency = frequency + 1
                """, (word, co, emotion, relationship))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.debug(f"[Pragmatics] graph update failed: {e}")


# ══════════════════════════════════════════════════════════════════════════════
#  CODE SWITCH DETECTOR
# ══════════════════════════════════════════════════════════════════════════════

class CodeSwitchDetector:
    """
    Detects mid-sentence language switches and interprets their emotional meaning.
    "project aipoindi but yaar I don't know how to tell manager"
    → Telugu → Hindi → English = stressed and uncertain
    """

    TELUGU_WORDS = {
        "aipoindi","ledu","undi","cheyyi","ante","kaadu","eppudu","ikkade",
        "akkade","vastav","velladu","tinnava","unnav","cheppadu","padindi",
        "chuddam","ayyindi","rey","ra","machha","enti","entira","daruvu",
        "cheppu","okate","aithe","appudu","kaani","telisi","manchidi",
        "baagundi","thelusa","padukko","nidra",
    }
    HINDI_WORDS = {
        "yaar","kya","nahi","theek","accha","bhai","matlab","bas","abhi",
        "karo","bol","kab","kyun","haan","areh","arre","yar","suno",
        "dekho","bolo","raho","jaao","aao",
    }
    ENGLISH_STRUCTURAL = {
        "the","is","are","was","were","have","has","had","but","and","so",
        "because","if","when","then","just","like","know","dont","cant",
        "wont","really","actually","anyway","basically",
    }

    def detect(self, text: str) -> List[Dict]:
        words = text.split()
        switches = []
        current_lang: Optional[str] = None
        for i, word in enumerate(words):
            detected = self._classify(word)
            if detected and detected != current_lang and current_lang is not None:
                switches.append({
                    "position":    i,
                    "word":        word,
                    "from_lang":   current_lang,
                    "to_lang":     detected,
                    "implication": self._interpret(current_lang, detected, i, len(words)),
                })
            if detected:
                current_lang = detected
        return switches

    def _classify(self, word: str) -> Optional[str]:
        w = word.lower().strip("?!., ")
        for char in word:
            cp = ord(char)
            if 0x0C00 <= cp <= 0x0C7F:
                return "telugu"
            if 0x0900 <= cp <= 0x097F:
                return "hindi"
        if w in self.TELUGU_WORDS:
            return "telugu"
        if w in self.HINDI_WORDS:
            return "hindi"
        if w in self.ENGLISH_STRUCTURAL:
            return "english"
        return None

    def _interpret(self, from_l: str, to_l: str, pos: int, total: int) -> str:
        rel_pos = pos / max(total, 1)
        phase = "early" if rel_pos < 0.33 else "mid" if rel_pos < 0.66 else "late"
        table: Dict[Tuple[str,str], Dict] = {
            ("telugu", "english"): {"early": "emphasizing a point", "mid": "technical content coming", "late": "firm conclusion"},
            ("english", "telugu"): {"early": "warming up, comfortable", "mid": "going personal/emotional", "late": "expressing true feeling in mother tongue"},
            ("hindi",   "telugu"): {"any": "very relaxed — mixing freely"},
            ("telugu",  "hindi"):  {"any": "borrowing expression that fits better in Hindi"},
            ("english", "hindi"):  {"any": "cultural marker — thinking in Hindi now"},
            ("hindi",   "english"):{"any": "technical/formal pivot"},
        }
        row = table.get((from_l, to_l), {})
        return row.get("any", row.get(phase, "language preference shift"))

    def trajectory(self, switches: List[Dict]) -> str:
        n = len(switches)
        if n >= 3:
            return "emotionally_volatile"
        if n == 2:
            langs = {s["to_lang"] for s in switches}
            return "seeking_clarity" if "english" in langs else "emotionally_engaged"
        if n == 1:
            return "transitioning"
        return "stable"


# ══════════════════════════════════════════════════════════════════════════════
#  DEEP LANGUAGE CORE  (used directly by Orchestrator without bus round-trip)
# ══════════════════════════════════════════════════════════════════════════════

class DeepLanguageCore:
    """
    Orchestrates Phonetic + Pragmatics + CodeSwitch into one MessageAnalysis.
    The Orchestrator instantiates this directly for inline, zero-latency use.
    """

    # Punctuation / pattern → emotion signal weights
    EMOTION_PATTERNS: Dict[str, Dict] = {
        "excitement":  {"re_patterns": [r"!{2,}"],            "weight": 2.0},
        "anger":       {"re_patterns": [r"[A-Z]{5,}"],        "weight": 2.5},
        "sadness":     {"re_patterns": [r"\.{3,}"],           "weight": 1.5},
        "anxiety":     {"re_patterns": [r"\?{2,}"],           "weight": 1.5},
        "playfulness": {"re_patterns": [r"haha|lol|😂|🤣"],   "weight": 2.0},
        "care":        {"re_patterns": [r"tinnava|khaana"],   "weight": 2.0},
    }

    # emotion_intensity × trajectory → hidden need
    NEED_MAP: Dict[str, str] = {
        "emotionally_volatile":  "grounding and calm presence",
        "seeking_clarity":       "clear, simple, honest answer",
        "emotionally_engaged":   "full engagement and validation",
        "transitioning":         "follow their lead",
        "stable":                "attentive response",
    }

    # (relationship, emotion) → (tone, words_to_use, words_to_avoid)
    TONE_RULES: Dict[Tuple[str, str], Tuple[str, List[str], List[str]]] = {
        ("mother",       "any"):        ("warm_respectful",  ["na", "cheppandi"],     ["rey", "machha"]),
        ("father",       "any"):        ("warm_respectful",  ["cheppandi"],           ["rey", "machha"]),
        ("elder",        "any"):        ("warm_respectful",  ["cheppandi", "ji"],     ["rey", "ra"]),
        ("best_friend",  "joy"):        ("playful_casual",   ["machha", "rey"],       ["ji", "sir"]),
        ("best_friend",  "excitement"): ("hyped_casual",     ["machha", "rey", "da"], ["ji"]),
        ("best_friend",  "sadness"):    ("warm_supportive",  ["rey", "chill"],        []),
        ("close_friend", "neutral"):    ("friendly_casual",  ["machha"],              ["ji", "sir"]),
        ("close_friend", "any"):        ("friendly_casual",  ["machha", "rey"],       ["ji"]),
        ("owner",        "any"):        ("close_friend",     ["ra", "rey"],           []),
    }

    def __init__(self, config_dir: str, db_path: str):
        self.phonetic   = PhoneticNormalizer()
        self.pragmatics = PragmaticsEngine(db_path)
        self.codesw     = CodeSwitchDetector()
        self.vocab      = self._load_vocab(Path(config_dir))
        logger.info(f"[DeepLanguageCore] Loaded {len(self.vocab)} vocab entries.")

    def _load_vocab(self, cfg: Path) -> Dict:
        combined: Dict[str, Any] = {}
        candidates = [
            cfg / "vocabulary_telugu.json",
            cfg / "vocabulary_hindi.json",
            cfg / ".." / "language" / "slang" / "telugu.json",
            cfg / ".." / "language" / "slang" / "hindi.json",
        ]
        for path in candidates:
            resolved = path.resolve()
            if not resolved.exists():
                continue
            try:
                with open(resolved, encoding="utf-8") as f:
                    data = json.load(f)
                for word, info in data.items():
                    key = word.lower()
                    if key == "meta":
                        continue
                    if isinstance(info, str):
                        combined[key] = {"meaning": info, "language": "unknown"}
                    elif isinstance(info, dict):
                        combined[key] = info
            except Exception as e:
                logger.warning(f"[DeepLanguageCore] Could not load {resolved.name}: {e}")
        return combined

    async def analyze(self, text: str, ctx: Dict) -> MessageAnalysis:
        """
        Full pipeline: text + context dict → MessageAnalysis.
        ctx keys: relationship, topic, emotion, formality, conversation_history
        """
        # ── 1. Phonetic normalization ─────────────────────────────────────
        normalized = self.phonetic.normalize_text(text)

        # ── 2. Code switch detection ──────────────────────────────────────
        switches = self.codesw.detect(text)
        trajectory = self.codesw.trajectory(switches)

        # ── 3. Vocabulary matches ─────────────────────────────────────────
        matches = self.phonetic.find_matches(text.lower(), self.vocab)

        # ── 4. Primary script ─────────────────────────────────────────────
        script = self._detect_primary_script(text, matches, switches)

        # ── 5. Pragmatic analysis for all matched words ───────────────────
        relationship = ctx.get("relationship", "unknown")
        word_ctx = {
            "relationship": relationship,
            "time_of_day":  self._time_of_day(),
            "topic":        ctx.get("topic"),
            "emotion":      ctx.get("emotion"),
            "formality":    ctx.get("formality", 0.3),
        }
        prag_insights: List[Dict] = []
        for m in matches:
            result = self.pragmatics.analyze(m["canonical"], word_ctx)
            if result["confidence"] > 0.25:
                prag_insights.append({
                    "word":            m["canonical"],
                    "true_meaning":    result["meaning"],
                    "tone":            result["tone"],
                    "never_sarcastic": result["never_sarcastic"],
                    "high_care_mode":  result["high_care_mode"],
                    "emoji_ok":        result["emoji_ok"],
                    "confidence":      result["confidence"],
                })

        # ── 6. Meaning layers ─────────────────────────────────────────────
        surface   = self._surface_meaning(normalized, matches)
        deep      = self._deep_meaning(surface, prag_insights, switches)
        subtext   = self._detect_subtext(text, ctx, switches)
        hidden    = self._hidden_need(trajectory, subtext, ctx)

        # ── 7. Emotion analysis ───────────────────────────────────────────
        emo_primary, emo_secondary, intensity = self._analyze_emotion(
            text, prag_insights)

        # ── 8. Response guidance ──────────────────────────────────────────
        dialect  = self._recommend_dialect(script, switches, relationship)
        tone, words_use, words_avoid = self._recommend_style(
            hidden, emo_primary, relationship, prag_insights, dialect)

        # ── 9. Flags ──────────────────────────────────────────────────────
        never_sarcastic = any(p.get("never_sarcastic") for p in prag_insights)
        high_care       = any(p.get("high_care_mode")  for p in prag_insights)

        # ── 10. Passive learning — update word co-occurrence graph ─────────
        canonical_words = [m["canonical"] for m in matches]
        for w in canonical_words:
            co = [x for x in canonical_words if x != w]
            self.pragmatics.update_word_graph(w, co, emo_primary, relationship)

        return MessageAnalysis(
            raw_text=text,
            detected_script=script,
            code_switches=switches,
            phonetic_matches=[m for m in matches if m["match_type"] == "phonetic"],
            normalized_text=normalized,
            surface_meaning=surface,
            deep_meaning=deep,
            subtext=subtext,
            hidden_need=hidden,
            emotion_primary=emo_primary,
            emotion_secondary=emo_secondary,
            emotion_intensity=intensity,
            emotion_trajectory=trajectory,
            formality_level=ctx.get("formality", 0.3),
            intimacy_signal=self._intimacy(prag_insights),
            recommended_dialect=dialect,
            recommended_tone=tone,
            words_to_use=words_use,
            words_to_avoid=words_avoid,
            optimal_length=self._recommend_length(hidden, emo_primary, text),
            never_sarcastic=never_sarcastic,
            high_care_mode=high_care,
        )

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _detect_primary_script(self, text: str, matches: List[Dict],
                                switches: List[Dict]) -> str:
        scores: Dict[str, float] = defaultdict(float)
        for m in matches:
            lang = m.get("data", {}).get("language", "")
            if lang:
                scores[lang] += 1.0 + (0.5 if m["match_type"] == "phonetic" else 0)
        for char in text:
            cp = ord(char)
            if 0x0C00 <= cp <= 0x0C7F:
                scores["telugu"] += 2.0
            elif 0x0900 <= cp <= 0x097F:
                scores["hindi"] += 2.0
        if not scores:
            return "english"
        if scores.get("telugu", 0) > 1 and scores.get("english", 0) > 1:
            return "tenglish"
        return max(scores, key=scores.get)  # type: ignore

    def _surface_meaning(self, normalized: str, matches: List[Dict]) -> str:
        if not matches:
            return normalized
        parts = [normalized]
        for m in matches[:3]:
            meaning = m.get("data", {}).get("meaning", "")
            if meaning:
                parts.append(f"({m['canonical']} = {meaning})")
        return " ".join(parts)

    def _deep_meaning(self, surface: str, prag: List[Dict],
                      switches: List[Dict]) -> str:
        parts = [surface]
        for p in prag[:3]:
            if p.get("true_meaning"):
                parts.append(f"[{p['word']}={p['true_meaning']}]")
        for s in switches:
            if s.get("implication"):
                parts.append(f"[switch→{s['implication']}]")
        return " ".join(parts)

    def _detect_subtext(self, message: str, ctx: Dict, switches: List[Dict]) -> str:
        signals = []
        msg_lower = message.lower()
        if len(message.split()) < 4 and ctx.get("last_message_was_emotional"):
            signals.append("short reply after emotional message — may be overwhelmed")
        if message.count("?") > 1 and ctx.get("last_was_question"):
            signals.append("answering question with question — deflecting")
        for s in switches:
            if s["to_lang"] == "telugu" and s["from_lang"] == "english":
                signals.append("switched to mother tongue — going emotional")
        if "..." in message:
            signals.append("trailing ellipsis — unsure or holding something back")
        return "; ".join(signals) if signals else "none detected"

    def _hidden_need(self, trajectory: str, subtext: str, ctx: Dict) -> str:
        # Trajectory-based
        if trajectory in self.NEED_MAP:
            base = self.NEED_MAP[trajectory]
        else:
            base = "attentive response"
        # Subtext overrides
        if "deflecting" in subtext:
            return "space and no pressure"
        if "mother tongue" in subtext:
            return "emotional validation in their language"
        if "overwhelmed" in subtext:
            return "time and gentle follow-up"
        if "holding something back" in subtext:
            return "gentle invitation to open up"
        # Emotion-based
        emotion_needs = {
            "anxiety": "reassurance and practical help",
            "anger":   "acknowledgment first, then solutions",
            "sadness": "presence and validation",
            "excitement": "matching energy and engagement",
            "confusion": "clarity and simple explanation",
            "loneliness": "connection and full attention",
        }
        emo = ctx.get("emotion", "")
        if emo in emotion_needs:
            return emotion_needs[emo]
        return base

    def _analyze_emotion(self, text: str,
                          prag: List[Dict]) -> Tuple[str, str, float]:
        scores: Dict[str, float] = defaultdict(float)
        # Pattern signals
        for emotion, cfg in self.EMOTION_PATTERNS.items():
            for pat in cfg["re_patterns"]:
                if re.search(pat, text):
                    scores[emotion] += cfg["weight"]
        # Punctuation
        scores["excitement"] += min(text.count("!"), 3) * 0.5
        scores["anxiety"]    += min(text.count("?"), 3) * 0.3
        scores["sadness"]    += text.count("...") * 0.8
        # Pragmatic tone signals
        tone_emo_map = {
            "warm_casual": "joy", "pure_care": "care",
            "playful_teasing": "playfulness", "firm_but_friendly": "mild_concern",
            "seeking_sympathy": "mild_distress", "ultra_casual": "comfort",
        }
        for p in prag:
            emo = tone_emo_map.get(p.get("tone", ""))
            if emo:
                scores[emo] += 1.5 * p.get("confidence", 0.5)
        if not scores:
            return "neutral", "neutral", 0.3
        sorted_emo = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        primary   = sorted_emo[0][0]
        secondary = sorted_emo[1][0] if len(sorted_emo) > 1 else "neutral"
        intensity = min(1.0, sorted_emo[0][1] / 5.0)
        return primary, secondary, intensity

    def _recommend_dialect(self, script: str, switches: List[Dict],
                            relationship: str) -> str:
        if script in ("telugu", "tenglish"):
            return "tenglish"
        if script == "hindi":
            return "hinglish"
        for s in reversed(switches):
            if s["to_lang"] == "telugu":
                return "tenglish"
            if s["to_lang"] == "hindi":
                return "hinglish"
        if relationship in ("mother", "father", "elder"):
            return "telugu_respectful"
        return "english"

    def _recommend_style(self, hidden_need: str, emotion: str, relationship: str,
                          prag: List[Dict], dialect: str
                          ) -> Tuple[str, List[str], List[str]]:
        # High-care situations override everything
        if any(p.get("high_care_mode") for p in prag):
            return "warm_supportive", ["na", "cheppandi"], ["machha", "rey"]
        # Never sarcastic in distress
        if emotion in ("sadness", "anxiety", "distress"):
            return "warm_supportive", ["okay", "chill", "undi"], []
        # Lookup table
        for (rel, emo), (tone, use, avoid) in self.TONE_RULES.items():
            if rel == relationship and (emo == emotion or emo == "any"):
                return tone, use, avoid
        # Generic friendly
        if relationship in ("close_friend", "best_friend", "owner"):
            return "playful_casual", ["machha", "rey"], ["ji", "sir"]
        return "natural", [], []

    def _recommend_length(self, hidden_need: str, emotion: str, text: str) -> str:
        word_count = len(text.split())
        if word_count < 5:
            return "short"
        if emotion in ("sadness", "anxiety"):
            return "short"
        if hidden_need == "clarity and simple explanation":
            return "medium"
        if word_count > 30:
            return "medium"
        return "match_theirs"

    def _intimacy(self, prag: List[Dict]) -> str:
        casual_tones  = {"ultra_casual","warm_casual","playful_casual","playful_teasing","hyped_casual"}
        formal_tones  = {"warm_respectful","professional_warm","acknowledgment"}
        c = sum(1 for p in prag if p.get("tone","") in casual_tones)
        f = sum(1 for p in prag if p.get("tone","") in formal_tones)
        if c > f:
            return "high_intimacy"
        if f > c:
            return "maintaining_distance"
        return "neutral"

    @staticmethod
    def _time_of_day() -> str:
        h = datetime.now().hour
        if 5 <= h < 12:  return "morning"
        if 12 <= h < 17: return "afternoon"
        if 17 <= h < 21: return "evening"
        return "late_night"


# ══════════════════════════════════════════════════════════════════════════════
#  AGENT WRAPPER  (registers on the bus for external callers)
# ══════════════════════════════════════════════════════════════════════════════

class DeepLanguageEngine(BaseAgent):
    """
    BaseAgent wrapper around DeepLanguageCore.
    The Orchestrator uses DeepLanguageCore directly (inline, no bus hop).
    Other agents can call Channel.DEEP_LANGUAGE if they need deep analysis.
    """

    def __init__(self, config_dir: str = "arion/config",
                 db_path: str = "arion/data/pragmatics.db"):
        super().__init__("DeepLanguageEngine", [Channel.DEEP_LANGUAGE])
        self.core = DeepLanguageCore(config_dir=config_dir, db_path=db_path)

    async def run_loop(self):
        while self.running:
            msg = await self.get_next_message(timeout=1.0)
            if msg:
                await self.handle_message(msg)

    async def handle_message(self, message: Message):
        if message.action == "analyze_deep":
            text = message.payload.get("text", "")
            ctx  = message.payload.get("context", {})
            try:
                analysis = await self.core.analyze(text, ctx)
                if message.requires_response:
                    await self.respond_to(message, "analysis_complete",
                                          analysis.to_dict())
            except Exception as e:
                logger.error(f"[DeepLanguageEngine] analyze failed: {e}")
                if message.requires_response:
                    await self.respond_to(message, "analysis_complete", {})

        elif message.action == "learn_pragmatic_rule":
            word    = message.payload.get("word", "")
            ctx     = message.payload.get("context", {})
            outcome = message.payload.get("outcome", {})
            if word:
                self.core.pragmatics.learn(word, ctx, outcome)
                logger.info(f"[DeepLanguageEngine] Pragmatic rule learned for '{word}'")
