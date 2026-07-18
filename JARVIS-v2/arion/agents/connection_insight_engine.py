import time
import random

class ConnectionInsightEngine:
    """
    Suggests meaningful connections between memories and knowledge.
    Ensures ARION feels like a friend who notices patterns, not just a log.
    """
    
    INSIGHT_TEMPLATES = {
        "recurring_pattern": [
            "bro noticed something ra — every time you mention {topic_a}, you also bring up {topic_b} soon after 🤔",
            "scene enti ra — {topic_a} ki {topic_b} connect avutundi meeru eppudu matladina 😂",
            "funny thing ra, whenever you talk about {topic_a}, you always seem to feel {emotion} after"
        ],
        "knowledge_connection": [
            "that thing you said about {owner_topic} — reminds me of what {knowledge_source} said ra",
            "bro you literally lived what {book_or_movie} was talking about ra 😂",
            "adhi exactly {philosophy} lo cheppindi ra — {simple_quote}"
        ],
        "growth_observation": [
            "noticed you don't stress about {old_stressor} anymore ra — growth 📈",
            "bro you used to always say {old_pattern}, these days different ra",
        ]
    }
    
    def __init__(self):
        self.last_insight_time = 0

    async def get_insight_if_ready(
        self,
        semantic_english: str,
        owner_emotion: str,
        profile: dict,
        conversation_length: int
    ) -> str or None:
        
        # ── Gate checks ────────────────────────────────────────────────
        
        # Not in middle of heavy conversation
        if owner_emotion in ["sad", "frustrated", "angry"]:
            return None
        
        # Only in relaxed/happy conversations
        if owner_emotion not in ["neutral", "happy", "playful", ""]:
            return None
        
        # Conversation must be deep enough
        if conversation_length < 3:
            return None
        
        # Max once per Day (simulated for now)
        hours_since = (time.time() - self.last_insight_time) / 3600
        if hours_since < 24:
            return None
        
        # 20% Spontaneity Gate
        if random.random() > 0.20:
            return None
        
        # ── Find an insight ──────────────────────────────────────────────
        
        # 1. Simple topic-based pattern check
        topics = profile.get("topics_discussed", {})
        high_freq_topics = [t for t, c in topics.items() if c > 5]
        
        if len(high_freq_topics) >= 2:
            self.last_insight_time = time.time()
            template = random.choice(self.INSIGHT_TEMPLATES["recurring_pattern"])
            return template.format(
                topic_a=high_freq_topics[0],
                topic_b=high_freq_topics[1],
                emotion=owner_emotion or "passionate"
            )
        
        return None
