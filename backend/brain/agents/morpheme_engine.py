"""
═══════════════════════════════════════════════════════════════
MORPHEME ENGINE
Splits words into their smallest meaningful units.

Telugu is AGGLUTINATIVE — words are built by
sticking pieces together like LEGO blocks.

"chestunnanu" =
    che     (root of "chey" = to do)
  + stunna  (present continuous marker)
  + nu      (first person singular suffix)
  = "I am doing"

"bagunnaru" =
    bagun   (root of "bagundi" = good)
  + na      (present state)
  + ru      (third person plural / formal you suffix)
  = "They are fine / You are fine (formal)"

"vellapotunnanu" =
    vella   (root = to go)
  + po      (directional = away)
  + tunna   (present continuous)
  + nu      (first person)
  = "I am going away"
═══════════════════════════════════════════════════════════════
"""

from dataclasses import dataclass, field
from typing import Optional


# ═══════════════════════════════════════════════════════════════
# TELUGU MORPHEME DATABASE
# Every meaningful chunk of Telugu words
# ═══════════════════════════════════════════════════════════════

TELUGU_MORPHEMES = {

    # ── VERB ROOTS (Dhatus) ────────────────────────────────────
    # Format: root → {meaning, type, forms}

    "che": {
        "meaning":   "do/perform",
        "type":      "verb_root",
        "full_verb": "cheyyadam",
        "telugu":    "చే",
        "variants":  ["chey", "ches", "che"],
        "example":   "chesanu = I did"
    },
    "vel": {
        "meaning":   "go/leave",
        "type":      "verb_root",
        "full_verb": "velladam",
        "telugu":    "వెళ్",
        "variants":  ["vel", "vell", "vella"],
        "example":   "vellanu = I went"
    },
    "vas": {
        "meaning":   "come",
        "type":      "verb_root",
        "full_verb": "raavadam",
        "telugu":    "వస్",
        "variants":  ["vas", "va", "vach"],
        "example":   "vastanu = I will come"
    },
    "chep": {
        "meaning":   "tell/say",
        "type":      "verb_root",
        "full_verb": "cheppadam",
        "telugu":    "చెప్",
        "variants":  ["chep", "chepp"],
        "example":   "cheppanu = I told"
    },
    "chood": {
        "meaning":   "see/look",
        "type":      "verb_root",
        "full_verb": "choodalm",
        "telugu":    "చూడ్",
        "variants":  ["chud", "choo", "chood"],
        "example":   "choodanu = I saw"
    },
    "tine": {
        "meaning":   "eat",
        "type":      "verb_root",
        "full_verb": "tinavadm",
        "telugu":    "తినే",
        "variants":  ["tin", "tine", "tina"],
        "example":   "tinanu = I ate"
    },
    "vin": {
        "meaning":   "hear/listen",
        "type":      "verb_root",
        "full_verb": "vinadam",
        "telugu":    "విన్",
        "variants":  ["vin", "vinn"],
        "example":   "vinanu = I heard"
    },
    "pad": {
        "meaning":   "sleep/fall",
        "type":      "verb_root",
        "full_verb": "padukodadam",
        "telugu":    "పడ్",
        "variants":  ["pad", "padd", "padu"],
        "example":   "padukonnanu = I slept"
    },
    "pamp": {
        "meaning":   "send",
        "type":      "verb_root",
        "full_verb": "pampadanam",
        "telugu":    "పంప్",
        "variants":  ["pamp", "pampu"],
        "example":   "pampanu = I sent"
    },
    "tel": {
        "meaning":   "know/understand",
        "type":      "verb_root",
        "full_verb": "telusukodadam",
        "telugu":    "తెల్",
        "variants":  ["tel", "telu", "teli"],
        "example":   "teliyadu = don't know"
    },
    "bagun": {
        "meaning":   "be good/fine",
        "type":      "verb_root",
        "full_verb": "bagundadam",
        "telugu":    "బాగున్",
        "variants":  ["bagun", "baag"],
        "example":   "bagunnanu = I am fine"
    },
    "un": {
        "meaning":   "be/exist/stay",
        "type":      "verb_root",
        "full_verb": "undadam",
        "telugu":    "ఉన్",
        "variants":  ["un", "und", "unn"],
        "example":   "unnanu = I am here"
    },

    # ── TENSE MARKERS ─────────────────────────────────────────

    "tunna": {
        "meaning":       "present continuous (am/is/are doing)",
        "type":          "tense_marker",
        "tense":         "present_continuous",
        "telugu":        "తున్న",
        "variants":      ["tunna", "stunna", "tuna"],
        "english_equiv": "-ing",
        "example":       "chestunnanu = I am doing"
    },
    "anu": {
        "meaning":       "past tense (I did)",
        "type":          "tense_marker",
        "tense":         "past",
        "telugu":        "ను",
        "variants":      ["anu", "enu", "inu"],
        "english_equiv": "-ed",
        "example":       "chesanu = I did"
    },
    "taanu": {
        "meaning":       "future tense (will do)",
        "type":          "tense_marker",
        "tense":         "future",
        "telugu":        "తాను",
        "variants":      ["taanu", "tanu", "taa"],
        "english_equiv": "will",
        "example":       "chestanu = I will do"
    },
    "ali": {
        "meaning":       "obligation (must/should/need to)",
        "type":          "tense_marker",
        "tense":         "obligation",
        "telugu":        "అలి",
        "variants":      ["ali", "aali"],
        "english_equiv": "must/should",
        "example":       "cheyali = must do"
    },
    "indi": {
        "meaning":       "completed action (it happened)",
        "type":          "tense_marker",
        "tense":         "perfect",
        "telugu":        "ఇంది",
        "variants":      ["indi", "ndi"],
        "english_equiv": "has/have happened",
        "example":       "ayindi = it happened/it is done"
    },

    # ── PERSON/NUMBER SUFFIXES ─────────────────────────────────

    "nu": {
        "meaning":       "I / first person singular",
        "type":          "person_suffix",
        "person":        "1st",
        "number":        "singular",
        "telugu":        "ను",
        "variants":      ["nu", "nanu"],
        "english_equiv": "I",
        "example":       "chestunnanu = I am doing"
    },
    "am": {
        "meaning":       "we / first person plural",
        "type":          "person_suffix",
        "person":        "1st",
        "number":        "plural",
        "telugu":        "అం",
        "variants":      ["am", "aam"],
        "english_equiv": "we",
        "example":       "chestunnaam = we are doing"
    },
    "av": {
        "meaning":       "you / second person informal",
        "type":          "person_suffix",
        "person":        "2nd",
        "number":        "singular",
        "telugu":        "అవ్",
        "variants":      ["av", "ava", "avaa"],
        "english_equiv": "you (informal)",
        "example":       "chestunnav = you are doing"
    },
    "aru": {
        "meaning":       "they/you (formal) / third or second person plural",
        "type":          "person_suffix",
        "person":        "3rd or 2nd formal",
        "number":        "plural",
        "telugu":        "అరు",
        "variants":      ["aru", "ru", "aru"],
        "english_equiv": "they / you (formal)",
        "example":       "chestunnaru = they/you(formal) are doing"
    },
    "di": {
        "meaning":       "she/it / third person feminine/neuter",
        "type":          "person_suffix",
        "person":        "3rd",
        "number":        "singular",
        "telugu":        "ది",
        "variants":      ["di", "adi"],
        "english_equiv": "she/it",
        "example":       "chestundhi = she is doing"
    },

    # ── CASE SUFFIXES (Postpositions) ──────────────────────────

    "ku": {
        "meaning":       "to/for (dative case)",
        "type":          "case_suffix",
        "case":          "dative",
        "telugu":        "కు",
        "variants":      ["ku", "ki", "ko"],
        "english_equiv": "to / for",
        "example":       "naku = to me | neeku = to you"
    },
    "lo": {
        "meaning":       "in/inside/within (locative case)",
        "type":          "case_suffix",
        "case":          "locative",
        "telugu":        "లో",
        "variants":      ["lo", "loni"],
        "english_equiv": "in / inside",
        "example":       "illlo = inside the house"
    },
    "tho": {
        "meaning":       "with/using (instrumental case)",
        "type":          "case_suffix",
        "case":          "instrumental",
        "telugu":        "తో",
        "variants":      ["tho", "to"],
        "english_equiv": "with / using",
        "example":       "nnutho = with me"
    },
    "ki": {
        "meaning":       "to/towards (directional dative)",
        "type":          "case_suffix",
        "case":          "dative_directional",
        "telugu":        "కి",
        "variants":      ["ki", "ku"],
        "english_equiv": "to / towards",
        "example":       "ooruki = towards the town"
    },
    "ni": {
        "meaning":       "object marker (accusative case)",
        "type":          "case_suffix",
        "case":          "accusative",
        "telugu":        "ని",
        "variants":      ["ni", "ni"],
        "english_equiv": "(direct object)",
        "example":       "nanu = me (as object)"
    },
    "kosam": {
        "meaning":       "for the sake of / because of",
        "type":          "case_suffix",
        "case":          "benefactive",
        "telugu":        "కోసం",
        "variants":      ["kosam", "kosam"],
        "english_equiv": "for / because of",
        "example":       "neekosam = for you"
    },
    "nundi": {
        "meaning":       "from (ablative case)",
        "type":          "case_suffix",
        "case":          "ablative",
        "telugu":        "నుండి",
        "variants":      ["nundi", "nincchi"],
        "english_equiv": "from",
        "example":       "illanundi = from the house"
    },

    # ── QUESTION/EMPHASIS SUFFIXES ─────────────────────────────

    "aa": {
        "meaning":       "question marker (yes/no question)",
        "type":          "question_suffix",
        "telugu":        "ఆ",
        "variants":      ["aa", "a"],
        "english_equiv": "? (yes/no)",
        "example":       "chestunnava? = are you doing?"
    },
    "e": {
        "meaning":       "only/just/emphasis",
        "type":          "emphasis_suffix",
        "telugu":        "ే",
        "variants":      ["e", "ye", "te"],
        "english_equiv": "only / just",
        "example":       "okkate = only one / alone"
    },
    "nte": {
        "meaning":       "if / conditional",
        "type":          "conditional_suffix",
        "telugu":        "ంటే",
        "variants":      ["nte", "aithe", "ante"],
        "english_equiv": "if / then",
        "example":       "chesnte = if you do"
    },

    # ── HINDI MORPHEMES ────────────────────────────────────────

    "raha": {
        "meaning":       "present continuous (is doing)",
        "type":          "hindi_tense_marker",
        "language":      "hindi",
        "telugu":        "తున్న (same function as tunna)",
        "variants":      ["raha", "rahi", "rahe"],
        "english_equiv": "-ing",
        "example":       "kar raha hoon = I am doing"
    },
    "hoon": {
        "meaning":       "I am (first person to be)",
        "type":          "hindi_person_suffix",
        "language":      "hindi",
        "variants":      ["hoon", "hun"],
        "english_equiv": "I am",
    },
    "hai": {
        "meaning":       "is/are (third person to be)",
        "type":          "hindi_tense_suffix",
        "language":      "hindi",
        "variants":      ["hai", "hain"],
        "english_equiv": "is/are",
    },
    "ne": {
        "meaning":       "past agent marker (I/he/she did)",
        "type":          "hindi_case_suffix",
        "language":      "hindi",
        "variants":      ["ne"],
        "english_equiv": "(past subject marker)",
        "example":       "maine kiya = I did"
    },

    # ── COMMON PREFIXES ────────────────────────────────────────

    "a": {
        "meaning":       "that/those (demonstrative prefix)",
        "type":          "demonstrative_prefix",
        "telugu":        "అ",
        "variants":      ["a", "aa"],
        "english_equiv": "that",
        "example":       "atanu = that man (he)"
    },
    "i": {
        "meaning":       "this/these (proximate demonstrative)",
        "type":          "demonstrative_prefix",
        "telugu":        "ఇ",
        "variants":      ["i", "ee", "e"],
        "english_equiv": "this",
        "example":       "idi = this thing"
    },
    "e": {
        "meaning":       "which/what (interrogative prefix)",
        "type":          "interrogative_prefix",
        "telugu":        "ఏ",
        "variants":      ["e", "em", "ela", "ekkada"],
        "english_equiv": "which/what",
        "example":       "evaru = who | ekkada = where"
    },
}


