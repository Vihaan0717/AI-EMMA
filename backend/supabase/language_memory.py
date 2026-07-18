"""
═══════════════════════════════════════════════════════════════
SUPABASE LANGUAGE MEMORY SCHEMA & CLIENT
═══════════════════════════════════════════════════════════════
Manages persistent storage for:
  ✓ Vocabulary (word -> meaning)
  ✓ Grammatical patterns
  ✓ Slang & Regional variations
═══════════════════════════════════════════════════════════════
"""

class LanguageMemory:
    def __init__(self, client):
        self.client = client
        self.table_name = "language_memory"

    async def add_word(self, word: str, meaning: str, lang: str = "telugu", tags: list = None):
        """Add a new word to the LTM"""
        data = {
            "word": word,
            "meaning": meaning,
            "language": lang,
            "tags": tags or [],
            "verified": False
        }
        return self.client.table(self.table_name).insert(data).execute()

    async def find_meaning(self, word: str):
        """Retrieve meaning from LTM"""
        return self.client.table(self.table_name).select("*").eq("word", word).execute()
