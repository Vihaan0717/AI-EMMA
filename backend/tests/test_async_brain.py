import asyncio
import sys
import os

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.orchestrator import jarvis_mind

async def test_brain():
    print("--- Starting Async Brain Test ---")
    inputs = [
        "Hi Jarvis",
        "What is the time?",
        "Tell me a joke"
    ]
    
    for i in inputs:
        print(f"User: {i}")
        try:
            # We use ainvoke because the graph is now async
            state = await jarvis_mind.ainvoke({"messages": [i]})
            print(f"JARVIS: {state['final_response']}")
            print("-" * 20)
        except Exception as e:
            print(f"CRASH: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_brain())
