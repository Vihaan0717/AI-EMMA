import logging
import asyncio
import os
import sys
from datetime import datetime

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ai_engine import AIEngine
from core.telegram_service import TelegramService
from tools.google_workspace_tools import get_daily_schedule

logger = logging.getLogger("Protocols.MorningBriefing")

async def run_morning_briefing(telegram_service: TelegramService = None):
    logger.info("Executing Morning Briefing Protocol...")
    ai = AIEngine()
    await ai.initialize()
    
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Try fetching schedule
    schedule_data = await get_daily_schedule()
    
    prompt = f"It is {current_date}. Write a high-energy morning briefing. Include a motivational quote. Here is my schedule for today:\n{schedule_data}\n\nPlease summarize the schedule naturally in the briefing, and add a quick summary of what the system will monitor today."
    system_prompt = "You are JARVIS. You are proactively waking the user up with a morning briefing."
    
    logger.info("Generating briefing content...")
    briefing_text = await ai.generate(prompt, system=system_prompt, use_fast=True)
    
    if telegram_service:
        logger.info("Sending briefing via Telegram...")
        await telegram_service.send_alert(f"🌅 Morning Briefing:\n\n{briefing_text}")
    else:
        logger.warning(f"TelegramService not provided. Briefing: {briefing_text}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_morning_briefing())
