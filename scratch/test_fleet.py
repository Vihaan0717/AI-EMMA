import asyncio
import logging
from core.fleet.manager import fleet_manager
from core.fleet.local_db import fleet_db
from core.fleet.memory import fleet_memory

# Configure logging
logging.basicConfig(level=logging.INFO)

async def test_fleet():
    print("Starting Local Fleet Verification...")
    
    # 1. Test Task
    task = "Optimize this Java code: for(int i=0; i<list.size(); i++) { System.out.println(list.get(i)); }"
    print(f"\nTask: {task}")
    
    # Run Fleet Manager
    result = await fleet_manager.execute_task(task, doer_id="hank")
    
    print(f"\nAgent: {result['agent']}")
    print(f"Response: {result['response']}")
    print(f"Score: {result['score']}")
    print(f"Feedback: {result['feedback']}")
    print(f"Latency: {result['latency_ms']:.2f}ms")
    
    # 2. Verify DB Stats
    stats = fleet_db.get_agent_stats("hank")
    print(f"\nHank's New Stats: EP={stats[0]}, ENT={stats[1]}, Success Rate={stats[2]:.2f}%")
    
    # 3. Verify Journaling
    fleet_memory.write_journal_entry("hank", "Java Optimization", result['feedback'])
    print("\n📓 Journal updated.")
    
    # 4. Sleep Cycle
    await fleet_memory.sleep_cycle()
    print("\n💤 Sleep Cycle simulation complete.")

if __name__ == "__main__":
    asyncio.run(test_fleet())
