import asyncio
import os
import pyautogui
from core.ai_engine import AIEngine

async def test_coordinate_extraction():
    # 1. Take a screenshot
    screenshot_path = "coord_test.png"
    print(f"Taking screenshot: {screenshot_path}")
    screenshot = pyautogui.screenshot()
    screenshot.save(screenshot_path)
    
    # 2. Initialize AI Engine
    ai = AIEngine()
    await ai.initialize()
    
    # 3. Try to find a common element (e.g., the Windows Start button or a specific icon)
    print("Analyzing screen for 'Windows Start Button' using moondream...")
    prompt = "Where is the Windows Start button? Provide coordinates in [ymin, xmin, ymax, xmax] format."
    
    result = await ai.vision_analyze(
        prompt=prompt,
        image_path=screenshot_path,
        model="moondream"
    )
    
    print("\n--- VISION COORDINATES ---")
    print(result)
    print("--------------------------\n")
    
    # Cleanup
    # os.remove(screenshot_path)

if __name__ == "__main__":
    asyncio.run(test_coordinate_extraction())
