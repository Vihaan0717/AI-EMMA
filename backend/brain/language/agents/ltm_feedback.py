"""
═══════════════════════════════════════════════════════════════
LTM FEEDBACK AGENT
═══════════════════════════════════════════════════════════════
Ensures JARVIS grows smarter with every interaction.
Cycle:
  1. Learn: New word/pattern detected
  2. Verify: Ask user if derived meaning is correct
  3. Save: Commit to Supabase Long Term Memory (LTM)
═══════════════════════════════════════════════════════════════
"""

import logging

logger = logging.getLogger('LTMFeedback')

class LTMFeedbackAgent:
    def __init__(self, supabase_client=None):
        self.supabase = supabase_client
        self.pending_confirmations = {}

    async def handle_new_pattern(self, word: str, derived_meaning: str, user_id: str):
        """Triggered when a new word is encountered"""
        self.pending_confirmations[user_id] = {
            "word": word,
            "meaning": derived_meaning
        }
        return f"Boss, I noticed you used '{word}'. Does it mean '{derived_meaning}'? (Yes/No)"

    async def process_feedback(self, user_id: str, feedback: str):
        """Processes user's 'Yes/No' or correction"""
        if user_id not in self.pending_confirmations:
            return None
        
        data = self.pending_confirmations.pop(user_id)
        if "yes" in feedback.lower():
            await self._save_to_ltm(data["word"], data["meaning"])
            return "Got it! Added to my permanent memory."
        else:
            return "Oh, my bad. Could you tell me what it actually means?"

    async def _save_to_ltm(self, word: str, meaning: str):
        """Saves confirmed meaning to Supabase"""
        if self.supabase:
            try:
                await self.supabase.table('language_memory').insert({
                    "word": word,
                    "meaning": meaning,
                    "verified": True
                }).execute()
            except Exception as e:
                logger.error(f"LTM Save failed: {e}")
