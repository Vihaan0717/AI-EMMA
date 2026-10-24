import os
import logging
import asyncio
try:
    from telegram import Bot
    from telegram.constants import ParseMode
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    Bot = None
    ParseMode = None

from typing import Optional
from config.system_config import JarvisConfig

logger = logging.getLogger("CallService")

class CallService:
    """
    Emergency Alert Service (via Telegram).
    Replaces Twilio. Used when JARVIS needs to send an urgent alert to the boss.
    """
    def __init__(self):
        self.token = JarvisConfig.TELEGRAM_TOKEN
        self.admin_chat_id = JarvisConfig.AUTHORIZED_CHAT_ID
        
        self.bot = None
        if not TELEGRAM_AVAILABLE:
            logger.warning("Telegram library not installed. Emergency alerts disabled.")
        elif self.token and self.admin_chat_id:
            try:
                self.bot = Bot(token=self.token)
                logger.info("Call Service (Telegram) initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize Telegram Bot: {e}")
        else:
            logger.warning("Telegram credentials missing. Emergency alerts disabled.")

    async def make_emergency_call(self, message_telugu: str):
        """
        Sends an urgent, high-priority alert to Telegram mimicking an emergency call.
        """
        if not self.bot or not self.admin_chat_id:
            logger.error("Call Service not configured for Telegram.")
            return False

        try:
            alert_text = f"🚨 *EMERGENCY ALERT* 🚨\n\nNamaste Boss. Idi JARVIS.\n\n{message_telugu}"
            
            await self.bot.send_message(
                chat_id=self.admin_chat_id,
                text=alert_text,
                parse_mode=ParseMode.MARKDOWN
            )
            
            logger.info("🚨 EMERGENCY TELEGRAM ALERT INITIATED")
            return True
        except Exception as e:
            logger.error(f"Emergency Telegram alert failed: {e}")
            return False
