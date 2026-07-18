import asyncio
import time
import sys
import os
import json

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.orchestrator import jarvis_mind
from agents.response_agent import mirror_engine
from services.data_layer import data_layer, InteractionRecord
from config.system_config import JarvisConfig

class JARVISHealthCheck:
    def __init__(self):
        self.results = {}
        self.latency_stats = []

    async def test_network_vitals(self):
        print("Checking Network Vitals...")
        # Check Ollama
        import requests
        try:
            res = requests.get(JarvisConfig.OLLAMA_BASE_URL, timeout=5)
            self.results["Ollama"] = "UP" if res.status_code == 200 else "DOWN"
        except: self.results["Ollama"] = "DOWN"

        # Check Supabase
        try:
            from agents.memory_agent import MemoryVault
            vault = MemoryVault()
            mood = vault.get_mood()
            self.results["Supabase"] = "UP" if mood else "DEGRADED"
        except Exception as e:
            self.results["Supabase"] = f"DOWN ({e})"

    async def test_mirror_pipeline(self):
        print("Benchmarking Sentient Mirror Pipeline...")
        start_time = time.time()
        test_input = "Hi Jarvis, I'm feeling a bit kiraak today. Namaste!"
        try:
            response = await mirror_engine.process(test_input)
            latency = time.time() - start_time
            self.latency_stats.append(latency)
            self.results["Mirror Pipeline"] = f"OK ({latency:.2f}s)"
            self.results["Mirror Soul Check"] = "SUCCESS" if any(w in response.lower() for w in ["namaste", "bos", "sir", "soul", "kiraak"]) else "FAIL (Personality missing)"
        except Exception as e:
            self.results["Mirror Pipeline"] = f"CRASHED ({e})"

    async def test_async_orchestrator(self):
        print("Testing Async Orchestrator Stress...")
        # Fire 3 requests in parallel (not sequential) to test real async capability
        tasks = [
            jarvis_mind.ainvoke({"messages": ["What is the time?"]}),
            jarvis_mind.ainvoke({"messages": ["Hey Jarvis"]}),
            jarvis_mind.ainvoke({"messages": ["Set a reminder for tea"]})
        ]
        start_time = time.time()
        try:
            states = await asyncio.gather(*tasks)
            latency = time.time() - start_time
            self.results["Async Parallelism"] = f"OK ({len(states)} parallel tasks in {latency:.2f}s)"
        except Exception as e:
            self.results["Async Parallelism"] = f"FAIL ({e})"

    async def test_memory_persistence(self):
        print("Testing Memory Persistence...")
        test_fact = f"Today's secret key is {int(time.time())}"
        try:
            from agents.memory_agent import MemoryVault
            vault = MemoryVault()
            vault.remember_fact(test_fact)
            # Sleep a moment for DB sync
            await asyncio.sleep(1)
            facts = vault.recall_facts()
            self.results["Memory Persistence"] = "OK" if test_fact in facts else "FAIL (Fact not found)"
        except Exception as e:
            self.results["Memory Persistence"] = f"FAIL ({e})"

    def print_report(self):
        print("\n" + "="*40)
        print("   JARVIS-X SYSTEM HEALTH REPORT")
        print("="*40)
        for feature, status in self.results.items():
            icon = "[OK]" if "OK" in status or status == "UP" or status == "SUCCESS" else "[!!]"
            print(f"{icon} {feature.ljust(20)}: {status}")
        print("="*40)
        if self.latency_stats:
            avg_lat = sum(self.latency_stats) / len(self.latency_stats)
            print(f"Average Persona Latency: {avg_lat:.2f}s")
        print("="*40 + "\n")

async def main():
    checker = JARVISHealthCheck()
    await checker.test_network_vitals()
    await checker.test_mirror_pipeline()
    await checker.test_async_orchestrator()
    await checker.test_memory_persistence()
    checker.print_report()

if __name__ == "__main__":
    asyncio.run(main())
