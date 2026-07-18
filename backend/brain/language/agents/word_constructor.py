"""
═══════════════════════════════════════════════════════════════
WORD CONSTRUCTOR AGENT
═══════════════════════════════════════════════════════════════
The 'Lego' engine of JARVIS Brain.
Deconstructs ANY word into its components:
  [Root Word] + [Suffix/Case] + [Context/Intent]
═══════════════════════════════════════════════════════════════
"""

import logging
from ..grammar.telugu_grammar import TELUGU_CASE_MARKERS, VERB_TENSES

logger = logging.getLogger('WordConstructor')

class WordConstructorAgent:
    def __init__(self):
        self.telugu_suffixes = self._collect_suffixes()

    def _collect_suffixes(self):
        suffixes = []
        for case in TELUGU_CASE_MARKERS.values():
            suffixes.extend(case)
        for tense in VERB_TENSES.values():
            suffixes.append(tense['suffix'])
        
        # Add Tenglish versions
        suffixes.extend(["tunnav", "tunna", "shanu", "tanu", "ndi"])
        return sorted(suffixes, key=len, reverse=True)

    def deconstruct(self, word: str, lang: str = "telugu") -> dict:
        """
        Breaks down a word into parts.
        Example: 'chestunnav' -> root='ches', suffix='tunnav'
        """
        word = word.strip()
        result = {
            "original": word,
            "root": word,
            "suffix": None,
            "parts": [],
            "meaning_hint": None
        }

        # Simplified greedy suffix matching
        for suffix in self.telugu_suffixes:
            if word.endswith(suffix):
                result["root"] = word[:-len(suffix)]
                result["suffix"] = suffix
                result["parts"] = [result["root"], suffix]
                break
        
        return result

    def reconstruct(self, root: str, suffix: str) -> str:
        """Combines parts into a valid word"""
        return root + suffix
