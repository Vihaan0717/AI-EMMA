import asyncio
import sys
import os

# Ensure the root project directory and the backend directory are in the Python path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root_dir)
sys.path.append(os.path.join(root_dir, 'backend'))

from backend.brain.agents.vision_hand_agent import VisionHandAgent
from backend.memory.vector_engine import VectorEngine

async def verify():
    print("1. Testing Vector Engine Initialization...")
    try:
        engine = VectorEngine()
        print("   [OK] ChromaDB client and Ollama embeddings configured.")
    except Exception as e:
        print(f"   [FAILED] Vector Engine failed: {e}")
        
    print("\n2. Testing VisionHandAgent Initialization...")
    try:
        agent = VisionHandAgent()
        print("   [OK] browser-use Agent initialized successfully.")
    except Exception as e:
        print(f"   [FAILED] VisionHandAgent failed: {e}")

if __name__ == "__main__":
    asyncio.run(verify())
