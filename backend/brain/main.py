"""
═══════════════════════════════════════════════════════════════
JARVIS BRAIN v2.0 - MAIN ENTRY POINT
═══════════════════════════════════════════════════════════════
"""

import logging
from brain.language import MultilingualBrain

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('JarvisBrain')

class JarvisBrain:
    def __init__(self, supabase_client=None):
        self.language_engine = MultilingualBrain(supabase_client)
        logger.info("Jarvis Brain v2.0 Initialized")

    async def handle_message(self, message: str, lang: str = "telugu"):
        """Process incoming message using the multilingual engine"""
        logger.info(f"Processing: {message}")
        analysis = self.language_engine.process_text(message, lang)
        return analysis

if __name__ == "__main__":
    brain = JarvisBrain()
    print(brain.language_engine.process_text("chestunnav"))
