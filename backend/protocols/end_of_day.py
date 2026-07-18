import logging
import asyncio
import os
import sys
from datetime import datetime

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ai_engine import AIEngine
from core.telegram_service import TelegramService

logger = logging.getLogger("Protocols.EndOfDay")

async def run_end_of_day(telegram_service: TelegramService = None):
    logger.info("Executing End of Day Protocol...")
    ai = AIEngine()
    await ai.initialize()
    
    prompt = "Write a brief end-of-day summary. Congratulate the user on making it through the day, remind them to log off, and suggest taking some rest."
    system_prompt = "You are JARVIS. You are proactively checking in with the user at the end of the day."
    
    logger.info("Generating End of Day content...")
    briefing_text = await ai.generate(prompt, system=system_prompt, use_fast=True)
    
    if telegram_service:
        logger.info("Sending End of Day message via Telegram...")
        await telegram_service.send_alert(f"🌙 End of Day:\n\n{briefing_text}")
    else:
        logger.warning(f"TelegramService not provided. Output: {briefing_text}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_end_of_day())
