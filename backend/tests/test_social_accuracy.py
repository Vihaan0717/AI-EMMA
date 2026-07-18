"""
Social Accuracy Tests — Automatically catches wrong tone,
wrong language, markdown leaks, and disrespectful address forms.
Run: pytest tests/test_social_accuracy.py -v
"""

import pytest
import re
import sys
import os

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.message_formatter import MessageFormatter, OutputChannel
from core.language_detector import get_correct_address_form, LANGUAGE_PROFILES

# ── Test 1: No Markdown in Human Messages ────────────────────────────────────
class TestMarkdownStripping:

    def test_strips_headers(self):
        text   = "### Hello Annaya\n## How are you?"
        result = MessageFormatter.strip_markdown(text)
        assert "###" not in result
        assert "##" not in result

    def test_strips_bold(self):
        text   = "**Annaya** how are you *doing*?"
        result = MessageFormatter.strip_markdown(text)
        assert "**" not in result
        assert result == "Annaya how are you doing?"

    def test_strips_code_blocks(self):
        text   = "Here is the answer:\n```python\nprint('hello')\n```"
        result = MessageFormatter.strip_markdown(text)
        assert "```" not in result

    def test_whatsapp_bubbles_are_short(self):
        long_text = "Hello. " * 50
        bubbles   = MessageFormatter.split_into_whatsapp_bubbles(long_text, max_chars=200)
        for bubble in bubbles:
            assert len(bubble) <= 250  # Allow slight overflow at sentence boundaries


# ── Test 2: Correct Address Forms ────────────────────────────────────────────
class TestAddressForms:

    def test_annaya_telugu_address(self):
        form = get_correct_address_form("Ravi", "annaya", "telugu")
        assert "Annaya" in form

    def test_teacher_address_contains_sir_or_madam(self):
        form = get_correct_address_form("Kumar", "teacher", "english")
        assert "Sir" in form or "Ma'am" in form or "Madam" in form

    def test_grandparent_telugu_address(self):
        form = get_correct_address_form("Thatha", "grandparent", "telugu")
        assert "Thatha" in form or "Ammamma" in form or "Garru" in form or "garru" in form


# ── Test 3: Disrespect Detection ──────────────────────────────────────────────
class TestDisrespectDetection:

    DISRESPECTFUL_TO_ANNAYA = [
        "Nee enti ra",      # Using 'Nee' to elder is wrong
        "Boss",             # Should never call Annaya 'Boss'
        "###",              # Markdown leak
        "**",               # Markdown leak
    ]

    def test_no_disrespectful_terms_in_annaya_message(self):
        """Ensure the generated message doesn't contain disrespectful terms."""
        from core.correct_examples import CORRECT_EXAMPLES
        annaya_msg = " ".join(CORRECT_EXAMPLES["annaya_normal"]["bubbles"])
        for bad_term in self.DISRESPECTFUL_TO_ANNAYA:
            # We check case insensitive
            assert bad_term.lower() not in annaya_msg.lower(), f"Found disrespectful term: '{bad_term}'"

    def test_no_markdown_in_whatsapp_examples(self):
        """All correct examples must be markdown-free."""
        from core.correct_examples import CORRECT_EXAMPLES
        markdown_pattern = re.compile(r'#{1,6}\s|[\*_]{2,}|```')
        for key, example in CORRECT_EXAMPLES.items():
            for bubble in example["bubbles"]:
                assert not markdown_pattern.search(bubble), \
                    f"Markdown found in '{key}': {bubble}"


# ── Test 4: Language Consistency ─────────────────────────────────────────────
class TestLanguageConsistency:

    def test_telugu_profile_has_elder_form(self):
        assert "example_elder" in LANGUAGE_PROFILES["telugu"]

    def test_telugu_never_nee_for_elders(self):
        """Telugu elder form should never use 'Nee' (disrespectful)."""
        elder_example = LANGUAGE_PROFILES["telugu"]["example_elder"]
        # 'Nee' alone as a word (not part of 'Meeru' etc.)
        assert " Nee " not in f" {elder_example} "

    def test_hindi_elder_uses_aap(self):
        elder_example = LANGUAGE_PROFILES["hindi"]["example_elder"]
        assert "aap" in elder_example.lower() or "Aap" in elder_example
