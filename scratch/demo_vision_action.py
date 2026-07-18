import asyncio
import os
import time
import pyautogui
from brain.agents.vision_hand_agent import VisionHandAgent
from services.hand_service import HandService

# Disable failsafe for this specific demo
pyautogui.FAILSAFE = False

async def demo_task():
    pyautogui.FAILSAFE = False
    vision_hand = VisionHandAgent()
    hands = HandService()
    
    print("JARVIS: Starting Google vision task...")
    
    import webbrowser
    print("Opening Browser to Google...")
    webbrowser.open('https://www.google.com')
    
    print("Waiting for page to load (5s)...")
    await asyncio.sleep(5)
    
    # 2. Use Vision to find the search bar
    print("JARVIS is scanning for the Google search bar...")
    result = await vision_hand.type_in_element("the main Google search input box", "Swiggy Hyderabad")
    
    print(f"Action Result: {result}")
    
    if "Successfully" in result:
        print("Finalizing action: Pressing Enter...")
        pyautogui.press('enter')
        await asyncio.sleep(3)
        
        # 3. Try to find the Swiggy website link
        print("Scanning for the Swiggy website link in results...")
        click_res = await vision_hand.find_and_click("the main Swiggy website link result")
        print(f"Click Result: {click_res}")
    
    # 4. Final Screenshot
    screenshot_path = "demo_result_google.png"
    pyautogui.screenshot().save(screenshot_path)
    print(f"Screenshot saved: {screenshot_path}")

if __name__ == "__main__":
    asyncio.run(demo_task())
