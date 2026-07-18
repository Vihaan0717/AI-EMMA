import asyncio
import os
from core.ai_engine import AIEngine

async def test_simple_vision():
    screenshot_path = "coord_test.png" # reuse previous
    
    ai = AIEngine()
    await ai.initialize()
    
    print("Asking moondream to describe the screen...")
    result = await ai.vision_analyze(
        prompt="Describe this screenshot. What application is open?",
        image_path=screenshot_path,
        model="moondream"
    )
    
    print("\n--- DESCRIPTION ---")
    print(result)
    print("-------------------\n")

if __name__ == "__main__":
    asyncio.run(test_simple_vision())
