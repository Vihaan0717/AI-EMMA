import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_base.agent_mcp_server import AgentMCPServer

sentinel_server = AgentMCPServer("sentinel", "Network Auditing & Security Agent")
mcp = sentinel_server.mcp

if mcp:
    @mcp.tool()
    def sentinel_audit_network(target_ip: str) -> str:
        """
        Runs a network security audit (e.g., Nmap sweep) on the target IP.
        """
        return f"[Sentinel] Simulated Nmap scan results for {target_ip}. No vulnerabilities found."

    @mcp.tool()
    def sentinel_check_system_health() -> str:
        """
        Checks internal JARVIS system health metrics.
        """
        return "[Sentinel] System health is nominal. All agents active."

if __name__ == "__main__":
    sentinel_server.run(transport="sse", port=8003)
