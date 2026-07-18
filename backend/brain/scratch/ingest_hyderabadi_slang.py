import sys
import os
from pathlib import Path

# Add project root to sys.path
root = Path(r'c:\Users\anger\Desktop\JARVIS_Project')
sys.path.append(str(root))

from brain.learning.learner import NexusLearner

def ingest():
    learner = NexusLearner(brain_file=str(root / 'data' / 'telugu_dna.json'))
    
    slang_data = [
        ("Baigan ke baatan", "Nonsense or useless talk", "slang", "Hyderabadi"),
        ("Light theesko", "Let it go / Take it easy / Ignore it", "slang", "Hyderabadi"),
        ("Chalta ka", "Get moving / Let's start moving", "slang", "Hyderabadi"),
        ("Barabar", "Exactly / Correctly / Perfectly", "slang", "Hyderabadi"),
        ("Kirraque", "Awesome / Intense / High quality", "slang", "Hyderabadi"),
        ("Dhaba dhaba", "Quickly / Fast", "slang", "Hyderabadi"),
        ("Thopu", "A big shot / Expert / High performer", "slang", "Hyderabadi"),
        ("Dimaak kharaab", "Annoyed / Mind spinning / Frustrated", "slang", "Hyderabadi"),
        ("Khaali peeli", "For no reason / Uselessly / Without cause", "slang", "Hyderabadi"),
        ("Bheja fry", "Brain fried / Mentally exhausted", "slang", "Hyderabadi"),
        ("Muttukoledu", "Didn't even touch (usually books or task)", "tutorial_patterns", "Hyderabadi"),
        ("Muchatlu", "Chats / Gossip / Idle talk", "slang", "Hyderabadi"),
        ("Giraaki", "Customer / Client", "slang", "Hyderabadi"),
        ("Mungi povaali", "Move forward / Rush inside / Advance", "slang", "Hyderabadi"),
        ("Thassa dhiya", "An expression of surprise or frustration (Damn it)", "slang", "Hyderabadi"),
        ("Lathkor", "Cheap / Worthless / Low quality person or thing", "slang", "Hyderabadi"),
        ("Scene sitaar", "Situation ruined / Plan failed / Total mess", "slang", "Hyderabadi"),
        ("Gummarekki", "Suddenly / Excessively / Sleeping like a log", "slang", "Hyderabadi"),
        ("Boti boti", "Meat pieces / Small bit / Barely any profit", "slang", "Hyderabadi"),
        ("Murgipoyinav", "Rotted away / Staying idle too long", "slang", "Hyderabadi"),
        ("Cuttingisthunnav", "Giving attitude / Showing off", "slang", "Hyderabadi"),
        ("Hau", "Yes / Yeah", "slang", "Hyderabadi"),
        ("Kaiku", "Why", "slang", "Hyderabadi")
    ]

    print(f"--- Ingesting {len(slang_data)} Hyderabadi Slang Patterns ---")
    for phrase, meaning, context, dialect in slang_data:
        res = learner.learn(phrase, meaning, context, dialect)
        print(res)

if __name__ == "__main__":
    ingest()
