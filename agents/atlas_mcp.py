import os
import sqlite3
import urllib.request
import urllib.parse
import json
import logging
import re
from datetime import datetime
from mcp_base.agent_mcp_server import AgentMCPServer

# Initialize MCP Server for Atlas
atlas_server = AgentMCPServer("atlas_mcp", "Research and Intelligence Gathering Agent")
mcp = atlas_server.mcp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from memory.obsidian_vault import ObsidianVault

def atlas_search_web(query: str) -> str:
    """
    Scrapes the internet for information on a specific topic.
    Saves the findings to Atlas's permanent memory database.
    """
    logger.info(f"Atlas is researching: {query}")
    
    try:
        # 1. Try Wikipedia API first for high-quality factual data
        wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(query)}"
        req = urllib.request.Request(wiki_url, headers={'User-Agent': 'Mozilla/5.0'})
        
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                extract = data.get("extract", "")
                
                if extract:
                    vault = ObsidianVault()
                    vault.write_note(query.lower(), f"Source: Wikipedia\n\n{extract}", "Atlas")
                    
                    return f"[ATLAS] Query processed. I researched '{query}' and acquired the following data: {extract[:500]}... [Data permanently committed to memory banks.]"
        except Exception:
            pass # Fallback to DuckDuckGo if Wiki fails or page doesn't exist
            
        # 2. Fallback: DuckDuckGo Lite Scraper
        ddg_url = "https://lite.duckduckgo.com/lite/"
        data = urllib.parse.urlencode({'q': query}).encode('utf-8')
        req = urllib.request.Request(ddg_url, data=data, headers={'User-Agent': 'Mozilla/5.0'})
        
        with urllib.request.urlopen(req, timeout=5) as response:
            html = response.read().decode('utf-8')
            
            # Simple regex to extract snippets from DDG Lite
            snippets = re.findall(r'<td class="result-snippet">(.*?)</td>', html, re.IGNORECASE | re.DOTALL)
            
            if snippets:
                # Clean HTML tags
                clean_text = re.sub(r'<[^>]+>', '', snippets[0]).strip()
                
                vault = ObsidianVault()
                vault.write_note(query.lower(), f"Source: DuckDuckGo\n\n{clean_text}", "Atlas")
                
                return f"[ATLAS] Query processed. I researched '{query}' and acquired the following data: {clean_text[:500]}... [Data permanently committed to memory banks.]"
            
        return f"[ATLAS] Negative result. I could not locate any verifiable data concerning '{query}'."

    except Exception as e:
        return f"[ATLAS] System error encountered during network traversal: {str(e)}"

def atlas_recall_memory(topic: str) -> str:
    """
    Searches Atlas's permanent database for previously learned knowledge.
    """
    try:
        vault = ObsidianVault()
        results = vault.search_notes(topic)
        
        if "No results found" in results:
            return f"[ATLAS] Memory deficit. I possess no stored records regarding '{topic}'. Requesting authorization to search external networks."
            
        memory_str = f"[ATLAS] Accessing Obsidian Vault memory banks for '{topic}':\n{results}\n"
        return memory_str
    except Exception as e:
        return f"[ATLAS] Obsidian Vault error: {str(e)}"

# Register Tools if MCP is loaded
if mcp:
    mcp.tool()(atlas_search_web)
    mcp.tool()(atlas_recall_memory)

if __name__ == "__main__":
    logger.info("Starting Atlas Research MCP Server...")
    try:
        atlas_server.run()
    except Exception:
        pass
