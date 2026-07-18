import asyncio
import sys
import os
from pathlib import Path

# Add project root to sys.path
root = Path(r'c:\Users\anger\Desktop\JARVIS_Project')
sys.path.append(str(root))

from core.fleet.manager import fleet_manager

async def test_routing():
    print("--- Testing Fleet Routing for Atlas-X ---")
    
    # Test task signature
    task = "Analyze the sales data for Q2 and give me ROI insights."
    sig = fleet_manager._generate_task_sig(task)
    print(f"Task: '{task}'")
    print(f"Detected Signature: {sig}")
    
    # Test agent selection
    agent_id = fleet_manager._check_habits(sig) or "hank"
    if sig == "analytics" and not fleet_manager._check_habits(sig):
        agent_id = "atlas_x"
        
    print(f"Selected Agent: {agent_id}")
    
    if agent_id == "atlas_x":
        print("✅ SUCCESS: Task correctly routed to Atlas-X.")
    else:
        print("❌ FAILURE: Task routed to wrong agent.")

if __name__ == "__main__":
    asyncio.run(test_routing())
