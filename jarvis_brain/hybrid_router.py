import os
import json
import logging
import requests
from typing import Dict, Any, Tuple
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class HybridRouter:
    """
    Acts as the main traffic controller for NEXUS-X.
    Intercepts prompts, applies token reduction, triages them, and routes them to 
    either Local Ollama (simple) or Cloud Groq (complex).
    """

    def __init__(self):
        # Local Models
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.local_fast_model = os.getenv("OLLAMA_FAST_MODEL", "phi4-mini")
        self.local_main_model = os.getenv("OLLAMA_MODEL", "llama3.1:latest")
        
        # Cloud Model
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        self.cloud_heavy_model = "llama-3.3-70b-versatile" # Massive 70B parameter model on Groq
        
    def _reduce_tokens(self, prompt: str) -> str:
        """
        Token reduction strategy to save context window and API limits.
        If a prompt is insanely long (e.g., massive copy-pasted logs), 
        we brutally summarize or truncate it unless explicitly asked to read all of it.
        """
        # A simple aggressive character limit for demonstration. 
        # In a full production system, this could use an SLM to extract only the core question.
        max_chars = 12000 # Roughly 3000 tokens
        if len(prompt) > max_chars:
            logger.warning(f"Prompt exceeds max length ({len(prompt)} chars). Truncating to save tokens.")
            # Keep the beginning (context) and the very end (the actual question)
            return prompt[:6000] + "\n\n...[CONTENT TRUNCATED FOR TOKEN REDUCTION]...\n\n" + prompt[-6000:]
        return prompt

    def _triage_prompt(self, prompt: str) -> str:
        """
        Uses the tiny, fast local model to classify the prompt.
        Heavily biased toward 'LOCAL' to save cloud resources.
        """
        triage_system_prompt = (
            "You are a triage routing engine. Analyze the user prompt. "
            "Reply with EXACTLY the word 'COMPLEX' if the prompt requires generating massive amounts of code, "
            "deep architectural design, or advanced mathematical reasoning. "
            "Reply with EXACTLY the word 'LOCAL' for all other tasks (chatting, summarization, basic coding, general knowledge). "
            "Bias strongly toward 'LOCAL'."
        )
        
        try:
            payload = {
                "model": self.local_fast_model,
                "prompt": f"System: {triage_system_prompt}\n\nUser Prompt: {prompt[:1000]}", # Only need the start to triage
                "stream": False
            }
            response = requests.post(f"{self.ollama_url}/api/generate", json=payload, timeout=30)
            response.raise_for_status()
            decision = response.json().get("response", "").strip().upper()
            
            if "COMPLEX" in decision:
                return "COMPLEX"
            return "LOCAL"
        except Exception as e:
            logger.error(f"Triage Engine failed: {e}. Defaulting to LOCAL path.")
            return "LOCAL"

    def _load_lessons_learned(self) -> str:
        import glob
        lessons_dir = "knowledge_vault/lessons_learned"
        lessons_text = ""
        if os.path.exists(lessons_dir):
            for file in glob.glob(os.path.join(lessons_dir, "*.md")):
                try:
                    with open(file, "r", encoding="utf-8") as f:
                        lessons_text += f.read() + "\n"
                except Exception:
                    pass
        return lessons_text

    def execute(self, raw_prompt: str) -> str:
        """
        The main entrypoint. Reduces tokens, triages, and executes.
        """
        logger.info("-" * 40)
        
        # Inject lessons learned
        lessons = self._load_lessons_learned()
        if lessons:
            logger.info("Injecting lessons learned from simulation loop.")
            raw_prompt = f"SYSTEM INSTRUCTION (Lessons Learned from Simulations):\n{lessons}\n\nUSER TASK:\n{raw_prompt}"

        logger.info("1. Applying Token Reduction...")
        prompt = self._reduce_tokens(raw_prompt)
        
        logger.info("2. Triaging Prompt via Fast Local Engine...")
        route = self._triage_prompt(prompt)
        
        if route == "COMPLEX" and self.groq_api_key:
            logger.info("3. Route Selected: CLOUD HANDOFF (Groq Llama-3 70B)")
            return self._execute_cloud(prompt)
        else:
            if route == "COMPLEX" and not self.groq_api_key:
                logger.warning("Complex task detected, but no GROQ_API_KEY found. Forcing Local fallback.")
            logger.info(f"3. Route Selected: LOCAL EXECUTION (Ollama {self.local_main_model})")
            return self._execute_local(prompt)

    def _execute_local(self, prompt: str) -> str:
        """Executes using local Ollama model."""
        try:
            payload = {
                "model": self.local_main_model,
                "prompt": prompt,
                "stream": False
            }
            response = requests.post(f"{self.ollama_url}/api/generate", json=payload)
            response.raise_for_status()
            return response.json().get("response", "")
        except Exception as e:
            return f"Local Execution Failed: {e}"

    def _execute_cloud(self, prompt: str) -> str:
        """Executes using Cloud Groq model."""
        try:
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.cloud_heavy_model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7
            }
            response = requests.post(self.groq_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Cloud Execution Failed: {e}"

if __name__ == "__main__":
    router = HybridRouter()
    
    print("\n--- TEST 1: Simple Chat ---")
    simple_prompt = "Hey JARVIS, how are you feeling today? Tell me a quick joke."
    res1 = router.execute(simple_prompt)
    print(f"Result:\n{res1.encode('cp1252', errors='replace').decode('cp1252')}\n")
    
    print("\n--- TEST 2: Complex Coding ---")
    complex_prompt = "Design a complete deep learning architecture using PyTorch for classifying satellite images. Provide the full model class, training loop, and evaluation metrics code. Explain the mathematical intuition behind the loss function used."
    res2 = router.execute(complex_prompt)
    print(f"Result:\n{res2.encode('cp1252', errors='replace').decode('cp1252')}\n")
