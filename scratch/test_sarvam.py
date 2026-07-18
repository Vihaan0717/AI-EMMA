import asyncio
import os
from dotenv import load_dotenv
import sys
import os
sys.path.append(os.getcwd())
from core.ai_engine import AIEngine

async def test():
    load_dotenv()
    engine = AIEngine()
    await engine.initialize()
    
    print(f"Testing Sarvam-1 (Indic Fast: {engine.indic_fast})")
    response = await engine.generate("Annaya, ela unnaru?", system="Respond in fluent Telugu.", use_fast=True)
    with open("scratch/test_sarvam.txt", "w", encoding="utf-8") as f:
        f.write(response)
    print(f"Response saved to scratch/test_sarvam.txt")
    
    await engine.close()

if __name__ == "__main__":
    asyncio.run(test())
