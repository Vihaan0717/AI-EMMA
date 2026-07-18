import json
import logging
from backend.memory.vector_engine import VectorEngine

logger = logging.getLogger(__name__)

class LibrarianAgent:
    """
    Takes analyzed insights and structures them into the persistent brain (Vector DB).
    """
    def __init__(self, vector_engine: VectorEngine = None):
        self.vector_engine = vector_engine or VectorEngine()

    def ingest(self, analysis_result: dict, source_url: str):
        """
        Converts the analysis result into text form and memorizes it.
        """
        try:
            insights = analysis_result.get("insights", [])
            domain = analysis_result.get("domain", "Unknown")
            credibility = analysis_result.get("credibility_score", 0)
            
            # Formulate the memory string
            memory_text = f"Source Domain: {domain}\nCredibility: {credibility}\nInsights:\n"
            for insight in insights:
                memory_text += f"- {insight}\n"
                
            metadata = {
                "source_url": source_url,
                "domain": domain,
                "type": "analyzed_article"
            }
            
            doc_id = self.vector_engine.memorize(memory_text, metadata=metadata)
            logger.info(f"Successfully ingested memory with doc_id: {doc_id}")
            return doc_id
        except Exception as e:
            logger.error(f"Failed to ingest analysis result: {e}")
            raise
