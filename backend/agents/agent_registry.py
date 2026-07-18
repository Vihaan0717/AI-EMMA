import yaml
from pathlib import Path
from agents.base_agent import BaseAgent
# Note: config.settings is not yet defined, but we can use the relative path or define it later.
# For now, I'll use the direct path to the agent config dir.
AGENT_CFG_DIR = Path("config/agents")

# Dynamically load agent IDs from YAML files
AGENT_IDS = [f.stem for f in AGENT_CFG_DIR.glob("*.yaml")]

_registry: dict[str, BaseAgent] = {}

def get_all_agents() -> list[BaseAgent]:
    global _registry
    if not _registry:
        for aid in AGENT_IDS:
            try:
                _registry[aid] = BaseAgent(aid)
            except FileNotFoundError as e:
                print(f"[WARN] Skipping agent: {e}")
            except Exception as e:
                print(f"[ERROR] Failed to load agent {aid}: {e}")
    return list(_registry.values())

def get_agent(agent_id: str) -> BaseAgent:
    if not _registry:
        get_all_agents()
    if agent_id not in _registry:
        raise ValueError(f"Agent {agent_id} not found in registry.")
    return _registry[agent_id]

def get_agents_by_skill(skill: str) -> list[BaseAgent]:
    """Return agents with expert or advanced level in a given skill."""
    result = []
    for agent in get_all_agents():
        level = agent.state.get("skills", {}).get(skill, "none")
        if level in ["expert", "advanced"]:
            result.append(agent)
    return result

def get_agents_by_trust(agent_id: str) -> list[BaseAgent]:
    """Return agents that the given agent trusts most."""
    agent = get_agent(agent_id)
    trust_ids = agent.cfg.get("trust_network", [])
    return [get_agent(tid) for tid in trust_ids if tid in AGENT_IDS] # Using AGENT_IDS to avoid recursion/init issues
