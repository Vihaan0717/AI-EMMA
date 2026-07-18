import asyncio
import os
import time
import pyautogui
from brain.agents.autonomous_order_agent import AutonomousOrderAgent
from config.system_config import JarvisConfig

# Disable failsafe for demo stability
pyautogui.FAILSAFE = False

async def full_autonomous_demo():
    agent = AutonomousOrderAgent()
    
    print("--- JARVIS: COMMERCE MISSION START ---")
    
    # 1. Navigation
    print("Step 1: Navigating to market...")
    pyautogui.hotkey('win', 'r')
    time.sleep(1)
    pyautogui.write('https://www.google.com/search?q=best+biryani+deals+online', interval=0.05)
    pyautogui.press('enter')
    
    print("Waiting for results to load...")
    await asyncio.sleep(6)
    
    # 2. Login Check
    print("Step 2: Checking Google Account status...")
    status = await agent.hand.check_login_status()
    print(f"Status: {status}")
    
    # 3. Market Analysis (Scan, Scroll, Compare)
    print(f"Step 3: Analyzing results (Budget: {JarvisConfig.ORDER_BUDGET} INR)...")
    analysis = await agent.run_market_analysis("Biryani")
    
    print("\n--- JARVIS ANALYSIS REPORT ---")
    print(analysis)
    print("------------------------------\n")
    
    # 4. Approval Loop
    print("Step 4: Requesting your approval via WhatsApp...")
    approval_status = await agent.request_order_approval(analysis, "919154716156")
    print(f"Result: {approval_status}")
    
    # Final confirmation screenshot
    agent.hands.capture_screen("commerce_demo_final.png")
    print("Demo complete. JARVIS is standing by for your 'Yes' to proceed with the order.")

if __name__ == "__main__":
    asyncio.run(full_autonomous_demo())
