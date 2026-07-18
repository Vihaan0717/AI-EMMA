import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from arion.agents.language_engine import LanguageEngine
from arion.agents.comprehension_engine import ComprehensionEngine
from arion.agents.orchestrator import Orchestrator
from arion.core.message_bus import Channel, Message

def build_word_index(vocab: dict) -> dict:
    index = {}
    for category, entries in vocab.items():
        if category == "meta": continue
        if isinstance(entries, dict):
            for word, meaning in entries.items():
                index[word.lower()] = meaning
    return index

async def test_pipeline():
    print("=== ARION PIPELINE TEST ===\n")
    
    le = LanguageEngine()
    ce = ComprehensionEngine()
    
    # Build complete word index for mirroring A2
    te_index = build_word_index(le.vocab_te)
    hi_index = build_word_index(le.vocab_hi)
    
    test_cases = [
        ("ame chasthunav", "What are you doing?"),
        ("chelli yala vundhe?", "How is your younger sister doing?"),
        ("amma yala vunnaru?", "How is mom doing?"),
        ("health yala vundhe?", "How is your health?"),
        ("ippudu em chesthunnav", "What are you doing right now?"),
        ("huhum okay", "Hmm, okay"),
        ("bore ga undi", "Feeling bored"),
        ("kya kar raha hai", "What are you doing?"),
    ]
    
    for text, expected_semantic in test_cases:
        print(f"--- Input: '{text}' ---")
        
        # 1. Normalize (A1)
        norm = le._normalize_script(text)
        print(f"A1 Normalize: script={norm['script']} tokens={norm['tokens']}")
        
        # 2. Semantic Bridge (A2 Mock + A3)
        decoded = {}
        for token in norm['tokens']:
            token_lower = token.lower()
            if token_lower in te_index:
                decoded[token_lower] = {"meaning": te_index[token_lower]}
            elif token_lower in hi_index:
                decoded[token_lower] = {"meaning": hi_index[token_lower]}
        
        semantic = await ce._build_semantic_english(text, decoded)
        print(f"A3 Semantic: '{semantic}'")
        
        # 3. Stylization (A6)
        stylized = le._stylize_dialect(semantic, norm['script'], "neutral")
        print(f"A6 Stylized: '{stylized}'\n")

if __name__ == "__main__":
    asyncio.run(test_pipeline())
