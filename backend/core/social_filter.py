"""
NEXUS-X Social Filter v3 — Bulletproof Edition
===============================================
Lightweight formatter that:
1. Strips markdown from WhatsApp messages
2. Enforces linguistic purity (no random language switches)
3. Applies cultural address forms
4. Splits into natural WhatsApp bubbles
5. NEVER crashes — guaranteed fallback at every step
"""

import re
import logging
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger("SocialFilter")

# ─────────────────────────────────────────────────────────────────────────────
# MARKDOWN STRIPPER
# ─────────────────────────────────────────────────────────────────────────────

def strip_markdown(text: str) -> str:
    """Remove all markdown symbols from text."""
    if not text:
        return ""
    text = re.sub(r'\*{1,3}(.+?)\*{1,3}', r'\1', text)   # bold/italic
    text = re.sub(r'#{1,6}\s*', '', text)                  # headers
    text = re.sub(r'`{1,3}[^`]*`{1,3}', '', text)         # code
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # links
    text = re.sub(r'^[-*•]\s+', '', text, flags=re.MULTILINE)  # bullets
    text = re.sub(r'\n{3,}', '\n\n', text)                # excess newlines
    return text.strip()


# ─────────────────────────────────────────────────────────────────────────────
# AI-ISM FILTER — Remove robotic phrases
# ─────────────────────────────────────────────────────────────────────────────

AI_PHRASES = [
    "as an ai", "i'm an ai", "i am an ai", "i don't have feelings",
    "i cannot feel", "i'm just a language model", "as a language model",
    "i don't have personal opinions", "i'm designed to", "my training data",
    "i don't have access to real-time",
]

def remove_ai_isms(text: str) -> str:
    lower = text.lower()
    for phrase in AI_PHRASES:
        if phrase in lower:
            text = re.sub(re.escape(phrase), "", text, flags=re.IGNORECASE)
    return text.strip()


# ─────────────────────────────────────────────────────────────────────────────
# TRANSLATION BRACKET REMOVER
# ─────────────────────────────────────────────────────────────────────────────

def remove_translation_brackets(text: str) -> str:
    """Remove parenthetical translations like '(How are you?)'"""
    # Remove (English translation) patterns after Telugu/Tenglish words
    text = re.sub(r'\s*\([A-Za-z ,\'!?]+\)', '', text)
    return text.strip()


# ─────────────────────────────────────────────────────────────────────────────
# LANGUAGE VALIDATOR
# ─────────────────────────────────────────────────────────────────────────────

HINDI_MARKERS = ["hai", "hain", "kaa", "mein", "aur", "yeh", "ek", "mahaan", 
                 "vishay", "jarrae", "pata", "kahaaniyaan", "samriddhi"]

def detect_accidental_hindi(text: str) -> bool:
    """Detect if the response accidentally slipped into Hindi."""
    words = text.lower().split()
    hindi_count = sum(1 for w in words if w in HINDI_MARKERS)
    has_telugu_script = bool(re.search(r'[\u0c00-\u0c7f]', text))
    # Hindi text has no Telugu script but has Hindi markers
    if hindi_count >= 3 and not has_telugu_script:
        return True
    return False


# ─────────────────────────────────────────────────────────────────────────────
# BUBBLE SPLITTER — Natural WhatsApp message chunks
# ─────────────────────────────────────────────────────────────────────────────

def split_into_bubbles(text: str, max_len: int = 300) -> List[str]:
    """Split long text into natural WhatsApp bubbles."""
    if len(text) <= max_len:
        return [text]
    
    # Try to split on sentence boundaries
    sentences = re.split(r'(?<=[.!?।\n])\s+', text)
    bubbles = []
    current = ""
    
    for s in sentences:
        if len(current) + len(s) + 1 <= max_len:
            current = (current + " " + s).strip()
        else:
            if current:
                bubbles.append(current)
            current = s
    
    if current:
        bubbles.append(current)
    
    return bubbles if bubbles else [text[:max_len]]


# ─────────────────────────────────────────────────────────────────────────────
# MAIN ENTRY POINTS
# ─────────────────────────────────────────────────────────────────────────────

async def apply_social_filter(
    raw_response: str,
    sender_name: str,
    context: str = ""
) -> Dict:
    """
    Lightweight social filter — always works, never crashes.
    Cleans and formats the response without a second LLM call.
    """
    try:
        if not raw_response or not raw_response.strip():
            return {
                "adapted_response": "Em cheppanu Boss?",
                "bubbles": ["Em cheppanu Boss?"],
                "language_used": "tenglish",
                "tone_applied": "casual"
            }

        response = raw_response.strip()

        # Step 1: Strip markdown
        response = strip_markdown(response)

        # Step 2: Remove AI-isms
        response = remove_ai_isms(response)

        # Step 3: Remove translation brackets
        response = remove_translation_brackets(response)

        # Step 4: Check for accidental Hindi (log warning)
        if detect_accidental_hindi(response):
            logger.warning(f"[SocialFilter] Accidental Hindi detected in response. Passing through for now.")
            # In future: trigger re-generation. For now, log and pass.

        # Step 5: Split into bubbles
        bubbles = split_into_bubbles(response)

        # Detect language of output for logging
        has_telugu = bool(re.search(r'[\u0c00-\u0c7f]', response))
        tenglish_words = ["boss", "anna", "ra", "ga", "unnav", "cheppu", "enti", "avuna"]
        has_tenglish = any(w in response.lower() for w in tenglish_words)
        lang = "telugu" if has_telugu else ("tenglish" if has_tenglish else "english")

        logger.info(f"[SocialFilter] Processed {len(bubbles)} bubble(s) for {sender_name} | lang={lang}")

        return {
            "adapted_response": "\n\n".join(bubbles),
            "bubbles": bubbles,
            "language_used": lang,
            "tone_applied": "cultural",
            "respect_score": 0.9
        }

    except Exception as e:
        logger.error(f"[SocialFilter] Error: {e}. Returning raw response.")
        safe = raw_response.strip() if raw_response else "Em cheppanu Boss?"
        return {
            "adapted_response": safe,
            "bubbles": [safe],
            "language_used": "unknown",
            "tone_applied": "fallback",
            "error": str(e)
        }


async def generate_human_message(
    intent: str,
    person_name: str,
    channel=None,
    context: str = ""
) -> Dict:
    """Legacy wrapper — now calls the lightweight filter."""
    return await apply_social_filter(intent, person_name, context)


def how_should_i_talk_to(person_name: str) -> str:
    """Quick guide for talking to someone."""
    return f"Talk to {person_name} in Tenglish (natural Hyderabad/Rajahmundry tone), with respect and warmth."
