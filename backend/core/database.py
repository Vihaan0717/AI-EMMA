from supabase import create_client, Client
from qdrant_client import QdrantClient
from config.system_config import JarvisConfig
from core.logger import get_logger

logger = get_logger("JarvisDatabase")

class JarvisDatabase:
    """Unified Cloud Database Manager for JARVIS-X."""
    
    def __init__(self):
        # 1. Supabase Initialization
        self.supabase: Client = None
        if JarvisConfig.SUPABASE_URL and JarvisConfig.SUPABASE_KEY:
            try:
                self.supabase = create_client(JarvisConfig.SUPABASE_URL, JarvisConfig.SUPABASE_KEY)
                logger.info("Supabase (PostgreSQL) connected successfully.")
            except Exception as e:
                logger.error(f"Supabase connection failed: {e}")
        
        # 2. Qdrant Cloud Initialization
        self.qdrant: QdrantClient = None
        if JarvisConfig.QDRANT_URL and JarvisConfig.QDRANT_API_KEY:
            try:
                self.qdrant = QdrantClient(url=JarvisConfig.QDRANT_URL, api_key=JarvisConfig.QDRANT_API_KEY)
                logger.info("Qdrant Cloud (Vector DB) connected successfully.")
                self._ensure_qdrant_collection()
            except Exception as e:
                logger.warning(f"Qdrant Cloud unavailable (Vector DB). Falling back to local memory.")

    def _ensure_qdrant_collection(self):
        """Ensures the knowledge collection exists in Qdrant."""
        if not self.qdrant: return
        collection_name = JarvisConfig.QDRANT_COLLECTION
        collections = self.qdrant.get_collections().collections
        exists = any(c.name == collection_name for c in collections)
        
        if not exists:
            logger.info(f"Creating Qdrant collection: {collection_name}")
            from qdrant_client.http.models import Distance, VectorParams
            self.qdrant.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE) # Gemini embedding size
            )

    # --- Structured Log Methods (Supabase) ---
    def log_interaction(self, data: dict):
        if self.supabase:
            return self.supabase.table("interaction_log").insert(data).execute()
        return None

    def upsert_setting(self, key: str, value: str, scope: str = "global"):
        if self.supabase:
            return self.supabase.table("settings").upsert({"key": key, "value": value, "scope": scope}).execute()
        return None

    # --- Semantic Memory Methods (Qdrant) ---
    def upsert_memory(self, vector: list, payload: dict, point_id: str = None):
        """Stores a text fragment with its embedding vector."""
        if not self.qdrant: return
        import uuid
        from qdrant_client.http.models import PointStruct
        
        point_id = point_id or str(uuid.uuid4())
        self.qdrant.upsert(
            collection_name=JarvisConfig.QDRANT_COLLECTION,
            points=[PointStruct(id=point_id, vector=vector, payload=payload)]
        )

    def search_knowledge(self, query_vector: list, limit: int = 5, score_threshold: float = 0.5, filter_payload: dict = None):
        """K-Find RAG Retrieval: Finds top-K similar memories above a relevance threshold."""
        if not self.qdrant: return []
        
        from qdrant_client.http.models import Filter, FieldCondition, MatchValue
        
        # Build optional metadata filter
        query_filter = None
        if filter_payload:
            conditions = [FieldCondition(key=k, match=MatchValue(value=v)) for k, v in filter_payload.items()]
            query_filter = Filter(must=conditions)
            
        results = self.qdrant.search(
            collection_name=JarvisConfig.QDRANT_COLLECTION,
            query_vector=query_vector,
            limit=limit,
            score_threshold=score_threshold,
            query_filter=query_filter
        )
        return results

# Global Instance
db_manager = JarvisDatabase()
