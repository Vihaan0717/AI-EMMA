import logging
from datetime import datetime, timezone
from typing import List
from core.memory_models import MemoryItem, MemoryStability, MemoryStatus

logger = logging.getLogger("jarvis.memory_decay")

class MemoryDecayEngine:
    def __init__(self, retriever):
        self.retriever = retriever

    def process_decay(self):
        """
        Sweeps the SemanticRetriever store and demotes TEMPORAL memories 
        to STALE after their temporal window expires, triggering re-validation.
        """
        store = self.retriever.memory_store
        now = datetime.now(timezone.utc)
        
        for mem in store:
            if mem.status not in [MemoryStatus.VERIFIED, MemoryStatus.ESTABLISHED]:
                continue
                
            last_ver_dt = datetime.fromisoformat(mem.last_verified)
            age_hours = (now - last_ver_dt).total_seconds() / 3600
            
            # Simulated time decay thresholds (in a real system, this would be days/weeks)
            if mem.stability == MemoryStability.TEMPORAL and age_hours > 24:
                mem.status = MemoryStatus.STALE
                self.retriever.add_memory(mem) # Save back to DB
                logger.info(f"Memory {mem.memory_id} (TEMPORAL) decayed to STALE.")
                
            elif mem.stability == MemoryStability.SEMI_STABLE and age_hours > 720: # 30 days
                mem.status = MemoryStatus.STALE
                self.retriever.add_memory(mem)
                logger.info(f"Memory {mem.memory_id} (SEMI_STABLE) decayed to STALE.")
                
            # STABLE memories do not decay purely on time.