# ═══════════════════════════════════════════════════════════════
# SYLLABLE PATTERNS IN TELUGU
# How to split a Telugu/Tenglish word into syllables
# ═══════════════════════════════════════════════════════════════

TELUGU_SYLLABLE_PATTERNS = [
    # Consonant clusters that should NOT be split
    "str", "sth", "chr", "shr", "spr", "ngr",
    # Common two-consonant combos
    "nd", "nt", "mb", "ng", "nk", "st", "sh",
    "ch", "gh", "ph", "th", "dh", "kh",
    # Single consonants
    "b", "c", "d", "f", "g", "h", "j", "k", "l",
    "m", "n", "p", "q", "r", "s", "t", "v", "w",
    "x", "y", "z",
]


@dataclass
class Morpheme:
    """One meaningful piece of a word"""
    text:       str
    meaning:    str
    type:       str
    telugu:     str     = ""
    language:   str     = "telugu"
    confidence: float   = 0.0
    position:   int     = 0     # Position in original word
    is_known:   bool    = False


@dataclass
class WordDecomposition:
    """Result of splitting a word into morphemes"""
    original_word:  str
    morphemes:      list[Morpheme]  = field(default_factory=list)
    constructed_meaning: str        = ""
    confidence:     float           = 0.0
    language:       str             = "unknown"
    notes:          list[str]       = field(default_factory=list)


