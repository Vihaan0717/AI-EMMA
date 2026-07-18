import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import asyncio
import json
import signal
from core.message_bus import Channel, MessageBus

async def main():
    print("\n" + "="*40, flush=True)
    print("      BOOTING ARION CORE", flush=True)
    print("="*40 + "\n", flush=True)

    # Deferred imports to prevent startup hang
    print("[Core] Importing subsystems...", flush=True)
    from agents.agent_monitor import AgentMonitor
    from agents.system_monitor import SystemMonitor
    from agents.resource_governor import ResourceGovernor
    from agents.language_engine import LanguageEngine
    from agents.intent_engine import IntentEngine
    from agents.emotion_engine import EmotionEngine
    from agents.persona_engine import PersonaEngine
    from agents.orchestrator import Orchestrator
    from agents.digital_twin import DigitalTwin
    from agents.comprehension_engine import ComprehensionEngine
    from agents.prediction_engine import PredictionEngine
    from agents.whatsapp_bridge import WhatsAppBridge
    from agents.telegram_center import TelegramCenter
    from agents.voice_engine import VoiceEngine
    from agents.coding_agent import CodingAgent
    from agents.knowledge_injector import KnowledgeInjector
    from agents.memory_manager import MemoryManager
    from agents.knowledge_ingestion_engine import KnowledgeIngestionEngine
    from agents.intake_watcher import IntakeWatcher
    from agents.learning_scheduler import LearningScheduler
    from agents.life_manager import LifeManager

    # ── ARION 3.0: Cognitive agents ───────────────────────────────────
    from agents.deep_language_engine import DeepLanguageEngine
    from agents.cognition_engine import CognitionEngine
    from agents.reflection_engine import ReflectionEngine
    from agents.goal_engine import GoalEngine
    
    config_paths = ["arion/config/system_config.json", "config/system_config.json"]
    config = None
    for cp in config_paths:
        if os.path.exists(cp):
            with open(cp, "r") as f:
                config = json.load(f)
            break
    
    if not config:
        print("[Core] FATAL: system_config.json not found.", flush=True)
        return

    bus = MessageBus()
    
    # Initialize agents - Now fast because heavy work moved to run_loops
    print("[Core] Initializing agents...", flush=True)
    agents = [
        AgentMonitor(config),
        SystemMonitor(),
        ResourceGovernor(),
        LanguageEngine(),
        IntentEngine(ollama_url=config["ollama_url"], model=config["model_name"]),
        EmotionEngine(),
        PersonaEngine("arion/config/persona_core.json", "arion/config/persona_adaptive.json"),
        Orchestrator(config),
        DigitalTwin(),
        ComprehensionEngine(ollama_url=config["ollama_url"], model=config["model_name"]),
        PredictionEngine(),
        WhatsAppBridge(config.get("bridge_queue", "arion/data/bridge_queue")),
        TelegramCenter(config),
        VoiceEngine(),
        CodingAgent(),
        KnowledgeInjector(),
        MemoryManager(config.get("db_paths", {})),
        KnowledgeIngestionEngine(config),
        IntakeWatcher(config),
        LearningScheduler(config),
        LifeManager(config),
        # ── ARION 3.0 ────────────────────────────────────────────────────
        DeepLanguageEngine(
            config_dir=config.get("config_dir", "arion/config"),
            db_path=config.get("db_paths", {}).get("pragmatics", "arion/data/pragmatics.db"),
        ),
        CognitionEngine(
            ollama_url=config.get("ollama_url", "http://localhost:11434"),
            model=config.get("fast_model", config.get("model_name", "gemma3:1b")),
        ),
        ReflectionEngine(config),
        GoalEngine(config),
    ]

    # Start all agents
    for agent in agents:
        print(f"[{agent.name}] Initializing...", flush=True)
        await agent.start()

    print("\n" + "="*40)
    print("      ARION IS ONLINE")
    print("="*40 + "\n")
    print("Persistent sentient mirror active. Press Ctrl+C to shutdown.\n", flush=True)
    
    try:
        # Keep the main process alive while agents are running
        while any(agent.running for agent in agents):
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        print("Shutdown signal received.")
    finally:
        for agent in agents:
            agent.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
