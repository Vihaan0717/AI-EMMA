"""
HuggingFace Inference Engine — Backup AI
Free serverless inference for Llama, Mistral, Gemma
"""

import asyncio
import logging
import os
from typing import Optional

import aiohttp

logger = logging.getLogger("HFEngine")


class HFEngine:
    """
    HuggingFace Inference API.
    Free tier — backup when Groq is unavailable.
    Models: meta-llama/Llama-3.2-3B-Instruct,
            google/gemma-2-2b-it,
            mistralai/Mistral-7B-Instruct-v0.3
    """

    MODELS = {
        "fast": "microsoft/DialoGPT-medium",
        "smart": "meta-llama/Llama-3.2-3B-Instruct",
        "backup": "google/gemma-2-2b-it"
    }

    BASE_URL = "https://api-inference.huggingface.co/models"

    def __init__(self):
        self.token = os.getenv("HF_TOKEN", "")
        self.is_ready = False
        self._session: Optional[aiohttp.ClientSession] = None
        self._current_model = self.MODELS["smart"]

    async def initialize(self):
        """Initialize HuggingFace connection"""
        if not self.token:
            logger.warning("No HF_TOKEN — HF engine disabled")
            return

        self._session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
        )

        # Test with a small request
        try:
            test = await self.generate(
                "Say: ready",
                max_tokens=10
            )
            if test:
                self.is_ready = True
                logger.info("✅ HuggingFace engine ready")
            else:
                logger.warning(
                    "HF test failed — will retry on demand"
                )
                # Still mark ready for retry
                self.is_ready = True
        except Exception as e:
            logger.warning(f"HF init: {e}")
            self.is_ready = bool(self.token)

    async def generate(
        self,
        prompt: str,
        system: str = None,
        max_tokens: int = 500,
        temperature: float = 0.7,
        model: str = None
    ) -> str:
        """Generate using HuggingFace Inference API"""
        if not self._session or not self.token:
            return ""

        chosen = model or self._current_model

        # Build prompt
        if system:
            full_prompt = (
                f"[INST] <<SYS>>\n{system}\n<</SYS>>\n\n"
                f"{prompt} [/INST]"
            )
        else:
            full_prompt = prompt

        payload = {
            "inputs": full_prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": temperature,
                "top_p": 0.9,
                "do_sample": True,
                "return_full_text": False
            },
            "options": {
                "wait_for_model": True,
                "use_cache": False
            }
        }

        try:
            async with self._session.post(
                f"{self.BASE_URL}/{chosen}",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if isinstance(data, list) and data:
                        return data[0].get(
                            "generated_text", ""
                        ).strip()
                    return ""
                elif resp.status == 503:
                    # Model loading — wait and retry
                    logger.info("HF model loading, waiting...")
                    await asyncio.sleep(20)
                    return await self.generate(
                        prompt, system, max_tokens,
                        temperature, model
                    )
                elif resp.status == 401:
                    logger.error("HF: Invalid token")
                    self.is_ready = False
                    return ""
                else:
                    logger.warning(
                        f"HF error {resp.status}"
                    )
                    return ""
        except asyncio.TimeoutError:
            logger.warning("HF request timed out")
            return ""
        except Exception as e:
            logger.error(f"HF generate error: {e}")
            return ""

    async def close(self):
        if self._session:
            await self._session.close()
