import logging
import time
import asyncio
from brain.learning.learner import NexusLearner
from core.message_bus import MessageBus, Channel, Message

logger = logging.getLogger("PassiveAwareness")

class PassiveAwareness:
    """
    A13: Passive Awareness Layer.
    Monitors background noise/speech for unknown linguistic candidates.
    """
    def __init__(self, bus: MessageBus, scholar=None):
        self.bus = bus
        self.scholar = scholar
        self.learner = NexusLearner()
        self.running = False
        self.vocab_set = self._build_vocab_set()

    def _build_vocab_set(self):
        """Builds a flat set of all known words/phrases to check against."""
        dna = self.learner.dna
        known = set()
        for registry in dna.values():
            for phrase in registry.keys():
                known.add(phrase.lower())
        return known

    async def start(self):
        self.running = True
        # Subscribe to VOICE channel (where all speech is logged)
        self.bus.subscribe(Channel.VOICE.value, self._analyze_input)
        logger.info("[A13] Passive Awareness active. Monitoring for linguistic candidates...")

    async def stop(self):
        self.running = False

    async def _analyze_input(self, msg: Message):
        """Analyze background speech for unknown words."""
        # Handle both string and dict data formats
        text = ""
        if isinstance(msg.data, str):
            text = msg.data.lower()
        elif isinstance(msg.data, dict):
            text = msg.data.get("text", "").lower()
            metadata = msg.data.get("metadata", {})
            
        if not text: return

        # Extract metadata
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
        location = metadata.get("location", "Unknown")
        tone = metadata.get("tone", "Neutral")

        # Simple candidate detection: 
        # Split by words and check against known vocabulary
        words = text.split()
        for word in words:
            # Strip punctuation
            clean_word = "".join(e for e in word if e.isalnum())
            if len(clean_word) > 3 and clean_word not in self.vocab_set:
                # Potential candidate detected!
                await self._log_candidate(clean_word, timestamp, location, tone)

    async def _log_candidate(self, word, timestamp, location, tone):
        """Adds a word to the DNA as a low-confidence candidate with context."""
        logger.info(f"[A13] Candidate Detected: {word} | Context: {location}, {tone} at {timestamp}")
        
        # 1. Register basic candidate
        self.learner.learn(word, "pending_verification", context=f"passive_at_{location}", dialect="Unknown")
        
        # 2. Trigger deep research via Scholar Agent
        if self.scholar:
            asyncio.create_task(self.scholar.classify_term(word, f"Passive detection at {location} with tone {tone}"))

        # Update local set
        self.vocab_set.add(word)

if __name__ == "__main__":
    # Test stub
    logging.basicConfig(level=logging.INFO)
    bus = MessageBus()
    pa = PassiveAwareness(bus)
    asyncio.run(pa.start())
