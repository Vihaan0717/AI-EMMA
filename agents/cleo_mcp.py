import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_base.agent_mcp_server import AgentMCPServer

cleo_server = AgentMCPServer("cleo", "Content Strategy & Social Media Agent")
mcp = cleo_server.mcp

if mcp:
    @mcp.tool()
    def cleo_draft_social_post(topic: str, platform: str) -> str:
        """
        Drafts a social media post tailored for the given platform.
        """
        return f"[Cleo] Drafted post for {platform} regarding {topic}:\n'Exciting news about {topic}! 🚀'"

    @mcp.tool()
    def cleo_analyze_trends() -> str:
        """
        Analyzes current social media trends.
        """
        return "[Cleo] Trending topics: AI, Automation, Productivity."

if __name__ == "__main__":
    cleo_server.run(transport="sse", port=8004)
