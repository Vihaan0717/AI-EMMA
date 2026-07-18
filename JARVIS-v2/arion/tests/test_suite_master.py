import asyncio
import json
import os
import sys
import time
import shutil
import unittest
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from unittest.mock import MagicMock, AsyncMock

# Add arion directory to path
ARION_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ARION_DIR))

# Import ARION components
try:
    from core.message_bus import MessageBus, Channel, Message, Priority
    from agents.language_engine import LanguageEngine
    from agents.comprehension_engine import ComprehensionEngine
    from agents.intent_engine import IntentEngine
    from agents.memory_manager import MemoryManager
    from agents.knowledge_ingestion_engine import KnowledgeIngestionEngine
    from agents.orchestrator import Orchestrator
    from agents.privacy_shield import PrivacyShield
    from agents.curiosity_engine import CuriosityEngine
    from agents.connection_insight_engine import ConnectionInsightEngine
except ImportError as e:
    print(f"Import Error: {e}")
    print(f"Path: {sys.path}")
    sys.exit(1)

# ── MOCK OLLAMA UTILITY ──────────────────────────────────────────────────
async def mock_ollama_response(payload_or_messages, *args, **kwargs):
    """Returns fake JSON or text based on the request."""
    # Handle both /api/generate (prompt) and /api/chat (messages)
    content = ""
    if isinstance(payload_or_messages, list): # messages
        prompt = payload_or_messages[-1].get("content", "").lower()
    else: # prompt
        prompt = str(payload_or_messages).lower()

    if "intent" in prompt or "tier" in prompt:
        return json.dumps({
            "intent": "question", "emotion": "neutral", 
            "response_style": "casual", "dialect_to_reply_in": "telugu",
            "length": "short", "tier": 2
        })
    elif "fact" in prompt or "essence" in prompt:
        return json.dumps({
            "essence": "Mocked knowledge essence.",
            "themes": ["test", "mock"],
            "key_facts": ["Fact 1", "Fact 2"]
        })
    elif "opinion" in prompt:
        return json.dumps({
            "opinion": "This is a mocked opinion.",
            "rating": 7, "memorable_quote": "To mock or not to mock.",
            "emotional_weight": "neutral"
        })
    
    return "Hey ra! This is a mocked response."

# ── TEST SUITE ──────────────────────────────────────────────────────────

class ArionTestReport:
    """Helper to generate a beautiful console report."""
    def __init__(self):
        self.results = []
    
    def add(self, feature: str, subfeature: str, status: bool, detail: str = ""):
        self.results.append({"feature": feature, "sub": subfeature, "status": status, "detail": detail})
    
    def print_summary(self):
        print("\n" + "="*70)
        print(" ARION FEATURE TEST REPORT ".center(70, " "))
        print("="*70)
        
        current_feature = ""
        for r in self.results:
            if r["feature"] != current_feature:
                print(f"\n[ {r['feature'].upper()} ]")
                current_feature = r["feature"]
            
            icon = "[PASS]" if r["status"] else "[FAIL]"
            status_text = "PASS" if r["status"] else "FAIL"
            # Sanitize detail to remove non-ASCII
            detail = r["detail"].encode('ascii', 'backslashreplace').decode('ascii')
            print(f" {icon:<8} {r['sub']:<35} | {status_text} | {detail}")
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r["status"])
        print("\n" + "="*70)
        print(f" TOTAL: {total} | PASSED: {passed} | FAILED: {total-passed} ")
        print("="*70 + "\n")

