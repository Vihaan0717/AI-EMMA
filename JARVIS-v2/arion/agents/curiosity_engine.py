"""
Curiosity Engine — ARION's Natural Interest System.

Notices gaps in knowledge about the owner.
Suggests natural, conversational questions to fill those gaps.
Never interrogates. Never forms. Asks like a friend would.
"""

import random
import time
from typing import Optional


class CuriosityEngine:

    # ── Knowledge Gaps → Natural Questions ──────────────────────────────────
    # Each entry: (fact_path, trigger_keywords, natural_questions, cooldown_hours)

    CURIOSITY_MAP = [

        # Family
        ("family.mother",
         ["sick", "not well", "tired", "hospital", "doctor"],
         [
             "arey em ayyindhi ra? amma okay ga undha?",
             "okay na? amma tho cheppava?",
             "rest chestunavaa bro?"
         ], 24),

        ("family.father",
         ["nanna", "dad", "father", "home"],
         [
             "nanna okay ga unnara?",
             "family lo andharuu okay ga unnaraa?"
         ], 48),

        ("family.sister",
         ["akka", "sister", "chelli"],
         [
             "akka em chesthundhi ippudu? college a job a?",
             "akka okay ga undha?"
         ], 48),

        # Work
        ("work.field",
         ["office", "work", "project", "meeting", "client"],
         [
             "em work chesthunnav ikkade exactly?",
             "software a? em field lo unav ra?",
             "kotta project a? em cheyyali undi?"
         ], 72),

        ("work.stress_level",
         ["tired", "exhausted", "work", "deadline", "meeting"],
         [
             "bro work ento stress ga undi?",
             "office lo pressure undi? or manageable ga undha?",
         ], 24),

        # Health
        ("health.current",
         ["sick", "fever", "not well", "cold", "headache"],
         [
             "arey em ayyindhi ra? fever a?",
             "okay ga unnava bro? em problem?",
             "medicine teskunnavaa?"
         ], 12),

        ("health.sleep",
         ["tired", "no sleep", "exhausted", "couldn't sleep"],
         [
             "sleep ainadha properly? or again late night a?",
             "bro rest cheyyi ra, anni work cheyyadam kadu",
             "phone pettu paduko bro 😂"
         ], 24),

        # Location
        ("location.home_city",
         ["home", "going home", "back home", "hometown"],
         [
             "ekkad unav ippudu ra?",
             "ikkade unava still or moved a?",
         ], 168),  # 1 week cooldown

        # Mood
        ("mood.negative_triggers",
         ["sad", "bored", "bore", "down", "low", "not good"],
         [
             "em ayyindhi ra? cheppu",
             "okay na bro? scene emi jarigindhi?",
             "kaburlu cheppu, em problem?"
         ], 6),

        # Goals
        ("goals.active_aspirations",
         ["want to", "planning", "trying", "learning", "future"],
         [
             "scene emi? em plan chestunavaa seriously?",
             "arey ela undi preparation? progress ainadha?",
         ], 72),

        # Interests
        ("interests.music",
         ["music", "song", "playlist", "listening"],
         [
             "enti ra ippudu chustunav/vinstunav?",
             "bro em song ippudu unna playlist lo?",
         ], 48),

        ("interests.gaming_sports",
         ["game", "playing", "cricket", "match", "tournament"],
         [
             "enti ra playing? pubg a cricket a?",
             "bro winning a losing a? 😂",
         ], 48),

    ]

    def __init__(self):
        self._last_asked: dict = {}  # fact_path → timestamp

    def should_ask(
        self,
        semantic_english: str,
        profile: dict,
        conversation_length: int,
        current_emotion: str = "neutral"
    ) -> Optional[str]:
        """
        Returns a natural question string if ARION should ask something.
        Returns None if conditions not right.

        Rules:
        - Wait at least 3 messages into conversation
        - Don't ask when owner is clearly upset/stressed
        - Respect cooldown per fact
        - Only ask ONE thing per conversation turn
        - Probability check — don't ask every time (feels natural)
        """

        # Too early in conversation
        if conversation_length < 3:
            return None

        # Don't interrogate when they're emotional
        if current_emotion in ["frustrated", "sad", "angry"]:
            return None

        # Random gate — only ask 40% of qualifying turns
        # Makes it feel spontaneous, not scripted
        if random.random() > 0.40:
            return None

        sem = semantic_english.lower()

        for (fact_path, triggers, questions, cooldown_hours) in self.CURIOSITY_MAP:

            # Check if trigger is in current message
            if not any(t in sem for t in triggers):
                continue

            # Check if we already know this (high confidence)
            fact_conf = self._get_confidence(profile, fact_path)
            if fact_conf >= 0.75:
                continue  # Already know enough about this

            # Check cooldown
            last_asked = self._last_asked.get(fact_path, 0)
            hours_since = (time.time() - last_asked) / 3600
            if hours_since < cooldown_hours:
                continue

            # ✅ All checks passed — ask naturally
            question = random.choice(questions)
            self._last_asked[fact_path] = time.time()
            return question

        return None

    def _get_confidence(self, profile: dict, path: str) -> float:
        """Navigate dot-path and return confidence score."""
        keys = path.split(".")
        node = profile
        for key in keys:
            if not isinstance(node, dict):
                return 0.0
            node = node.get(key, {})
        if isinstance(node, dict):
            return node.get("confidence", 0.0)
        return 0.0
