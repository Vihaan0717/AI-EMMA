import sqlite3
import os
import re
from datetime import datetime
from core.logger import get_logger
from agents.memory_agent import MemoryAgent

logger = get_logger("LearningAgent")

class LearningAgent:
    """
    JARVIS 2.0 Learning Engine.
    Tracks user interactions and infers patterns/relationships.
    """
    def __init__(self, db_path="memory/learning.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()
        self.memory = MemoryAgent()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS interactions
                     (id INTEGER PRIMARY KEY, contact TEXT, intent TEXT, 
                      user_response TEXT, response_time_ms INTEGER, timestamp DATETIME)''')
        c.execute('''CREATE TABLE IF NOT EXISTS learned_patterns
                     (id INTEGER PRIMARY KEY, pattern_type TEXT, key TEXT, value TEXT,
                      confidence REAL, timestamp DATETIME)''')
        c.execute('''CREATE TABLE IF NOT EXISTS multilingual_vocabulary
                     (id INTEGER PRIMARY KEY, language TEXT, word TEXT,
                      translation TEXT, confidence REAL, timestamp DATETIME)''')
        conn.commit()
        conn.close()

    def record_interaction(self, contact, intent, response, response_time_ms):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO interactions (contact, intent, user_response, response_time_ms, timestamp) VALUES (?, ?, ?, ?, ?)",
                  (contact, intent, response, response_time_ms, datetime.now()))
        conn.commit()
        conn.close()
        logger.info(f"LearningAgent: Recorded interaction for {contact}.")

        # Trigger autonomous analysis
        self.analyze_interaction(contact, response)

    def analyze_interaction(self, contact, user_input):
        """Analyze input for relationship clues and patterns."""
        user_input = user_input.lower()

        # 1. Relationship Inference
        relationships = {
            "brother": [r"\bmy brother\b", r"\bhe is my brother\b"],
            "friend": [r"\bmy friend\b", r"\bhe is a friend\b", r"\bshe is a friend\b"],
            "sister": [r"\bmy sister\b"],
            "mother": [r"\bmy mom\b", r"\bmy mother\b"],
            "father": [r"\bmy dad\b", r"\bmy father\b"]
        }

        for rel, patterns in relationships.items():
            for pattern in patterns:
                match = re.search(pattern, user_input)
                if match:
                    # In a real scenario, we'd need to extract the name.
                    # For now, let's look for a capitalized name near the pattern if possible,
                    # or just log the inference for the last mentioned person.
                    logger.info(f"LearningAgent: Inferred relationship '{rel}' from input: '{user_input}'")
                    # self.memory.store_identity(name, rel, 5) # Placeholder
                    break

    def get_common_patterns(self, contact):
        # Placeholder for pattern detection logic
        return []

    def learn_new_language_pattern(self, language, text, translation, confidence=1.0):
        """Stores a new learned word or phrase."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO multilingual_vocabulary (language, word, translation, confidence, timestamp) VALUES (?, ?, ?, ?, ?)",
                  (language, text, translation, confidence, datetime.now()))
        conn.commit()
        conn.close()
        logger.info(f"LearningAgent: Learned new {language} pattern: '{text}' -> '{translation}'")

    def get_learned_vocabulary(self, language=None):
        """Retrieves learned vocabulary, optionally filtered by language."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        if language:
            c.execute("SELECT language, word, translation FROM multilingual_vocabulary WHERE language = ?", (language,))
        else:
            c.execute("SELECT language, word, translation FROM multilingual_vocabulary")
        rows = c.fetchall()
        conn.close()
        return rows

    def perform_daily_analysis(self):
        """Analyzes all interactions from the last 24 hours to find new patterns."""
        logger.info("LearningAgent: Performing daily autonomous analysis...")
        # 1. Fetch last 24h interactions
        # 2. Extract topics
        # 3. Identify frequent apps/times
        # 4. Store in learned_patterns table
        pass
