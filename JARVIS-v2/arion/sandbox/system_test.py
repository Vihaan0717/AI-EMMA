import asyncio
import os
import json
import time
from pathlib import Path
from datetime import datetime

# Add arion to path
import sys
sys.path.append(os.getcwd())

from core.message_bus import Channel, Message, MessageBus
from agents.orchestrator import Orchestrator
from agents.memory_manager import MemoryManager

# --- MOCKS ---

async def mock_ollama_request(self, messages):
    """Mock LLM response logic."""
    last_msg = messages[-1]["content"] if messages else ""
    
    if "baigan" in last_msg.lower():
        return "Baigan! Kya bolre tum? Kiraak hai sab."
    if "feedback:" in last_msg.lower():
        return "✅ Noted. I'll adjust."
    if "how are you" in last_msg.lower():
        return "Bindaas mowa! Nuvvu ela unnavu?"
    
    return "👍"

# Monkeypatch Orchestrator
Orchestrator._ollama_request = mock_ollama_request

# Mock Intent Engine responses
async def mock_get_tiered_intent(self, text):
    if "life" in text.lower() or "deep" in text.lower():
        return {"tier": 5, "intent": "philosophical_query", "category": "Deep Talk"}
    if "baigan" in text.lower():
        return {"tier": 3, "intent": "slang_usage", "category": "Regional Slang"}
    return {"tier": 1, "intent": "casual_chat", "category": "Small Talk"}

Orchestrator._get_tiered_intent = mock_get_tiered_intent

# --- TEST RUNNER ---

async def test_system_flow():
    print("\n=== STARTING ARION SYSTEM TEST ===\n")
    
    # Load dummy config
    config = {
        "ollama_url": "http://localhost:11434",
        "model_name": "llama3",
        "db_paths": {
            "sqlite": "sandbox/test_memory.db",
            "chroma": "sandbox/test_chroma",
            "obsidian_vault": "vault"
        }
    }
    
    # Clean old test db if exists
    if os.path.exists("sandbox/test_memory.db"):
        os.remove("sandbox/test_memory.db")
    
    bus = MessageBus()
    
    # Start agents
    mem = MemoryManager(config["db_paths"])
    orch = Orchestrator(config)
    
    await mem.start()
    await orch.start()
    
    print("\n[Init] Waiting for agents to settle...")
    await asyncio.sleep(2) # Wait for init
    
    # --- SCENARIO 1: New Contact (Rohan) - Casual ---
    print("\n[Scenario 1] New Contact (Rohan): 'Hey how are you?'")
    await bus.publish(Message(
        from_agent="TestRunner", to_channel=Channel.ORCHESTRATOR, action="process_input",
        payload={"text": "Hey how are you mama?", "contact": "Rohan", "source": "whatsapp"}
    ))
    await asyncio.sleep(3)
    
    # --- SCENARIO 2: Deep Talk (Promotion Candidate) ---
    print("\n[Scenario 2] Rohan: 'What is the meaning of life?'")
    await bus.publish(Message(
        from_agent="TestRunner", to_channel=Channel.ORCHESTRATOR, action="process_input",
        payload={"text": "What is the meaning of life? Just curious.", "contact": "Rohan", "source": "whatsapp"}
    ))
    await asyncio.sleep(3)
    
    # --- SCENARIO 3: Dialect Detection ---
    print("\n[Scenario 3] Rohan: 'Sab baigan mein mila diye!'")
    await bus.publish(Message(
        from_agent="TestRunner", to_channel=Channel.ORCHESTRATOR, action="process_input",
        payload={"text": "Sab baigan mein mila diye!", "contact": "Rohan", "source": "whatsapp"}
    ))
    await asyncio.sleep(3)

    # --- SCENARIO 4: Owner Feedback ---
    print("\n[Scenario 4] Owner: 'feedback: you are being too polite'")
    await bus.publish(Message(
        from_agent="TestRunner", to_channel=Channel.ORCHESTRATOR, action="process_input",
        payload={"text": "feedback: you are being too polite", "contact": "Owner", "source": "whatsapp", "is_owner": True}
    ))
    await asyncio.sleep(3)
    
    # --- CONSOLIDATION ---
    print("\n[Consolidation] Triggering manual memory promotion...")
    await bus.publish(Message(
        from_agent="TestRunner", to_channel=Channel.MEMORY, action="consolidate_memory"
    ))
    await asyncio.sleep(5)
    
    # --- VERIFICATION ---
    print("\n=== VERIFICATION ===\n")
    
    vault = Path("vault")
    
    checks = {
        "People_Index": vault / "People" / "Index.md",
        "Rohan_Profile": vault / "People" / "Rohan" / "Profile.md",
        "Rohan_Conversation": vault / "Memories" / "Conversations" / "Rohan" / f"{datetime.now().strftime('%Y-%m-%d')}.md",
        "Feedback_Log": vault / "Agent_Self" / "Feedback_Log.md",
        "Emotion_Log": vault / "Memories" / "Emotions" / f"{datetime.now().strftime('%Y-%m-%d')}.md"
    }
    
    for name, path in checks.items():
        if path.exists():
            print(f"FOUND: {name} at {path}")
            # print(path.read_text()) # Uncomment to see contents
        else:
            print(f"MISSING: {name} at {path}")

    # Stop agents
    await mem.stop()
    await orch.stop()
    
    print("\n=== TEST COMPLETED ===\n")

if __name__ == "__main__":
    asyncio.run(test_system_flow())
