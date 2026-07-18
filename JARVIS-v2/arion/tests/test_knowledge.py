import asyncio
import json
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(os.getcwd())

from agents.knowledge_ingestion_engine import KnowledgeIngestionEngine
from agents.knowledge_retrieval import KnowledgeRetrieval
import chromadb

async def test_knowledge_flow():
    print("=== ARION KNOWLEDGE SYSTEM TEST ===")
    
    config = {
        "db_paths": {
            "chroma": "arion/data_test/chromadb",
            "obsidian_vault": "arion/vault_test"
        },
        "ollama_url": "http://localhost:11434",
        "model_name": "llama3.1"
    }

    # 1. Initialize Engine
    engine = KnowledgeIngestionEngine(config)
    await engine._init_chroma()

    # 2. Ingest something
    test_content = "Stoicism is a school of Hellenistic philosophy founded by Zeno of Citium in Athens in the early 3rd century BC. It is a philosophy of personal virtue ethics informed by its system of logic and its views on the natural world, asserting that the practice of virtue is both necessary and sufficient to achieve eudaimonia (happiness, or flourishing)."
    
    print("\n--- Testing Ingestion ---")
    node = await engine.ingest(
        content=test_content,
        domain="philosophy",
        title="Stoicism",
        source_type="test"
    )
    
    print(f"Ingested Node ID: {node['id']}")
    print(f"ARION's Take: {node['arion_opinion']}")

    # 3. Test Retrieval
    print("\n--- Testing Retrieval ---")
    retrieval = KnowledgeRetrieval(engine.chroma_client, engine.knowledge_collection)
    
    # Simulate a user query about stress/life
    query = "I'm feeling very stressed about work and things I can't control."
    context = await retrieval.get_relevant_context(query)
    
    if context:
        print("Found relevant context:")
        print(context)
    else:
        print("No context found (Check ChromaDB distance/thresholds)")

    print("\n=== TEST COMPLETE ===")

if __name__ == "__main__":
    asyncio.run(test_knowledge_flow())
