import asyncio
import os
import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from memory.memory_manager import MemoryManager

logging.basicConfig(level=logging.INFO)

async def test_memory_flow():
    print("--- Starting Hybrid Memory Test ---")
    memory = MemoryManager()
    await memory.initialize()

    # 1. Test Remember (Non-blocking)
    print("\n1. Testing 'remember' (async)...")
    node_id = await memory.remember("The secret code is 42", importance=0.9, metadata={"source": "test"})
    print(f"Memory stored instantly with ID: {node_id}")
    
    # Check if it's in T1 buffer
    found_in_t1 = any(node.id == node_id for node in memory.t1_buffer)
    print(f"Found in T1 buffer: {found_in_t1}")

    # 2. Test Recall (Read-through)
    print("\n2. Testing 'recall'...")
    results = await memory.recall("secret code")
    if results:
        print(f"Recalled: {results[0]['content']} (Type: {results[0].get('type')})")
    else:
        print("Recall failed!")

    # 3. Test Consolidation (Dreaming)
    print("\n3. Testing background consolidation...")
    print("Waiting 2 seconds for worker to process queue...")
    await asyncio.sleep(2)
    
    # Verify it's in SQLite
    results_sql = await memory.recall("secret code")
    if results_sql:
        print(f"Recalled after consolidation: {results_sql[0]['content']} (Type: {results_sql[0].get('type')})")

    # 4. Test Negative Memory (Red Nodes)
    print("\n4. Testing Negative Memory (Red Nodes)...")
    await memory.remember("This attempt failed miserably", importance=1.0, is_red=True)
    await asyncio.sleep(1) # wait for worker
    
    similarity = await memory.check_negative_constraints("The attempt failed")
    print(f"Negative constraint similarity: {similarity:.2f}")
    
    if similarity > 0.8:
        print("SUCCESS: Negative constraint correctly identified!")

    # 5. Test Activation Decay (Simulated)
    print("\n5. Testing Activation Decay...")
    # Manually trigger a sweep with a short decay time or just check the logic
    await memory._deep_consolidation_sweep()
    print("Sweep completed.")

    await memory.stop()
    print("\n--- Hybrid Memory Test Completed ---")

if __name__ == "__main__":
    asyncio.run(test_memory_flow())
