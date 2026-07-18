"""
Message Formatter — Ensures messages sent to real humans
are NEVER polluted with markdown, code blocks, or symbols.
Every human channel (WhatsApp, SMS, spoken) gets clean text.
"""

import re
from enum import Enum

class OutputChannel(Enum):
    WHATSAPP   = "whatsapp"
    TELEGRAM   = "telegram"
    SMS        = "sms"
    SPOKEN     = "spoken"      # Text-to-speech
    DASHBOARD  = "dashboard"   # Streamlit (markdown OK here)
    OBSIDIAN   = "obsidian"    # Markdown OK here too

class MessageFormatter:
    # Pre-compiled regex patterns for performance
    _RE_HEADERS      = re.compile(r'#{1,6}\s*')
    _RE_BOLD_ITALIC  = re.compile(r'\*{1,3}|_{1,3}')
    _RE_CODE_BLOCK   = re.compile(r'```[\s\S]*?```')
    _RE_INLINE_CODE  = re.compile(r'`[^`]*`')
    _RE_BULLETS      = re.compile(r'^\s*[-*+]\s+', re.MULTILINE)
    _RE_NUM_LISTS    = re.compile(r'^\s*\d+\.\s+', re.MULTILINE)
    _RE_HTML_TAGS    = re.compile(r'<[^>]+>')
    _RE_HORIZ_RULES  = re.compile(r'---+|===+')
    _RE_EXTRA_NL     = re.compile(r'\n{3,}')
    _RE_URLS         = re.compile(r'http\S+')
    _RE_SENTENCES    = re.compile(r'(?<=[.!?])\s+')

    @staticmethod
    def strip_markdown(text: str) -> str:
        """Remove ALL markdown symbols from text."""
        # Remove headers (### ## #)
        text = MessageFormatter._RE_HEADERS.sub('', text)
        # Remove bold/italic (** * __ _)
        text = MessageFormatter._RE_BOLD_ITALIC.sub('', text)
        # Remove code blocks (``` `)
        text = MessageFormatter._RE_CODE_BLOCK.sub('', text)
        text = MessageFormatter._RE_INLINE_CODE.sub('', text)
        # Remove bullet dashes that look robotic
        text = MessageFormatter._RE_BULLETS.sub('', text)
        # Remove numbered lists formatting (keep numbers, remove dots)
        text = MessageFormatter._RE_NUM_LISTS.sub('', text)
        # Remove HTML tags if any
        text = MessageFormatter._RE_HTML_TAGS.sub('', text)
        # Remove horizontal rules
        text = MessageFormatter._RE_HORIZ_RULES.sub('', text)
        # Clean extra whitespace
        text = MessageFormatter._RE_EXTRA_NL.sub('\n\n', text)
        return text.strip()

    @staticmethod
    def format_for_whatsapp(text: str) -> str:
        """
        WhatsApp supports: *bold* _italic_ ~strikethrough~ ```code```
        But we keep it minimal and human for family messages.
        """
        clean = MessageFormatter.strip_markdown(text)
        # WhatsApp uses single * for bold — only for truly important words
        # We keep it plain by default for family/elder messages
        return clean

    @staticmethod
    def format_for_spoken(text: str) -> str:
        """Remove everything that sounds weird when spoken aloud."""
        clean = MessageFormatter.strip_markdown(text)
        # Remove URLs
        clean = MessageFormatter._RE_URLS.sub('a link', clean)
        # Spell out abbreviations
        clean = clean.replace("e.g.", "for example")
        clean = clean.replace("i.e.", "that is")
        return clean

    @staticmethod
    def format_for_channel(text: str, channel: OutputChannel) -> str:
        """Auto-select correct formatter based on destination."""
        if channel in [OutputChannel.DASHBOARD, OutputChannel.OBSIDIAN]:
            return text  # Markdown is fine here
        elif channel == OutputChannel.WHATSAPP or channel == "whatsapp":
            return MessageFormatter.format_for_whatsapp(text)
        elif channel == OutputChannel.SPOKEN or channel == "spoken":
            return MessageFormatter.format_for_spoken(text)
        else:
            return MessageFormatter.strip_markdown(text)

    @staticmethod
    def split_into_whatsapp_bubbles(text: str, max_chars: int = 200) -> list[str]:
        """
        Break long messages into natural WhatsApp bubbles.
        Humans don't send one massive wall of text.
        """
        clean    = MessageFormatter.format_for_whatsapp(text)
        # Split by sentence boundaries but keep the punctuation
        sentences = MessageFormatter._RE_SENTENCES.split(clean)
        bubbles, current = [], ""

        for sentence in sentences:
            if len(current) + len(sentence) < max_chars:
                current += (" " if current else "") + sentence
            else:
                if current:
                    bubbles.append(current.strip())
                current = sentence

        if current:
            bubbles.append(current.strip())

        return bubbles if bubbles else [clean]
