import asyncio
import os
import sys
import logging

# Ensure imports work from backend dir
sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.path.join(os.getcwd(), "backend"))

from main import NexusSystem
from core.fleet.manager import fleet_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AgentsTalkVerifier")

async def test_agent_chats():
    print("=== INITIALIZING NEXUS SYSTEM FOR COLLABORATION TESTS ===")
    system = NexusSystem()
    
    # Disable external whatsapp/telegram integrations for testing
    os.environ["WHATSAPP_ENABLED"] = "false"
    os.environ["WHATSAPP_ONLY"] = "true"
    
    try:
        await system.initialize()
        # Wire memory manager to fleet manager
        fleet_manager.memory_manager = system.memory
        fleet_manager.ai_engine = system.ai
        
        print("\n=== 1. CHATTING WITH ARION (Tenglish & LTM Memory Recall) ===")
        # We will check if Arion uses Tenglish and pulls facts from memory.json
        arion_res = await system.brain.process_input("nuvvu ela unnav? my favorite food is what?", source="whatsapp")
        print(f"User: nuvvu ela unnav? my favorite food is what?")
        print(f"Arion: {arion_res.get('response')}")
        print(f"Dialect detected: {arion_res.get('dialect')}, Language: {arion_res.get('language')}")
        
        print("\n=== 2. RUNNING SENTINEL SECURITY AUDIT AND OBSIDIAN LOGGING ===")
        # Test routing and Sentinel execution on network sweep
        sentinel_res = await system.brain.process_input("Sentinel, run a check networks scan on 127.0.0.1", source="ui")
        print(f"User: Sentinel, run a check networks scan on 127.0.0.1")
        print(f"Sentinel (Vocal Response): {sentinel_res.get('response')}")
        print(f"Logs stored in: {sentinel_res.get('vault_path')}")
        
        # Verify file actually exists
        if sentinel_res.get('vault_path') and os.path.exists(sentinel_res.get('vault_path')):
            print("  PASS: Obsidian audit md file created and verified.")
        else:
            print("  FAIL: Obsidian audit md file not found.")

        print("\n=== 3. TESTING HANK (OS / Coding Tools & Critic Peer Review) ===")
        hank_res = await fleet_manager.execute_task("Write a quick code block in Python that prints out system time.", doer_id="hank")
        print(f"Hank Response:\n{hank_res.get('response')}")
        print(f"Critic Score: {hank_res.get('score')}/100")
        print(f"Critic Feedback: {hank_res.get('feedback')}")
        
        print("\n=== 4. TESTING CLEO (Creative Strategist) ===")
        cleo_res = await fleet_manager.execute_task("Write a 2-sentence creative story about a star going supernova.", doer_id="cleo")
        print(f"Cleo Response:\n{cleo_res.get('response')}")
        print(f"Critic Score: {cleo_res.get('score')}/100")
        
        print("\n=== 5. TESTING ATLAS (Research & Skills Scraper) ===")
        # We can pass query that triggers research / scraper integration
        atlas_res = await fleet_manager.execute_task("What is the latest system design best practice for fail-safe servers?", doer_id="atlas")
        print(f"Atlas Response:\n{atlas_res.get('response')}")
        print(f"Critic Score: {atlas_res.get('score')}/100")

        await system.stop()
        print("\n=== ALL SYSTEM INTERACTION TESTS COMPLETED ===")
    except Exception as e:
        print(f"System failed during chat testing: {e}")
        import traceback
        traceback.print_exc()
        try:
            await system.stop()
        except:
            pass

if __name__ == "__main__":
    asyncio.run(test_agent_chats())