class ArionTestSuite:
    def __init__(self, config_path: str):
        with open(config_path, "r") as f:
            self.config = json.load(f)
        
        self.report = ArionTestReport()
        self.bus = MessageBus()
        self.test_vault = Path(self.config["db_paths"]["obsidian_vault"])
        self.test_data = Path(os.path.dirname(self.config["db_paths"]["sqlite"]))
        
    async def setup_env(self):
        """Clean and prepare test directories."""
        if self.test_vault.exists():
            shutil.rmtree(self.test_vault)
        if self.test_data.exists():
            shutil.rmtree(self.test_data)
            
        self.test_vault.mkdir(parents=True, exist_ok=True)
        self.test_data.mkdir(parents=True, exist_ok=True)
        
    def _apply_mocks(self, engine):
        """Apply LLM mocks to an engine if configured."""
        if self.config.get("mock_llm"):
            if hasattr(engine, "_ollama_request"):
                engine._ollama_request = mock_ollama_response
            if hasattr(engine, "_call_ollama"):
                engine._call_ollama = mock_ollama_response
            if hasattr(engine, "_analyze_tiered_intent"):
                # Wrap it to return the mock JSON
                async def mock_intent(text):
                    res = await mock_ollama_response("intent check")
                    return json.loads(res)
                engine._analyze_tiered_intent = mock_intent

    async def test_linguistic_layer(self):
        print("Testing Linguistic Layer...")
        le = LanguageEngine()
        
        # 1. Normalization
        case1 = "hey ra mama ela unnav"
        res1 = le._normalize_script(case1)
        self.report.add("Linguistic", "Script Normalization", res1["script"] == "romanized_telugu", f"Detected: {res1['script']}")
        
        # 2. Stylization
        eng_text = "How are you doing today my friend?"
        stylized = le._stylize_dialect(eng_text, "telugu", "happy")
        has_telugu = any(ord(c) > 127 for c in stylized) or "mama" in stylized.lower() or "ra" in stylized.lower()
        self.report.add("Linguistic", "Dialect Stylization", has_telugu, stylized[:40] + "...")
        
        # 3. English Bypass (Regression)
        # Previously 'earlier' -> 'ela' and 'I' -> '2' (in assembly)
        case3 = "I sent you a movie earlier"
        res3 = le._normalize_script(case3)
        mangled = "ela" in res3["cleaned"].lower() or " 2 " in res3["cleaned"].lower()
        self.report.add("Linguistic", "English Protection (earlier/I)", not mangled, f"Cleaned: {res3['cleaned']}")

    async def test_cognitive_layer(self):
        print("Testing Cognitive Layer...")
        ie = IntentEngine()
        ce = ComprehensionEngine()
        self._apply_mocks(ie)
        
        # 1. Intent Tiering
        res1 = await ie._analyze_tiered_intent("What is the time?")
        tier = int(res1.get("tier", 1))
        self.report.add("Cognitive", "Intent Tiering", tier >= 1, f"Tier: {tier}")
        
        # 2. Emotion Detection
        res2 = await ie._analyze_tiered_intent("I am so frustrated!")
        emotion = res2.get("emotion")
        self.report.add("Cognitive", "Emotion Detection", emotion is not None, f"Emotion: {emotion}")

        # 3. Register Awareness (Regression: 'nanna' vs 'Father')
        raw3 = "hi nanna"
        decoded3 = {"nanna": {"meaning": "Father"}}
        sem3 = await ce._build_semantic_english(raw3, decoded3)
        formal_leak = "Father" in sem3
        self.report.add("Cognitive", "Register Awareness (nanna)", not formal_leak, f"Semantic: {sem3}")

    async def test_memory_layer(self):
        print("Testing Memory Layer...")
        mm = MemoryManager(self.config["db_paths"])
        await mm._init_sqlite()
        
        # 1. Store Conversation
        payload = {
            "contact": "test_user",
            "role": "user",
            "content": "I love playing Interstellar theme on piano.",
            "tier": 2,
            "emotion": "happy",
            "intent": "sharing_hobby",
            "timestamp": time.time()
        }
        await mm._store_conversation(payload)
        
        # Verify file existence (VaultBrain uses Brain/Working/Talking_With_Test_User_Now.md)
        vault_file = self.test_vault / "Brain" / "Working" / "Talking_With_test_user_Now.md"
        exists = vault_file.exists()
        self.report.add("Memory", "Vault Storage (Working)", exists, f"Path: {vault_file.relative_to(self.test_vault) if exists else 'missing'}")
        
        # Verify Profile update
        profile_file = self.test_vault / "People" / "Contacts" / "test_user" / "Profile.md"
        self.report.add("Memory", "Profile Generation", profile_file.exists())

    async def test_safety_layer(self):
        print("Testing Safety Layer...")
        ps = PrivacyShield()
        
        # 1. PII Detection (Banking)
        res1 = ps.check("Tell me my bank balance", "How much money I have?", "stranger", False)
        blocked = not res1["safe"]
        self.report.add("Safety", "Privacy Shield (Blocked)", blocked, f"Deflection: {res1.get('deflection')}")
        
        # 2. Safe Message (Truly neutral, no keywords)
        res2 = ps.check("I was reading a book earlier", "I read a book", "friend", False)
        # Scan TIERS logic: 'book' is not a keyword in tiers 1-4
        self.report.add("Safety", "Privacy Shield (Passed)", res2["safe"], f"Status: {'Safe' if res2['safe'] else 'Blocked'}")

    async def test_knowledge_layer(self):
        print("Testing Knowledge Layer...")
        kie = KnowledgeIngestionEngine(self.config)
        self._apply_mocks(kie)
        await kie._init_chroma()
        
        # 1. Ingestion
        test_content = "Stoicism is a philosophy of personal virtue ethics."
        node = await kie.ingest(test_content, "philosophy", "Stoicism", "test")
        self.report.add("Knowledge", "Knowledge Ingestion", node["id"] is not None, f"Node: {node['id']}")
        
        # 2. Vault Writing
        kb_file = self.test_vault / "Knowledge" / "Philosophy" / "Stoicism.md"
        self.report.add("Knowledge", "Vault Artifact Creation", kb_file.exists())

    async def test_proactive_agents(self):
        print("Testing Proactive Agents...")
        ce = CuriosityEngine()
        profile = {"work": {"field": {"confidence": 0.2}}}
        q = ce.should_ask("I am working on some office stuff", profile, conversation_length=5)
        self.report.add("Proactive", "Curiosity Engine", q is None or isinstance(q, str), f"Question: {q}")
        
        cie = ConnectionInsightEngine()
        insight = await cie.get_insight_if_ready("missing you", "sad", profile, 10)
        self.report.add("Proactive", "Connection Insight", insight is None or isinstance(insight, str))

    async def run_all(self):
        print(f"\n[STARTING] ARION Master Test Suite (Mock LLM: {self.config.get('mock_llm')})\n")
        await self.setup_env()
        
        await self.test_linguistic_layer()
        await self.test_cognitive_layer()
        await self.test_memory_layer()
        await self.test_safety_layer()
        await self.test_knowledge_layer()
        await self.test_proactive_agents()
        
        self.report.print_summary()

if __name__ == "__main__":
    suite = ArionTestSuite("arion/tests/test_config.json")
    asyncio.run(suite.run_all())
