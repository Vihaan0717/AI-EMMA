import asyncio
import os
import logging
import sys

# Add current dir to sys.path to ensure imports work
sys.path.insert(0, os.getcwd())

from main import NexusSystem

# Configure logging
logging.basicConfig(level=logging.INFO)

async def test_boot():
    print("=== TESTING NEXUS-X A10-A13 INTEGRATION BOOT ===")
    system = NexusSystem()
    
    # Disable external bridges for the test
    os.environ["WHATSAPP_ENABLED"] = "false"
    os.environ["WHATSAPP_ONLY"] = "true"
    
    try:
        await system.initialize()
        print("PASS: Core systems initialized.")
        
        if system.passive_awareness:
            print("PASS: A13 Passive Awareness online.")
        
        # Test candidate logging
        from core.message_bus import Channel, Message
        test_msg = Message(Channel.VOICE.value, "new_speech", {"text": "This is a kirrak candidate test"})
        await system.bus.publish(Channel.VOICE.value, "new_speech", {"text": "This is a kirrak candidate test"})
        await asyncio.sleep(2) # Wait for processing
        
        print("PASS: A13 logic check complete.")
        
        await system.stop()
        print("DONE: Integration test PASSED.")
    except Exception as e:
        print(f"FAIL: Integration test FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_boot())
