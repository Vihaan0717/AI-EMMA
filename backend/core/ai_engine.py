"""
AI Engine - Bulletproof Ollama wrapper
Never hangs, never crashes, always has a fallback
"""

import os
import asyncio
import json
import logging
import time
from typing import Optional, AsyncGenerator

import aiohttp

from core.circuit_breaker import get_breaker
from core.rate_limiter import get_limiter

logger = logging.getLogger("AIEngine")


class AIEngine:
    """
    Bulletproof wrapper around Ollama.
    Circuit breaker + rate limiter + retry + fallback.
    """

    FALLBACK = "I'm thinking... please give me a moment."

    def __init__(self):
        self.base_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.primary = os.getenv("OLLAMA_MODEL", "llama3.1")
        self.fast = os.getenv("OLLAMA_FAST_MODEL", "llama3.1:latest")
        self.indic_model = os.getenv("OLLAMA_INDIC_MODEL", "mashriram/sarvam-m")
        self.indic_fast = os.getenv("OLLAMA_INDIC_FAST_MODEL", "mashriram/sarvam-1")
        self.embed_model = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
        self.vision_model = os.getenv("OLLAMA_VISION_MODEL", "moondream")
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self._session: Optional[aiohttp.ClientSession] = None
        self._ready = False
        self._cache = {}  # Semantic cache layer
        self._cb_primary = get_breaker(
            "ollama_primary",
            fail_threshold=5,
            recovery_timeout=30.0,
            timeout_per_call=180.0
        )
        self._cb_fast = get_breaker(
            "ollama_fast",
            fail_threshold=3,
            recovery_timeout=20.0,
            timeout_per_call=90.0
        )
        self._rl = get_limiter("ollama")
        
        # --- HEAVY TASK THROTTLING (2-MINUTE COOLDOWN) ---
        self._heavy_lock = asyncio.Lock()
        self._last_heavy_time = 0.0

    async def initialize(self):
        """Initialize and verify Ollama connection"""
        self._session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=120)
        )

        # Verify connection
        for attempt in range(3):
            try:
                async with self._session.get(
                    f"{self.base_url}/api/tags",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        models = [
                            m['name']
                            for m in data.get('models', [])
                        ]
                        logger.info(
                            f"[AI] Ollama connected. "
                            f"Models: {len(models)}"
                        )
                        self._ready = True
                        return
            except Exception as e:
                logger.warning(
                    f"Ollama connect attempt {attempt+1}: {e}"
                )
                await asyncio.sleep(2 ** attempt)

        logger.error("❌ Ollama not reachable - running in fallback mode")

    async def generate(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.75,
        use_fast: bool = False,
        system: str = None,
        keep_alive: str = "30s",
        is_heavy: bool = False
    ) -> str:
        """
        Generate response.
        Hybrid Intelligent Router: High-speed Cloud (Gemini) primary with Local (Ollama) fallback.
        """
        
        # --- ENFORCE 2-MINUTE COOLDOWN FOR HEAVY TASKS ---
        if is_heavy:
            async with self._heavy_lock:
                current_time = time.time()
                time_since_last = current_time - self._last_heavy_time
                if time_since_last < 120.0:
                    wait_time = 120.0 - time_since_last
                    logger.warning(f"[AI] Heavy task throttling active. Waiting {wait_time:.1f}s...")
                    await asyncio.sleep(wait_time)
                self._last_heavy_time = time.time()
                
        # Quick Semantic Cache check
        cache_key = f"{system or ''}:{prompt}"
        if cache_key in self._cache:
            logger.info(f"[AI Cache] Hit for query: {prompt[:40]}...")
            return self._cache[cache_key]

        from config.system_config import JarvisConfig
        
        # --- HYBRID CLOUD ROUTING (PRODUCTION LEVEL SPEED) ---
        if JarvisConfig.USE_CLOUD_PRIMARY and self.gemini_key:
            logger.debug("[AI] Routing query to high-speed cloud primary (Gemini)...")
            cloud_res = await self._call_gemini(prompt, system)
            if cloud_res:
                self._cache[cache_key] = cloud_res
                return cloud_res
            logger.warning("[AI] Cloud primary failed. Falling back to local Ollama...")

        if not self._ready:
            # Fallback directly to Gemini if Ollama is not ready but cloud primary was disabled
            if self.gemini_key:
                cloud_res = await self._call_gemini(prompt, system)
                if cloud_res:
                    self._cache[cache_key] = cloud_res
                    return cloud_res
            return self.FALLBACK

        # Rate limit
        allowed = await self._rl.wait(timeout=10.0)
        if not allowed:
            return self.FALLBACK

        # Choose model and breaker
        model = self.fast if use_fast else self.primary
        
        # ── LOCAL TELUGU ADAPTER ──────────────────────────────────
        if system and "telugu" in system.lower():
            model = self.indic_fast if use_fast else self.indic_model
            # Warm, conversational persona instead of "dictionary" mode
            system = "You are ARION, a warm and culturally fluent Telugu assistant. Speak naturally in Telugu script. Never use Hindi. Do not give dictionary definitions; just talk."

        cb = self._cb_fast if use_fast else self._cb_primary

        # Execute through circuit breaker
        result = await cb.call(
            self._call_ollama,
            prompt=prompt,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            keep_alive=keep_alive,
            fallback=None
        )

        if result:
            if result != self.FALLBACK:
                self._cache[cache_key] = result
            return result
            
        # ── FALLBACK TO GEMINI (in case cloud primary was off but local failed) ──
        if self.gemini_key:
            logger.warning("[AI] Local Ollama failed. Attempting Gemini fallback...")
            gemini_res = await self._call_gemini(prompt, system)
            if gemini_res:
                self._cache[cache_key] = gemini_res
                return gemini_res

        return self.FALLBACK

    async def _call_gemini(self, prompt: str, system: str = None) -> Optional[str]:
        """Direct Gemini API fallback call"""
        try:
            model_name = "gemini-2.5-flash-lite"
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.gemini_key}"
            
            full_prompt = f"{system}\n\n{prompt}" if system else prompt
            
            payload = {
                "contents": [{"parts": [{"text": full_prompt}]}]
            }
            
            async with self._session.post(url, json=payload, timeout=15) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data['candidates'][0]['content']['parts'][0]['text'].strip()
                else:
                    logger.error(f"[AI] Gemini Error ({resp.status}): {await resp.text()}")
                    return None
        except Exception as e:
            logger.error(f"[AI] Gemini connection failed: {e}")
            return None

    async def _call_ollama(
        self,
        prompt: str,
        model: str,
        max_tokens: int,
        temperature: float,
        system: str = None,
        keep_alive: str = "30s"
    ) -> str:
        """Direct Ollama API Chat call"""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        # Parse keep_alive to int if it represents seconds or is purely digital, else keep as string
        keep_alive_val = keep_alive
        if isinstance(keep_alive, str) and keep_alive.endswith("s"):
            try:
                keep_alive_val = int(keep_alive[:-1])
            except ValueError:
                pass

        payload: dict = {
            "model": model,
            "messages": messages,
            "stream": False,
            "keep_alive": keep_alive_val,  # Unload from VRAM after specified timeout
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "num_ctx": 2048,  # Optimized local context size to cut prefill latency by 75%
                "top_p": 0.9,
                "repeat_penalty": 1.1
            }
        }

        async with self._session.post(
            f"{self.base_url}/api/chat",
            json=payload
        ) as resp:
            if resp.status != 200:
                raise RuntimeError(
                    f"Ollama HTTP {resp.status}"
                )
            data = await resp.json()
            return data.get("message", {}).get("content", "").strip()

    async def generate_stream(
        self,
        prompt: str,
        model: str = None,
        temperature: float = 0.75
    ) -> AsyncGenerator[str, None]:
        """Streaming generation for real-time response"""
        if not self._ready:
            yield self.FALLBACK
            return

        model = model or self.primary
        messages = [{"role": "user", "content": prompt}]
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": 500
            }
        }

        try:
            async with self._session.post(
                f"{self.base_url}/api/chat",
                json=payload
            ) as resp:
                async for line in resp.content:
                    if line:
                        try:
                            chunk = json.loads(line.decode())
                            token = chunk.get("message", {}).get("content", "")
                            if token:
                                yield token
                            if chunk.get("done"):
                                break
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield self.FALLBACK

    async def embed(self, text: str, is_heavy: bool = False) -> Optional[list]:
        """Generate embeddings for vector memory"""
        if not self._ready:
            return None
            
        # --- ENFORCE 2-MINUTE COOLDOWN FOR HEAVY TASKS ---
        if is_heavy:
            async with self._heavy_lock:
                current_time = time.time()
                time_since_last = current_time - self._last_heavy_time
                if time_since_last < 120.0:
                    wait_time = 120.0 - time_since_last
                    logger.warning(f"[AI] Heavy task throttling active for embed. Waiting {wait_time:.1f}s...")
                    await asyncio.sleep(wait_time)
                self._last_heavy_time = time.time()
                
        try:
            async with self._session.post(
                f"{self.base_url}/api/embeddings",
                json={"model": self.embed_model, "prompt": text},
                timeout=aiohttp.ClientTimeout(total=60) # Increased to handle CPU load
            ) as resp:
                if resp.status != 200:
                    logger.error(f"Embed error: HTTP {resp.status}")
                    return None
                data = await resp.json()
                return data.get("embedding")
        except Exception as e:
            logger.error(f"Embed error: {str(e) or 'Timeout/Connection error'}")
            return None

    async def vision_analyze(
        self,
        prompt: str,
        image_path: str,
        model: str = None
    ) -> str:
        """
        Analyze an image using a Vision-Language Model (VLM).
        Perfect for screen reading and object localization.
        """
        if not self._ready:
            return "Vision Engine not ready."

        import base64
        try:
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Vision error (image load): {e}")
            return f"Error loading image: {e}"

        model = model or self.vision_model
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                    "images": [encoded_string]
                }
            ],
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_ctx": 4096
            }
        }

        try:
            async with self._session.post(
                f"{self.base_url}/api/chat",
                json=payload
            ) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"Ollama Vision HTTP {resp.status}")
                data = await resp.json()
                return data.get("message", {}).get("content", "").strip()
        except Exception as e:
            logger.error(f"Vision error: {e}")
            return f"Vision processing failed: {e}"

    async def find_object(self, object_name: str, image_path: str) -> Optional[list]:
        """
        Specialized vision call to find an object and return [ymin, xmin, ymax, xmax].
        Optimized for Moondream 2.
        """
        prompt = f"Where is the {object_name}? Return only the coordinates in [ymin, xmin, ymax, xmax] format."
        response = await self.vision_analyze(prompt, image_path)
        
        import re
        match = re.search(r'\[(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\]', response)
        if match:
            return [int(x) for x in match.groups()]
        
        # Try finding any 4 numbers if the brackets are missing
        numbers = re.findall(r'\d+', response)
        if len(numbers) >= 4:
            return [int(x) for x in numbers[:4]]
            
        return None

    async def health_check(self) -> bool:
        """Quick health check"""
        try:
            async with self._session.get(
                f"{self.base_url}/api/tags",
                timeout=aiohttp.ClientTimeout(total=3)
            ) as resp:
                return resp.status == 200
        except:
            return False

    def _apply_telugu_few_shot(self, prompt: str) -> str:
        """Injects few-shot examples for Romanized Telugu logic stability."""
        few_shot = """
Example 1:
Input: [Telugu] Nuvvu ela unnav?
Reasoning: [English] User is asking how I am in casual Telugu.
Output: [Telugu] Nenu bagunnanu, Annaya. Meeru ela unnaru?

Example 2:
Input: [Telugu] Ee code enduku work avvatledu?
Reasoning: [English] User is asking why their code is not working. I should provide technical help in mixed Tenglish.
Output: [Telugu] Aa error message chudandi, logic lo chinna mistake undi. Nenu fix cheyanu?

---
"""
        return few_shot + prompt

    async def close(self):
        if self._session:
            await self._session.close()
