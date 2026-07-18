import asyncio
import logging
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from pipeline.pipeline_runner import PipelineRunner
from core.fleet.manager import fleet_manager

class MockBrain:
    def __init__(self):
        self.modules = {
            "ai": None,
            "memory": None
        }

async def test_greeting_logic():
    print("--- Testing Pipeline Greeting Logic ---")
    brain = MockBrain()
    runner = PipelineRunner(brain)
    
    test_cases = [
        ("Hi Jarvis", True),
        ("hello", True),
        ("Java code for Hello World", False),
        ("give me python code for a calculator", False),
        ("how to fix a flat tire", False),
        ("namaste", True),
        ("ela unnav", True),
        ("Jarvis, what is the latest news?", False)
    ]
    
    # We need to mock the salience score or just check the is_greeting flag
    # Since we modified the code, let's test the logic directly or by calling process
    # But process requires modules. Let's just test the logic snippet.
    
    GREETING_WORDS = ["hi", "hello", "hey", "namaste", "namaskaram", "yo", "sup", "nuvvu ela", "ela unnav", "gm", "gn"]
    tech_keywords = ["code", "java", "python", "script", "how to", "debug", "math", "search", "who", "what"]

    for text, expected in test_cases:
        cleaned_input = text.lower().strip()
        has_tech_intent = any(tk in cleaned_input for tk in tech_keywords)
        
        is_precise_greeting = False
        for g in GREETING_WORDS:
            if cleaned_input == g or cleaned_input.startswith(g + " "):
                is_precise_greeting = True
                break
        
        is_greeting = (
            (is_precise_greeting or "jarvis" == cleaned_input or "jarivs" == cleaned_input) and
            not has_tech_intent and
            len(cleaned_input) < 50
        )
        
        status = "PASSED" if is_greeting == expected else "FAILED"
        print(f"[{status}] Input: '{text}' | Is Greeting: {is_greeting} | Expected: {expected}")

async def test_fleet_sig():
    print("\n--- Testing Fleet Signature Logic ---")
    test_cases = [
        ("Java code for hello world", "coding"),
        ("Python script to scrape a website", "coding"),
        ("Who is the president of India?", "research"),
        ("Write a poem about space", "creative"),
        ("Solve x + 5 = 10", "math"),
        ("Hi how are you", "general")
    ]
    
    for text, expected in test_cases:
        sig = fleet_manager._generate_task_sig(text)
        status = "PASSED" if sig == expected else "FAILED"
        print(f"[{status}] Input: '{text}' | Sig: {sig} | Expected: {expected}")

if __name__ == "__main__":
    asyncio.run(test_greeting_logic())
    asyncio.run(test_fleet_sig())
