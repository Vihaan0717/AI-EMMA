"""
NEXUS-X OMEGA Free AI Engine
100% Local - No API Keys - Powered by Ollama
"""

import asyncio
import json
import logging
import aiohttp
import time
from typing import Optional, Dict, Any

logger = logging.getLogger('FreeAIEngine')


class FreeAIEngine:
    """
    Local AI engine using Ollama
    Zero cost, zero API keys, full power
    """

    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.primary_model = "llama3.1"
        self.fast_model = "gemma2:2b"
        self.timeout = 60
        self.session: Optional[aiohttp.ClientSession] = None
        self.is_ready = False
        self.request_count = 0
        self.total_tokens = 0

    async def initialize(self):
        """Initialize the AI engine"""
        self.session = aiohttp.ClientSession()
        await self._check_and_pull_models()
        self.is_ready = True
        logger.info(
            f"🤖 AI Engine ready: {self.primary_model}"
        )

    async def _check_and_pull_models(self):
        """Check if models exist, pull if not"""
        try:
            async with self.session.get(
                f"{self.base_url}/api/tags", timeout=5
            ) as resp:
                data = await resp.json()
                models = [
                    m['name'] for m in data.get('models', [])
                ]
                logger.info(f"📦 Available models: {models}")

                # Pull primary model if not available
                if not any(
                    self.primary_model in m for m in models
                ):
                    logger.info(
                        f"⬇️ Pulling {self.primary_model}..."
                    )
                    await self._pull_model(self.primary_model)
        except Exception as e:
            logger.warning(f"Could not check models: {e}")

    async def _pull_model(self, model_name: str):
        """Pull a model from Ollama"""
        try:
            async with self.session.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name},
                timeout=300
            ) as resp:
                async for line in resp.content:
                    data = json.loads(line.decode())
                    if "status" in data:
                        logger.info(f"Pull: {data['status']}")
        except Exception as e:
            logger.error(f"Model pull failed: {e}")

    async def generate(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
        use_fast: bool = False,
        system: str = None
    ) -> str:
        """Generate response from local LLM"""
        if not self.session:
            self.session = aiohttp.ClientSession()

        model = self.fast_model if use_fast else self.primary_model
        start = time.time()

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "num_ctx": 4096,
                "top_p": 0.9,
                "top_k": 40,
                "repeat_penalty": 1.1
            }
        }

        if system:
            payload["system"] = system

        try:
            async with self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    response = data.get("response", "").strip()
                    elapsed = time.time() - start
                    self.request_count += 1
                    
                    # Logic to handle token counting if available in data
                    tokens = data.get("eval_count", 0)
                    self.total_tokens += tokens
                    logger.debug(f"Generated {tokens} tokens in {elapsed:.2f}s")
                    
                    return response
                else:
                    error_text = await resp.text()
                    logger.error(f"Ollama error: {error_text}")
                    return f"I had trouble thinking. Error: {resp.status}"
        except Exception as e:
            logger.error(f"Generation error: {e}")
            return "I encountered an error while processing your request."

    async def health_check(self) -> bool:
        """Check AI health"""
        try:
            async with self.session.get(f"{self.base_url}/api/tags", timeout=3) as resp:
                return resp.status == 200
        except:
            return False

    async def reinitialize(self):
        """Reinitialize engine"""
        if self.session:
            await self.session.close()
        await self.initialize()
