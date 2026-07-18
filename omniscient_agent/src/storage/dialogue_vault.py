import chromadb
import logging
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DialogueVault:
    """Stores and retrieves powerful dialogues using vector search."""

    def __init__(self, db_path: str = "./vault_db"):
        self.db_path = db_path
        logger.info(f"Initializing Dialogue Vault at {self.db_path}")
        self.client = chromadb.PersistentClient(path=self.db_path)
        
        # Create or get the collection for dialogues
        self.collection = self.client.get_or_create_collection(
            name="powerful_dialogues",
            metadata={"hnsw:space": "cosine"}
        )

    def save_dialogue(self, text: str, metadata: Dict[str, Any], dialogue_id: str):
        """
        Saves a dialogue into the vault.
        metadata can include: 'speaker', 'series_name', 'emotion', 'audio_path'
        """
        try:
            self.collection.add(
                documents=[text],
                metadatas=[metadata],
                ids=[dialogue_id]
            )
            logger.info(f"Saved dialogue {dialogue_id} to vault.")
        except Exception as e:
            logger.error(f"Failed to save dialogue: {e}")

    def search_similar_dialogues(self, query_text: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Searches for dialogues with similar philosophical or emotional meaning.
        """
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            
            # Format the output cleanly
            formatted_results = []
            if results and results.get('documents'):
                docs = results['documents'][0]
                metas = results['metadatas'][0]
                for doc, meta in zip(docs, metas):
                    formatted_results.append({
                        "text": doc,
                        "metadata": meta
                    })
            return formatted_results
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

if __name__ == "__main__":
    vault = DialogueVault()
    # Dummy test
    vault.save_dialogue("I am justice!", {"speaker": "Light Yagami", "series": "Death Note"}, "dn_001")
    res = vault.search_similar_dialogues("justice and morality", 1)
    print("Search results:", res)
