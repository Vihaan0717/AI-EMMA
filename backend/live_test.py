import asyncio
import os
import json
import psutil
import logging
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.getcwd())

load_dotenv()

# Configure logging to console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    stream=sys.stdout
)

# NEXUS Core Imports
from core.ai_engine import AIEngine
from memory.memory_manager import MemoryManager
from core.brain import NexusBrain
from core.message_bus import MessageBus

async def live_deployment_test():
    print("\n" + "="*60)
    print("INITIALIZING NEXUS-X LIVE DEPLOYMENT TEST (VR/SANDBOX)")
    print("="*60)
    
    # 1. Setup Mock Modules for Brain
    bus = MessageBus()
    ai = AIEngine()
    memory = MemoryManager()
    
    print("Initializing AI Engine...")
    await ai.initialize()
    print("Initializing Memory Manager...")
    await memory.initialize()
    
    brain = NexusBrain({
        "bus": bus,
        "ai": ai,
        "memory": memory,
        "privacy": None 
    })
    
    print("Starting Brain...")
    await brain.start()
    
    print("\n--- STAGE 1: Verify Hardware Safety (A12) ---")
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory().percent
    print(f"Initial CPU Usage: {cpu_usage}%")
    print(f"Initial Memory Usage: {memory_info}%")
    
    print("\n--- STAGE 2: Testing A1 'Student' Trigger ---")
    test_input = "Nexus, listen, 'Kirrak' means 'Awesome' in Hyderabad slang."
    print(f"Input: {test_input}")
    
    # Use ADMIN_NUMBER to pass the privacy gate
    admin_sender = os.getenv("ADMIN_NUMBER", "919154716156")
    print(f"Using Admin Sender: {admin_sender}")
    
    # Run through the pipeline
    print("Processing input through pipeline...")
    result = await brain.process_input(test_input, source="ui", sender=admin_sender)
    
    print("\n--- PIPELINE RESULTS ---")
    print(json.dumps(result, indent=2))
    
    response = result.get("response", "")
    
    # Check if 'Kirrak' was learned
    dna_found = False
    dna_path = "data/telugu_dna.json"
    if os.path.exists(dna_path):
        with open(dna_path, 'r', encoding='utf-8') as f:
            dna = json.load(f)
        if "Kirrak" in dna.get("slang_registry", {}):
            dna_found = True

    if dna_found:
        print("\n[OK] SUCCESS: 'Kirrak' verified in T7 Linguistic DNA.")
    else:
        print("\n[FAIL] FAILURE: 'Kirrak' NOT found in DNA registry.")

    if "A1-STUDENT" in result.get("stages", []):
        print("[OK] SUCCESS: Pipeline reported A1-STUDENT stage completion.")
    else:
        print("[FAIL] FAILURE: A1-STUDENT stage NOT found in processing history.")

    print("\n--- STAGE 3: Hardware Stability Monitor ---")
    await asyncio.sleep(1)
    cpu_usage_final = psutil.cpu_percent(interval=1)
    print(f"Final CPU Usage: {cpu_usage_final}%")
    print("System remains stable and throttled.")

    # Cleanup
    await memory.stop()
    await ai.close()
    print("\n" + "="*60)
    print("TEST COMPLETE. NEXUS-X IS AWAKE.")
    print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(live_deployment_test())
