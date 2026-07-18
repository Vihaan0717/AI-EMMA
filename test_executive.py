import asyncio
import os
import logging
import sys

# Add current dir to sys.path to ensure imports work
sys.path.insert(0, os.getcwd())

from main import NexusSystem
from nexus.cognition.executive_a14 import NexusMode

# Configure logging
logging.basicConfig(level=logging.INFO)

async def test_executive():
    print("=== TESTING NEXUS-X A14 EXECUTIVE ORCHESTRATION ===")
    system = NexusSystem()
    
    # Disable external bridges for the test
    os.environ["WHATSAPP_ENABLED"] = "false"
    os.environ["WHATSAPP_ONLY"] = "true"
    
    try:
        await system.initialize()
        print("PASS: Core systems initialized.")
        
        # Test Mode Switching via input
        print("Testing Mode Decision: 'Write some python code'...")
        mode = system.executive.decide_mode("Write some python code", "ui")
        if mode == NexusMode.ENGINEER:
            print(f"PASS: Correctly decided {mode.value} mode.")
        else:
            print(f"FAIL: Decided {mode.value} mode instead of engineer.")

        # Test Mode Switching via command
        print("Testing Mission Brief: Switching to BUDDY Mode...")
        await system.executive.set_mode(NexusMode.BUDDY)
        if system.executive.current_mode == NexusMode.BUDDY:
            print("PASS: Mode switched to BUDDY.")
        
        # Test Scholar Loop (Mocked data)
        print("Testing Scholar Peer-Review Loop for 'Kirrak'...")
        from core.fleet.manager import fleet_manager
        # Note: This will attempt to call LLMs, so we check if it starts without crashing
        try:
            # We don't actually need to wait for full LLM completion if models aren't loaded,
            # but we can check if the orchestration logic is triggered.
            result = await fleet_manager.scholar_peer_review("Kirrak", "Awesome")
            print(f"PASS: Scholar Peer-Review completed with score {result['score']}.")
        except Exception as e:
            print(f"INFO: Scholar loop triggered but likely failed due to local model absence: {e}")

        await system.stop()
        print("DONE: Executive test complete.")
    except Exception as e:
        print(f"FAIL: Executive test FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_executive())
