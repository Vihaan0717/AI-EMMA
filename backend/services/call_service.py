import os
import logging
try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    Client = None

from typing import Optional

logger = logging.getLogger("CallService")

class CallService:
    """
    Emergency Voice Call Service (via Twilio).
    Used when JARVIS needs to ring the boss's physical phone.
    """
    def __init__(self):
        self.sid = os.getenv("TWILIO_SID")
        self.token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = os.getenv("TWILIO_FROM_NUMBER")
        self.admin_number = os.getenv("ADMIN_NUMBER")
        
        self.client = None
        if not TWILIO_AVAILABLE:
            logger.warning("Twilio library not installed. Emergency calls disabled.")
        elif self.sid and self.token:
            try:
                self.client = Client(self.sid, self.token)
                logger.info("Call Service (Twilio) initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize Twilio: {e}")
        else:
            logger.warning("Twilio credentials missing. Emergency calls disabled.")

    async def make_emergency_call(self, message_telugu: str):
        """
        Makes a physical phone call and speaks the message in Telugu.
        """
        if not self.client or not self.admin_number:
            logger.error("Call Service not configured for Twilio.")
            return False

        try:
            # TwiML for Telugu speech
            twiml = f'''
            <Response>
                <Say language="te-IN" voice="Polly.Aditi">
                    Namaste Boss. Idi JARVIS. {message_telugu}
                </Say>
                <Pause length="1"/>
                <Say language="te-IN">Repeat chestunnanu.</Say>
                <Say language="te-IN">{message_telugu}</Say>
            </Response>
            '''
            
            call = self.client.calls.create(
                to=self.admin_number if "+" in self.admin_number else f"+{self.admin_number}",
                from_=self.from_number,
                twiml=twiml
            )
            
            logger.info(f"🚨 EMERGENCY CALL INITIATED: {call.sid}")
            return True
        except Exception as e:
            logger.error(f"Emergency call failed: {e}")
            return False
