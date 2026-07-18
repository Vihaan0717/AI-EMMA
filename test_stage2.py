import asyncio
import logging
import os
import sys
import time

# Ensure backend is in sys.path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))

from vision.screen_monitor import ScreenMonitor
from core.ai_engine import AIEngine
from tools.vision_tools import look_at_screen

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestStage2")

class MockSystem:
    def __init__(self):
        self.screen_monitor = ScreenMonitor(buffer_size=1, interval=2)
        self.ai = AIEngine()

async def main():
    logger.info("Initializing Test System...")
    sys_instance = MockSystem()
    
    # 1. Start AI Engine
    await sys_instance.ai.initialize()
    
    # 2. Start Screen Monitor
    sys_instance.screen_monitor.start()
    
    logger.info("Waiting 5 seconds for screen monitor to capture frames...")
    await asyncio.sleep(5)
    
    # 3. Test look_at_screen tool
    logger.info("Triggering look_at_screen tool...")
    
    query = "What text do you see on the screen?"
    result = await look_at_screen(query, system_instance=sys_instance)
    
    logger.info("=============================")
    logger.info(f"TEST RESULT:\n{result}")
    logger.info("=============================")
    
    # 4. Stop Screen Monitor
    sys_instance.screen_monitor.stop()

if __name__ == "__main__":
    asyncio.run(main())
