import os
from typing import Dict, List, Any, Optional
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class MemoryAgent:
    """
    JARVIS 2.0 Memory Agent.
    Manages three layers of memory (Identity, Episodic, Semantic) 
    using Supabase for long-term storage.
    """
    def __init__(self, db_dir="memory"):
        self.db_dir = db_dir  # unused, kept for backward compatibility
        url: str = os.environ.get("SUPABASE_URL", "")
        key: str = os.environ.get("SUPABASE_KEY", "")
        if not url or not key or url == "your_supabase_url_here":
            print("Warning: valid SUPABASE_URL or SUPABASE_KEY not found in environment variables. Memory operations may fail.")
            self.supabase = None
        else:
            self.supabase: Client = create_client(url, key)

    def store_identity(self, name: str, relationship: str, trust_level: int, face_embedding: Optional[bytes] = None):
        if not self.supabase: return
        data = {
            "name": name,
            "relationship": relationship,
            "trust_level": trust_level,
            "face_embedding": face_embedding.hex() if face_embedding else None
        }
        
        response = self.supabase.table("identity").select("id").eq("name", name).execute()
        if response.data:
            self.supabase.table("identity").update(data).eq("name", name).execute()
        else:
            self.supabase.table("identity").insert(data).execute()

    def store_event(self, event: str, person: str = "Unknown"):
        if not self.supabase: return
        data = {
            "event": event,
            "associated_person": person
        }
        self.supabase.table("episodic").insert(data).execute()

    def store_knowledge(self, category: str, key: str, value: str):
        if not self.supabase: return
        data = {
            "category": category,
            "key": key,
            "value": value
        }
        self.supabase.table("semantic").insert(data).execute()

    def recall_identity(self, name: str) -> Dict[str, Any]:
        if not self.supabase: return {}
        response = self.supabase.table("identity").select("*").eq("name", name).execute()
        if response.data:
            row = response.data[0]
            return {"id": row.get("id"), "name": row.get("name"), "relationship": row.get("relationship"), "trust_level": row.get("trust_level")}
        return {}

    def get_recent_events(self, limit: int = 5) -> List[Dict[str, Any]]:
        if not self.supabase: return []
        response = self.supabase.table("episodic").select("event", "timestamp").order("timestamp", desc=True).limit(limit).execute()
        return [{"event": row.get("event"), "timestamp": row.get("timestamp")} for row in response.data] if response.data else []

    def remember_fact(self, fact: str):
        """Legacy helper to store a general fact."""
        self.store_event(fact, "Boss")
        self.store_knowledge("General", "fact", fact)

    def recall_facts(self) -> str:
        """Legacy helper to recall all facts as a string for LLM injection."""
        facts = []
        if not self.supabase: return "Memory offline."
        
        # Get Identity
        response = self.supabase.table("identity").select("name", "relationship").execute()
        if response.data:
            for row in response.data:
                facts.append(f"User is {row.get('name')} ({row.get('relationship')}).")
        
        # Get Recent Events
        events = self.get_recent_events(limit=10)
        for e in events:
            facts.append(f"Recent event: {e['event']} at {e['timestamp']}")
            
        return "\n".join(facts) if facts else "No specific memories found."
    
    # ═══════════════════════════════════════════════════════════════
    # NEW SENTIENCE & SOCIAL MODULES
    # ═══════════════════════════════════════════════════════════════

    def get_mood(self) -> Dict[str, float]:
        """Recalls the current persistent mood vector."""
        if not self.supabase: 
            return {"Happy": 0.5, "Ambitious": 0.8, "Lonely": 0.1, "Jealous": 0.0, "Fear": 0.0, "Pride": 0.5}
        
        response = self.supabase.table("mood_states").select("*").order("timestamp", desc=True).limit(1).execute()
        if response.data:
            return response.data[0].get("vector", {})
        return {"Happy": 0.5, "Ambitious": 0.8} # Default state

    def update_mood(self, mood_vector: Dict[str, float]):
        """Persists a new mood state."""
        if not self.supabase: return
        self.supabase.table("mood_states").insert({"vector": mood_vector}).execute()

    def store_social_connection(self, name: str, relationship: str, context: str):
        """Stores a new entry in the Social Graph."""
        if not self.supabase: return
        data = {
            "name": name,
            "relationship": relationship,
            "context": context,
            "trust_level": 50 # Default trust for registered guests
        }
        self.supabase.table("social_graph").insert(data).execute()

    def get_social_connection(self, name: str) -> Optional[Dict]:
        """Checks if a person is in the Social Graph."""
        if not self.supabase: return None
        response = self.supabase.table("social_graph").select("*").eq("name", name).execute()
        return response.data[0] if response.data else None

    def update_reinforcement(self, penalty_reward: float):
        """Updates the internal 'Self-Correction' weights based on Boss feedback."""
        if not self.supabase: return
        # Logic to increment/decrement weights based on praise/penalty
        current = self.supabase.table("logic_weights").select("weight").order("id", desc=True).limit(1).execute()
        new_weight = (current.data[0]["weight"] if current.data else 1.0) + penalty_reward
        self.supabase.table("logic_weights").insert({"weight": new_weight}).execute()

    def get_ethical_framework(self) -> str:
        """Recalls the Boss's preferred ethical framework (Default: Dharma)."""
        if not self.supabase: return "Dharma"
        response = self.supabase.table("settings").select("value").eq("key", "ethical_framework").execute()
        return response.data[0]["value"] if response.data else "Dharma"

# Backward compatibility alias
MemoryVault = MemoryAgent

if __name__ == "__main__":
    memory = MemoryAgent()
    memory.store_event("Started refactoring to JARVIS 2.0 to use Supabase", "Architect")
    print(memory.get_recent_events())

# Singleton instance for JARVIS-X Routing
memory_agent_instance = MemoryAgent()