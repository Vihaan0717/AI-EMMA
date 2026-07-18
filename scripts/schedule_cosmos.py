"""
Initializes Cosmos's nightly autonomous learning goal.
"""
import sys
import os

# Add backend to path
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from core.fleet.goal_manager import goal_manager

def start_nightly_learning():
    goal_manager.add_goal(
        agent_id="cosmos",
        description="Every night: Run a deep learning cycle. 1) Read social_insights.json for trends. 2) Scrape Wikipedia/IMDB for movies or history. 3) Scrape Arxiv for scientific papers. 4) Read and analyze religious/philosophical texts like the Bhagavad Gita. 5) Save all insights into the Knowledge Graph."
    )
    print("Successfully assigned the continuous learning goal to Cosmos.")

if __name__ == "__main__":
    start_nightly_learning()
