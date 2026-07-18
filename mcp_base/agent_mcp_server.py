import logging
from typing import Optional
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    logging.error("Failed to import FastMCP. Run: pip install mcp")
    FastMCP = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentMCPServer:
    """
    Base class for wrapping an agent into an MCP Server.
    Provides standard setup for the transport layer (SSE or stdio) 
    and handles naming isolation.
    """
    
    def __init__(self, agent_name: str, description: str):
        self.agent_name = agent_name
        self.description = description
        
        if FastMCP:
            self.mcp = FastMCP(
                name=f"{self.agent_name}_mcp",
                dependencies=["mcp"]
            )
            logger.info(f"Initialized MCP Server for agent: {self.agent_name}")
        else:
            self.mcp = None
            logger.warning("FastMCP not available. Server will not start.")

    def run(self, transport: str = "sse", host: str = "0.0.0.0", port: int = 8000):
        """
        Runs the MCP server.
        transport: 'sse' (Server-Sent Events over HTTP) or 'stdio'
        """
        if not self.mcp:
            raise RuntimeError("FastMCP is not initialized.")

        if transport.lower() == "sse":
            logger.info(f"Starting {self.agent_name} MCP server via SSE on {host}:{port}")
            # FastMCP's .run() handles transport wrapping. Note: SSE requires fastapi/uvicorn
            self.mcp.run(transport="sse", host=host, port=port)
        elif transport.lower() == "stdio":
            logger.info(f"Starting {self.agent_name} MCP server via stdio")
            self.mcp.run(transport="stdio")
        else:
            raise ValueError(f"Unknown transport: {transport}")

if __name__ == "__main__":
    # Test execution
    server = AgentMCPServer("test_agent", "A test agent MCP server")
    print("Base server ready to be extended by specific agents.")
