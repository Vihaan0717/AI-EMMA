AGENT_CAPABILITIES = {
    "atlas": {
        "capabilities": [
            {
                "name": "web_research",
                "description": "Research information from external sources",
                "tools": ["atlas_search_web"],
                "domains": ["research", "science", "fact_checking"]
            },
            {
                "name": "memory_recall",
                "description": "Recall memories from Obsidian vault",
                "tools": ["atlas_recall_memory"],
                "domains": ["memory", "history"]
            }
        ]
    },
    "hank": {
        "capabilities": [
            {
                "name": "security_scan",
                "description": "Scan security logs",
                "tools": ["scan_security_logs"],
                "domains": ["security", "system_logs"]
            },
            {
                "name": "intel_summary",
                "description": "Get Hank intel summary",
                "tools": ["get_hank_intel_summary"],
                "domains": ["security", "threat_intel"]
            }
        ]
    },
    "psyche": {
        "capabilities": [
            {
                "name": "emotion_analysis",
                "description": "Analyze emotion and behavior",
                "tools": ["psyche_analyze_emotion", "psyche_get_profile", "psyche_log_preference"],
                "domains": ["emotion", "preferences", "behavior"]
            }
        ]
    },
    "council": {
        "capabilities": [
            {
                "name": "debate",
                "description": "Hold reasoning debates",
                "tools": ["invoke_council"],
                "domains": ["reasoning", "debate", "decision_analysis"]
            }
        ]
    },
    "social": {
        "capabilities": [
            {
                "name": "social_manager",
                "description": "Manage social interactions",
                "tools": ["social_get_summary", "social_read_messages"],
                "domains": ["social_updates", "messages"]
            }
        ]
    }
}

def get_capable_agents(domain: str) -> list[str]:
    capable_agents = []
    for agent, info in AGENT_CAPABILITIES.items():
        for cap in info.get("capabilities", []):
            if domain in cap.get("domains", []):
                capable_agents.append(agent)
                break
    return capable_agents