class MorphemeEngine:
    """
    Splits any Telugu/Tenglish/Hindi word into
    its meaningful parts and identifies each part.
    """

    def __init__(self):
        self.morphemes = TELUGU_MORPHEMES

    def decompose(self, word: str) -> WordDecomposition:
        """
        Main entry: split a word into morphemes.

        "chestunnanu" →
          [che(do) + stunna(present) + nu(I)]
          → "I am doing"
        """
        word = word.lower().strip()
        result = WordDecomposition(original_word=word)

        # ── Try full word first ──────────────────────────
        if word in self.morphemes:
            m = self.morphemes[word]
            result.morphemes.append(Morpheme(
                text        = word,
                meaning     = m["meaning"],
                type        = m["type"],
                telugu      = m.get("telugu", ""),
                confidence  = 1.0,
                is_known    = True
            ))
            result.confidence = 1.0
            result.constructed_meaning = m["meaning"]
            return result

        # ── Try greedy left-to-right morpheme matching ───
        morphemes_found = self._greedy_match(word)

        if morphemes_found:
            result.morphemes = morphemes_found
            result.confidence = sum(
                m.confidence for m in morphemes_found
            ) / len(morphemes_found)
            result.constructed_meaning = self._assemble_meaning(
                morphemes_found, word
            )
        else:
            # ── Fallback: syllable split ─────────────────
            syllables = self._split_syllables(word)
            result.notes.append(
                f"Unknown word. Syllables: {' | '.join(syllables)}"
            )
            result.confidence = 0.1

        return result

    def _greedy_match(self, word: str) -> list[Morpheme]:
        """
        Try to match morphemes from left to right.
        Longest match first (greedy).
        """
        found    = []
        position = 0
        remaining = word

        while remaining:
            best_match = None
            best_length = 0

            # Try all morphemes, find longest match
            for morph_text, morph_data in self.morphemes.items():
                # Check all variants of this morpheme
                all_forms = [morph_text] + morph_data.get("variants", [])

                for form in all_forms:
                    if (remaining.startswith(form) and
                            len(form) > best_length):
                        best_match  = (form, morph_data)
                        best_length = len(form)

            if best_match:
                form, data = best_match
                found.append(Morpheme(
                    text        = form,
                    meaning     = data["meaning"],
                    type        = data["type"],
                    telugu      = data.get("telugu", ""),
                    confidence  = 0.85,
                    position    = position,
                    is_known    = True
                ))
                remaining = remaining[best_length:]
                position += best_length
            else:
                # Can't match — consume one character
                found.append(Morpheme(
                    text        = remaining[0],
                    meaning     = "unknown",
                    type        = "unknown",
                    confidence  = 0.0,
                    position    = position,
                    is_known    = False
                ))
                remaining = remaining[1:]
                position += 1

        return found if any(m.is_known for m in found) else []

    def _assemble_meaning(
        self, morphemes: list[Morpheme], original: str
    ) -> str:
        """
        Combine morpheme meanings into a natural sentence.
        Uses grammar rules about word order.
        """
        parts = []

        # Separate by type
        verb_root   = None
        tense       = None
        person      = None
        case        = None
        emphasis    = []
        unknowns    = []

        for m in morphemes:
            if m.type == "verb_root":
                verb_root = m
            elif m.type == "tense_marker":
                tense = m
            elif m.type == "person_suffix":
                person = m
            elif m.type == "case_suffix":
                case = m
            elif m.type in ("emphasis_suffix", "question_suffix"):
                emphasis.append(m)
            elif not m.is_known:
                unknowns.append(m.text)

        # ── Build meaning from parts ──────────────────────
        if verb_root and tense and person:
            # Full verb conjugation
            meaning = (
                f"{person.meaning.split('/')[0].strip()} "
                f"{tense.meaning.split('(')[0].strip()} "
                f"{verb_root.meaning}"
            )
            parts.append(meaning)

        elif verb_root and tense:
            meaning = (
                f"{tense.meaning.split('(')[0].strip()} "
                f"{verb_root.meaning}"
            )
            parts.append(meaning)

        elif verb_root and person:
            parts.append(
                f"{person.meaning.split('/')[0].strip()} "
                f"{verb_root.meaning}"
            )

        elif verb_root:
            parts.append(verb_root.meaning)

        else:
            # Not a verb — concatenate known meanings
            for m in morphemes:
                if m.is_known:
                    parts.append(m.meaning.split("(")[0].strip())

        if emphasis:
            for e in emphasis:
                parts.append(f"[{e.meaning}]")

        if unknowns:
            parts.append(f"(unknown parts: {', '.join(unknowns)})")

        return " ".join(parts) if parts else "meaning unclear"

    def _split_syllables(self, word: str) -> list[str]:
        """Basic syllable splitter as fallback"""
        vowels   = set("aeiouáéíóú")
        syllables = []
        current   = ""

        for i, char in enumerate(word):
            current += char
            if char in vowels:
                # Check if next char starts a new syllable
                if i + 1 < len(word) and word[i+1] not in vowels:
                    syllables.append(current)
                    current = ""

        if current:
            syllables.append(current)

        return syllables if syllables else [word]
