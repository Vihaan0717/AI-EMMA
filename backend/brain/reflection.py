import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict

logger = logging.getLogger("jarvis.brain.reflection")

class ReflectionEngine:
    """
    Background system that reviews memories to detect patterns and update heuristics.
    Implements 'growth' through self-review.
    """
    def __init__(self, memory_manager):
        self.memory = memory_manager
        self.is_running = False

    async def start_loop(self):
        self.is_running = True
        while self.is_running:
            # Run reflection every 4 hours in the background
            await asyncio.sleep(14400) 
            await self.reflect()

    async def reflect(self):
        """Review recent interactions and extract high-level patterns."""
        logger.info("[Reflection] Commencing self-review cycle...")
        
        # 1. Fetch recent episodic memories
        recent_episodes = await self.memory.get_recent_episodes(limit=50)
        
        # 2. Detect repetition or frustration patterns
        patterns = self._detect_patterns(recent_episodes)
        
        # 3. Compress redundant info
        for pattern in patterns:
            logger.info(f"[Reflection] Pattern Detected: {pattern['observation']}")
            # Update the 'compressed' memory layer
            await self.memory.store_pattern(pattern)
            
        logger.info(f"[Reflection] Cycle complete. {len(patterns)} insights gained.")

    def _detect_patterns(self, episodes: List[Dict]) -> List[Dict]:
        """Simple heuristic pattern detection."""
        insights = []
        
        # Example: Detect if user dislikes repetitive explanations
        negative_feedback = [e for e in episodes if e.get("sentiment") == "negative"]
        if len(negative_feedback) > 3:
            insights.append({
                "observation": "User shows frustration in recent long interactions",
                "confidence": 0.85,
                "action": "reduce_response_complexity"
            })
            
        # Example: Detect preferred language
        telugu_count = sum(1 for e in episodes if e.get("language") == "telugu")
        if telugu_count > len(episodes) * 0.7:
            insights.append({
                "observation": "User strongly prefers Telugu/Tenglish",
                "confidence": 0.95,
                "action": "prioritize_telugu_responses"
            })
            
        return insights

    def stop(self):
        self.is_running = False
