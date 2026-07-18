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

from backend.tools.google_workspace_tools import read_unread_emails, set_workspace_approval

# Helper to simulate an agent call stack
async def run_as_agent_loop(coro):
    # This function name contains "loop" to simulate background agent loops
    return await coro

async def main():
    print("--- Testing Agent Approval Gate in a general script ---")
    print("Executing as a background agent (should get blocked since this file name doesn't contain 'test_google'):")
    agent_res = await run_as_agent_loop(read_unread_emails())
    print("Agent Result:")
    print(agent_res)
    
    print("\n--- Testing Temporary Approval ---")
    print("Approving workspace access for 10 seconds...")
    set_res = set_workspace_approval(10)
    print("Approval Response:", set_res)
    
    print("\nExecuting as background agent after approval (should succeed):")
    approved_res = await run_as_agent_loop(read_unread_emails())
    print("Approved Agent Result:")
    print(approved_res)

if __name__ == "__main__":
    asyncio.run(main())
