import asyncio
import sys
import os

# Ensure backend is in the path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root_dir)
sys.path.append(os.path.join(root_dir, 'backend'))

from backend.brain.reasoning.react_graph import ReActGraph
from backend.brain.agents.proposal_agent import ProposalAgent

async def test_react_loop():
    print("\n--- TESTING REACT LOOP ---")
    graph = ReActGraph(model_name="llama3.1")
    query = "Find the latest news on AI and compare the top 3 articles."
    try:
        print(f"Query: {query}")
        result = await graph.execute(query)
        print(f"\nFinal Result:\n{result}")
    except Exception as e:
        print(f"ReAct Loop failed: {e}")

def test_proposal_agent():
    print("\n--- TESTING SAFE PROPOSAL PIPELINE ---")
    agent = ProposalAgent(model_name="llama3.1")
    feature_request = "Create a function that adds two numbers together"
    print(f"Request: {feature_request}")
    try:
        filename = agent.generate_proposal(feature_request)
        print(f"Proposal successfully generated at: {filename}")
        
        with open(filename, "r", encoding="utf-8") as f:
            print("\nPreview:")
            print(f.read())
            
    except Exception as e:
        print(f"Proposal Agent failed: {e}")

if __name__ == "__main__":
    test_proposal_agent()
    print("\n--- TESTING REACT LOOP ---")
    asyncio.run(test_react_loop())
