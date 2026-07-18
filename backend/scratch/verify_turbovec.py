import asyncio
import numpy as np
import os
import sys

# Ensure imports work from backend dir
sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.path.join(os.getcwd(), "backend"))

from memory.memory_manager import MemoryManager, HAS_TURBOVEC

class MockEmbedder:
    async def embed(self, text: str):
        # nomic-embed-text embedding dimension is 768
        # Generate a deterministic vector based on characters to make test repeatable
        vec = np.zeros(768, dtype=np.float32)
        for i, char in enumerate(text[:768]):
            vec[i] = ord(char) / 255.0
        # Normalize vector to simulate cosine distance properly
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec /= norm
        return vec.tolist()

async def main():
    print("=== TURBOVEC INTEGRATION TEST ===")
    print(f"Is turbovec installed and available? {HAS_TURBOVEC}")
    if not HAS_TURBOVEC:
        print("FAIL: turbovec is not installed or import failed.")
        sys.exit(1)

    # Clean up any existing turbovec files from previous runs to ensure clean test
    tq_path = "backend/memory/semantic/turbovec.tq"
    tq_json_path = "backend/memory/semantic/turbovec_metadata.json"
    if os.path.exists(tq_path):
        os.remove(tq_path)
    if os.path.exists(tq_json_path):
        os.remove(tq_json_path)

    # Initialize MemoryManager
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    memory = MemoryManager()
    await memory.initialize()
    
    print(f"MemoryManager _tq_index: {memory._tq_index}")
    print(f"MemoryManager HAS_TURBOVEC: {HAS_TURBOVEC}")
    
    # Set mock embedder
    embedder = MockEmbedder()
    memory.set_embedder(embedder)

    # Define test memory documents
    memories_to_store = [
        "Quantum computing algorithms require error correction techniques.",
        "Deep learning model architectures are scaling rapidly using attention mechanisms.",
        "Local agentic architectures keep data secure and zero-latency.",
        "Hyderabad startups use specific Telugu-influenced tech slang.",
        "Proper server redundancy prevents database failovers and data loss."
    ]

    print("\n--- Persisting Memories to TurboQuant Index ---")
    for doc in memories_to_store:
        node_id = await memory.remember(content=doc, importance=0.8, metadata={"type": "test_doc"})
        print(f"Stored: '{doc}' -> Node ID: {node_id}")

    # Wait briefly for consolidation write queue to process items
    print("Waiting for write-behind queue to drain...")
    while not memory.write_queue.empty() or len(memory.dirty_set) > 0:
        await asyncio.sleep(0.1)
    await asyncio.sleep(0.5) # small extra buffer for file I/O sync

    print("\n--- Testing Vector Query Retrieval via TurboQuant Index ---")
    queries = [
        "failover server redundancy",
        "quantum error correction",
        "telugu tech slang in startups"
    ]

    for query in queries:
        print(f"\nQuery: '{query}'")
        recalled = await memory._recall_vector(query, limit=2)
        print(f"Results (limit 2):")
        for res in recalled:
            print(f"  - [{res.get('type')}] Similarity: {res.get('relevance'):.4f} | ID: {res.get('id')} | Content: {res.get('content')}")

    # Verify that the turbovec files were created on disk
    print("\n--- Verifying Index Storage ---")
    tq_file = os.path.abspath(memory.tq_path)
    tq_json_file = os.path.abspath(memory.tq_json_path)
    print(f"Checking absolute paths:\n - {tq_file}\n - {tq_json_file}")
    if os.path.exists(tq_file) and os.path.exists(tq_json_file):
        print(f"PASS: {tq_file} size: {os.path.getsize(tq_file)} bytes")
        print(f"PASS: {tq_json_file} size: {os.path.getsize(tq_json_file)} bytes")
    else:
        print("FAIL: TurboQuant files were not written to disk.")

    await memory.stop()
    print("\n=== TURBOVEC INTEGRATION TEST COMPLETED ===")

if __name__ == "__main__":
    asyncio.run(main())
