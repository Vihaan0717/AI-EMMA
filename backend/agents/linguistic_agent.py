from core.logger import get_logger
from agents.learning_agent import LearningAgent

logger = get_logger("LinguisticAgent")

class LinguisticAgent:
    """
    JARVIS 2.0 Linguistic Education Agent.
    Teaches the user about Telugu, Tenglish, and Hindi letters/vowels.
    """
    def __init__(self):
        self.learning_agent = LearningAgent()
        # Sample Data - Expanding on the user's request
        self.telugu_vowels = {
            "అ": {"meaning": "a", "usage": "As in 'America'", "type": "vowel"},
            "ఆ": {"meaning": "aa", "usage": "As in 'Father'", "type": "vowel"},
            "ఇ": {"meaning": "i", "usage": "As in 'India'", "type": "vowel"},
            "ఈ": {"meaning": "ee", "usage": "As in 'Feet'", "type": "vowel"},
            "ఉ": {"meaning": "u", "usage": "As in 'Put'", "type": "vowel"},
            "ఊ": {"meaning": "oo", "usage": "As in 'School'", "type": "vowel"},
        }

        self.common_phrases = {
            "Namaskaram": "Hello / Greeting",
            "Ela unnavu?": "How are you? (Telugu)",
            "Kaiku?": "Why? (Hyderabadi Hindi/Slang)",
            "Baigan": "Eggplant (literally), used as 'Nonsense' in Hyderabadi slang"
        }

    def explain_letter(self, letter):
        """Returns the meaning and usage of a specific letter."""
        if letter in self.telugu_vowels:
            info = self.telugu_vowels[letter]
            return f"The letter '{letter}' means '{info['meaning']}'. Usage: {info['usage']}."
        return f"I am still learning about the letter '{letter}', Boss."

    def get_lesson(self, topic):
        """Generates a brief lesson on a linguistic topic."""
        if topic.lower() == "telugu vowels":
            lesson = "Here are some Telugu vowels (Achulu):\n"
            for k, v in self.telugu_vowels.items():
                lesson += f"- {k} ({v['meaning']}): {v['usage']}\n"
            return lesson
        elif topic.lower() == "slang":
            lesson = "Local Hyderabad slang includes:\n"
            for k, v in self.common_phrases.items():
                if "Hyderabadi" in v or "slang" in v:
                    lesson += f"- {k}: {v}\n"
            return lesson
        elif topic.lower() == "learned":
            vocab = self.learning_agent.get_learned_vocabulary()
            if not vocab:
                return "I haven't learned any new words yet, Boss."
            lesson = "Here are some words I've recently learned:\n"
            for lang, word, trans in vocab:
                lesson += f"- [{lang}] {word}: {trans}\n"
            return lesson

        return "Which topic would you like to learn about? I can teach Telugu Vowels, Local Slang, or show you what I've 'learned'."

    def analyze_tenglish(self, phrase):
        """Breaks down Tenglish (Telugu + English) phrases."""
        # Simple heuristic breakdown
        words = phrase.split()
        analysis = "Analysis of your Tenglish phrase:\n"
        for word in words:
            if word.lower() in ["ela", "unnavu", "namaskaram"]:
                analysis += f"- {word}: Telugu word\n"
            else:
                analysis += f"- {word}: English/Other word\n"
        return analysis
