import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "data" / "iq_core.db"
AGENT_CFG_DIR = BASE_DIR / "config" / "agents"
AGENT_STATE_DIR = BASE_DIR / "data" / "agents" / "state"
VAULT_PATH = Path(os.getenv("VAULT_PATH", "knowledge_vault"))

# Model settings
ROUTER_MODEL = "llama3.2:1b"
REASONING_MODEL = "llama3.2:3b"
REWARD_MODEL = "llama3.2:3b"
DISTILL_MODEL = "llama3.2:1b"
