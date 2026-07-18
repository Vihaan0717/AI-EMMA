import sys
import os
from pathlib import Path
import json

# Add project root to sys.path
root = Path(r'c:\Users\anger\Desktop\JARVIS_Project')
sys.path.append(str(root))

from brain.learning.learner import NexusLearner

def ingest():
    # Force UTF-8 for printing if possible
    if sys.stdout.encoding != 'utf-8':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    learner = NexusLearner(brain_file=str(root / 'data' / 'telugu_dna.json'))
    
    godavari_data = [
        ("Andoy / Andi", "Respectful suffixes added to sentences for extreme politeness", "polite", "East Godavari"),
        ("Thirakaatam", "Chaos / Complicated problem / Confusion", "slang", "East Godavari"),
        ("Gaduggaay", "Someone who is very smart, clever, or overly sharp/witty", "slang", "East Godavari"),
        ("Vetakaaram", "High-level sarcasm or mockery (The trademark of Godavari people)", "slang", "East Godavari"),
        ("Bheebhatsanga", "Extremely / Intensely / Brute force", "slang", "East Godavari"),
        ("Allaatam", "Trouble / Stress / Worry", "slang", "East Godavari"),
        ("Pottikkalu", "Traditional Jackfruit leaf steamed idli (authentic delicacy)", "vocabulary", "East Godavari"),
        ("Panasapottu Koora", "Authentic Jackfruit curry (Godavari special)", "vocabulary", "East Godavari"),
        ("Viyyangaru", "Co-father-in-law (formal relative term)", "vocabulary", "East Godavari"),
        ("Peetala meedha nunchi lechipovadam", "Dramatic hyperbole for walking out of a ceremony in protest", "slang", "East Godavari"),
        ("Pootharekulu", "Famous paper-sweet from Atreyapuram", "vocabulary", "East Godavari"),
        ("Andoi", "Respectful way of saying 'Hey' or addressing someone", "polite", "East Godavari"),
        ("Mandi", "Yes sir / Yes ma'am", "polite", "East Godavari"),
        ("Maku", "To us (dialect specific pronunciation)", "slang", "East Godavari"),
        ("Naligipovadam", "To be crushed, exhausted or worn out by travel/work", "slang", "East Godavari"),
        ("Gummarekki", "Suddenly / Excessively (Shared with Hyd but used differently here)", "slang", "East Godavari"),
        ("Peechi", "Stubbornness / Creating trouble", "slang", "East Godavari"),
        ("Saranjama", "Arrangements / Preparation / Luggage", "slang", "East Godavari")
    ]

    print(f"--- Ingesting {len(godavari_data)} East Godavari Patterns ---")
    for phrase, meaning, context, dialect in godavari_data:
        try:
            res = learner.learn(phrase, meaning, context, dialect)
            # Only print safe characters to avoid console errors
            safe_res = "".join(c if ord(c) < 128 else '?' for c in res)
            print(safe_res)
        except Exception as e:
            print(f"Failed to learn {phrase}: {e}")

if __name__ == "__main__":
    ingest()
