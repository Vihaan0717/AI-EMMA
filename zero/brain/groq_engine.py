"""
Groq Engine — Llama 3 for FREE
Fastest free LLM inference available
"""

import asyncio
import logging
import os
import time
from typing import Optional

import aiohttp

logger = logging.getLogger("GroqEngine")


class GroqEngine:
    """
    Groq API wrapper — completely free tier.
    Models: llama-3.1-8b-instant, llama-3.2-3b-preview,
            gemma2-9b-it, mixtral-8x7b-32768
    Rate limits: 30 req/min, 6000 tokens/min (free)
    """

    MODELS = {
        "fast": "llama-3.2-3b-preview",
        "smart": "llama-3.1-8b-instant",
        "powerful": "gemma2-9b-it",
        "reasoning": "mixtral-8x7b-32768"
    }

    BASE_URL = "https://api.groq.com/openai/v1"

    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.is_ready = False
        self._session: Optional[aiohttp.ClientSession] = None
        self._request_count = 0
        self._last_minute_reset = time.time()
        self._minute_requests = 0

    async def initialize(self):
        """Initialize and test connection"""
        if not self.api_key:
            logger.warning("No GROQ_API_KEY found")
            return

        self._session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )

        # Test connection
        try:
            test = await self.generate(
                "Reply with: OK",
                max_tokens=5,
                use_fast=True
            )
            if test:
                self.is_ready = True
                logger.info("✅ Groq AI connected")
        except Exception as e:
            logger.error(f"Groq test failed: {e}")

    async def generate(
        self,
        prompt: str,
        system: str = None,
        max_tokens: int = 500,
        temperature: float = 0.75,
        use_fast: bool = False,
        model: str = None
    ) -> str:
        """Generate response using Groq"""
        if not self._session:
            return ""

        # Rate limit check (30 req/min free tier)
        await self._rate_limit_check()

        # Choose model
        if model:
            chosen_model = model
        elif use_fast:
            chosen_model = self.MODELS["fast"]
        else:
            chosen_model = self.MODELS["smart"]

        messages = []
        if system:
            messages.append({
                "role": "system",
                "content": system
            })
        messages.append({
            "role": "user",
            "content": prompt
        })

        payload = {
            "model": chosen_model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": 0.9,
            "stream": False
        }

        try:
            async with self._session.post(
                f"{self.BASE_URL}/chat/completions",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self._request_count += 1
                    self._minute_requests += 1
                    return (
                        data["choices"][0]["message"]["content"]
                        .strip()
                    )
                elif resp.status == 429:
                    # Rate limited — wait and retry
                    logger.warning("Groq rate limited, waiting...")
                    await asyncio.sleep(60)
                    return await self.generate(
                        prompt, system, max_tokens,
                        temperature, use_fast, model
                    )
                else:
                    error = await resp.text()
                    logger.error(
                        f"Groq error {resp.status}: {error[:100]}"
                    )
                    return ""
        except asyncio.TimeoutError:
            logger.error("Groq request timed out")
            return ""
        except Exception as e:
            logger.error(f"Groq error: {e}")
            return ""

    async def generate_with_persona(
        self,
        message: str,
        persona: str,
        context: str = "",
        memories: str = "",
        language: str = "english",
        emotion: str = "neutral"
    ) -> str:
        """Generate with full persona context"""

        system = f"""{persona}

COMMUNICATION RULES:
- Respond naturally like a human, not a robot
- Language: {language}
- User's emotion: {emotion}
- Never say "As an AI"
- Be direct, warm, and genuinely helpful
- Match the user's energy level"""

        full_prompt = ""
        if memories:
            full_prompt += f"RELEVANT MEMORIES:\n{memories}\n\n"
        if context:
            full_prompt += f"CONVERSATION CONTEXT:\n{context}\n\n"
        full_prompt += f"USER: {message}\n\nRespond:"

        return await self.generate(
            prompt=full_prompt,
            system=system,
            max_tokens=600,
            temperature=0.8
        )

    async def _rate_limit_check(self):
        """Check and enforce rate limits"""
        now = time.time()
        if now - self._last_minute_reset >= 60:
            self._minute_requests = 0
            self._last_minute_reset = now

        if self._minute_requests >= 28:  # Keep 2 buffer
            wait = 60 - (now - self._last_minute_reset)
            if wait > 0:
                logger.info(
                    f"Rate limit: waiting {wait:.1f}s"
                )
                await asyncio.sleep(wait)
                self._minute_requests = 0
                self._last_minute_reset = time.time()

    async def close(self):
        if self._session:
            await self._session.close()
