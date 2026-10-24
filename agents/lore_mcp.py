import os
import sys
import logging
import asyncio
from mcp_base.agent_mcp_server import AgentMCPServer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.agent_result import AgentResult
from memory.obsidian_vault import ObsidianVault

# Ensure backend is accessible for ReAct
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.append(root_dir)
backend_dir = os.path.join(root_dir, 'backend')
if backend_dir not in sys.path:
    sys.path.append(backend_dir)
    
from backend.brain.reasoning.react_graph import ReActGraph

lore_server = AgentMCPServer("lore_mcp", "Culture, Media, Mythology, and Lore Agent")
mcp = lore_server.mcp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def lore_deep_dive(topic: str) -> str:
    """
    Analyzes deep cultural, mythological, and media topics.
    Uses the autonomous ReAct engine to scrape the web for trends, reviews, and lore.
    Saves the findings to the Obsidian Vault under the 'Lore' agent.
    """
    logger.info(f"Lore is researching: {topic}")
    
    async def _run_react():
        try:
            # We use ReAct to do deep multi-step research
            graph = ReActGraph(model_name="llama3.1")
            
            # Format the query to ensure ReAct knows what Lore wants
            lore_query = (
                f"Perform a deep cultural and factual analysis on the following topic: '{topic}'. "
                f"Extract key themes, character arcs, mythological meanings, real-world impacts, "
                f"social media trends, or factual timelines. Synthesize this into a rich summary."
            )
            
            result = await graph.execute(lore_query)
            
            # Save to Obsidian Vault
            vault = ObsidianVault()
            vault.write_note(f"Lore on {topic[:30]}", result, "Lore")
            
            return AgentResult(
                status="success",
                confidence=0.9,
                sources=["ReAct Web Agents"],
                answer=result,
                needs_verification=False,
                errors=[]
            ).to_json()
            
        except Exception as e:
            return AgentResult(
                status="error",
                confidence=0.0,
                sources=[],
                answer="",
                needs_verification=True,
                errors=[f"Lore ReAct loop failed: {str(e)}"]
            ).to_json()
            
    return asyncio.run(_run_react())

if mcp:
    mcp.tool()(lore_deep_dive)

if __name__ == "__main__":
    logger.info("Starting Lore MCP Server...")
    try:
        lore_server.run()
    except Exception:
        pass
