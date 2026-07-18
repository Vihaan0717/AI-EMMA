import asyncio
import os
import pyautogui
from core.ai_engine import AIEngine

async def test_vision():
    # 1. Take a screenshot
    screenshot_path = "debug_screenshot.png"
    print(f"Taking screenshot: {screenshot_path}")
    screenshot = pyautogui.screenshot()
    screenshot.save(screenshot_path)
    
    # 2. Initialize AI Engine
    ai = AIEngine()
    await ai.initialize()
    
    # 3. Analyze using Gemma 3 (already installed)
    print("Analyzing screen with gemma3:1b...")
    result = await ai.vision_analyze(
        prompt="Describe what you see on this screen in detail.",
        image_path=screenshot_path,
        model="gemma3:1b"
    )
    
    print("\n--- VISION ANALYSIS ---")
    print(result)
    print("-----------------------\n")
    
    # Cleanup
    # os.remove(screenshot_path)

if __name__ == "__main__":
    asyncio.run(test_vision())
