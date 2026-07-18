import asyncio
import sys
import os
import time

# Configure stdout/stderr to use UTF-8
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Add root and backend to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend"))

from backend.tools.google_workspace_tools import get_daily_schedule, read_unread_emails, set_workspace_approval

# Helper to simulate an agent call stack
async def run_as_agent_loop(coro):
    # This function name contains "loop" to simulate background agent loops
    return await coro

async def main():
    print("--- 1. Testing Rate Limiting ---")
    print("Calling schedule first time:")
    res1 = await get_daily_schedule()
    print("Result 1:", res1)
    
    print("\nCalling schedule second time immediately:")
    res2 = await get_daily_schedule()
    print("Result 2:", res2)
    
    # Wait for rate limit cool down
    print("\nWaiting 10 seconds for rate limit cool down...")
    await asyncio.sleep(10)
    
    print("\n--- 2. Testing Agent Approval Gate ---")
    print("Executing as a background agent (simulated):")
    # This runs within a function containing "loop"
    agent_res = await run_as_agent_loop(read_unread_emails())
    print("Agent Result:")
    print(agent_res)
    
    print("\n--- 3. Testing Temporary Approval ---")
    print("Approving workspace access for 10 seconds...")
    set_res = set_workspace_approval(10)
    print("Approval Response:", set_res)
    
    print("\nExecuting as background agent after approval:")
    approved_res = await run_as_agent_loop(read_unread_emails())
    print("Approved Agent Result:")
    print(approved_res)

if __name__ == "__main__":
    asyncio.run(main())
