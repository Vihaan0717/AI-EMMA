"""
SmartReasoningEngine — The Core Brain
Priority Chain:
  1. Pattern Match (Instant, learned from past)
  2. Knowledge Base (Structured stored facts)
  3. Ollama Local LLM (Private, no cloud)
  4. Web Search Fallback (DuckDuckGo, no API key)
  5. Pure Logic Analysis (Rules + algorithms)
  6. Learn & Store Everything for next time
"""

import asyncio
import logging
import time
from typing import Optional, Dict, Any
from datetime import datetime

from .pattern_learner import PatternLearner
from .knowledge_base import KnowledgeBase
from .web_fallback import WebFallback
from .analyzer import DeepAnalyzer

logger = logging.getLogger("JARVIS.ReasoningEngine")


class SmartReasoningEngine:
    """
    100% Efficient Reasoning Engine.
    No Google API. No Gemini. No Groq. No token costs.
    Gets smarter with every single query.
    """

    # ─── Thresholds ───────────────────────────────────────────────
    PATTERN_CONFIDENCE_THRESHOLD = 0.82   # Use pattern if ≥82% match
    KB_CONFIDENCE_THRESHOLD      = 0.75   # Use KB if ≥75% relevance
    OLLAMA_TIMEOUT_SECONDS       = 12     # Give Ollama 12s before fallback
    # ──────────────────────────────────────────────────────────────

    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url    = ollama_url
        self.pattern       = PatternLearner()
        self.kb            = KnowledgeBase()
        self.web           = WebFallback()
        self.analyzer      = DeepAnalyzer()
        self._query_count  = 0
        logger.info("✅ SmartReasoningEngine initialized — Zero API dependency mode")

    # ═══════════════════════════════════════════════════════════════
    #  PUBLIC — Main entry point
    # ═══════════════════════════════════════════════════════════════

    async def think(
        self,
        query: str,
        context: Optional[Dict] = None,
        force_web: bool = False
    ) -> Dict[str, Any]:
        """
        The single function you call for everything.
        Returns a structured response dict with source, answer, confidence,
        analysis, and any learned patterns.
        """
        start = time.perf_counter()
        self._query_count += 1
        query = query.strip()

        logger.info(f"🧠 Query #{self._query_count}: {query[:80]}...")

        # ── STEP 1: Pattern recognition (fastest, ~0ms) ───────────
        if not force_web:
            pattern_result = await self._check_patterns(query)
            if pattern_result:
                return self._build_response(
                    query, pattern_result, source="pattern_memory",
                    elapsed=time.perf_counter() - start
                )

        # ── STEP 2: Knowledge base lookup (~1ms) ──────────────────
        if not force_web:
            kb_result = await self._check_knowledge_base(query)
            if kb_result:
                return self._build_response(
                    query, kb_result, source="knowledge_base",
                    elapsed=time.perf_counter() - start
                )

        # ── STEP 3: Local Ollama (~2-12s) ─────────────────────────
        if not force_web:
            ollama_result = await self._try_ollama(query, context)
            if ollama_result:
                # Learn from this Ollama response
                await self._learn_and_store(query, ollama_result, source="ollama")
                return self._build_response(
                    query, ollama_result, source="ollama_local",
                    elapsed=time.perf_counter() - start
                )

        # ── STEP 4: Web search fallback (no API key needed) ───────
        logger.warning("⚠️ Ollama unavailable → Switching to Web Fallback")
        web_result = await self._web_search_and_analyze(query)
        if web_result:
            await self._learn_and_store(query, web_result, source="web")
            return self._build_response(
                query, web_result, source="web_search",
                elapsed=time.perf_counter() - start
            )

        # ── STEP 5: Pure logic reasoning (always works) ───────────
        logger.warning("⚠️ Web fallback failed → Pure logic reasoning")
        logic_result = await self.analyzer.pure_logic_reason(query)
        return self._build_response(
            query, logic_result, source="pure_logic",
            elapsed=time.perf_counter() - start
        )

    # ═══════════════════════════════════════════════════════════════
    #  PRIVATE — Step handlers
    # ═══════════════════════════════════════════════════════════════

    async def _check_patterns(self, query: str) -> Optional[Dict]:
        """Check learned patterns for a high-confidence match."""
        try:
            match = self.pattern.find_best_match(query)
            if match and match["confidence"] >= self.PATTERN_CONFIDENCE_THRESHOLD:
                logger.info(f"✅ Pattern match: {match['confidence']:.0%} confidence")
                return match
        except Exception as e:
            logger.error(f"Pattern check failed: {e}")
        return None

    async def _check_knowledge_base(self, query: str) -> Optional[Dict]:
        """Search structured knowledge base."""
        try:
            result = self.kb.smart_search(query)
            if result and result.get("relevance", 0) >= self.KB_CONFIDENCE_THRESHOLD:
                logger.info(f"✅ KB match: relevance={result['relevance']:.0%}")
                return result
        except Exception as e:
            logger.error(f"KB search failed: {e}")
        return None

    async def _try_ollama(
        self, query: str, context: Optional[Dict]
    ) -> Optional[Dict]:
        """Try local Ollama with a timeout guard."""
        try:
            import httpx
            prompt = self._build_smart_prompt(query, context)
            async with httpx.AsyncClient(timeout=self.OLLAMA_TIMEOUT_SECONDS) as client:
                resp = await client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": "llama3.1",
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.3,   # Low temp = more deterministic
                            "top_p": 0.9,
                            "num_predict": 1024
                        }
                    }
                )
                if resp.status_code == 200:
                    data = resp.json()
                    raw_answer = data.get("response", "").strip()
                    if raw_answer:
                        # Deep-analyze the Ollama output
                        analysis = await self.analyzer.analyze_text(raw_answer)
                        return {
                            "answer": raw_answer,
                            "analysis": analysis,
                            "confidence": 0.88
                        }
        except Exception as e:
            logger.warning(f"Ollama failed: {type(e).__name__}: {e}")
        return None

    async def _web_search_and_analyze(self, query: str) -> Optional[Dict]:
        """DuckDuckGo search + deep extraction. No API key."""
        try:
            raw = await self.web.search(query)
            if not raw:
                return None
            analysis = await self.analyzer.analyze_text(raw["combined_text"])
            return {
                "answer": raw["best_answer"],
                "analysis": analysis,
                "sources": raw["sources"],
                "confidence": raw["confidence"]
            }
        except Exception as e:
            logger.error(f"Web fallback failed: {e}")
        return None

    async def _learn_and_store(
        self, query: str, result: Dict, source: str
    ) -> None:
        """
        Store the result in both Pattern Learner and Knowledge Base.
        This is how JARVIS gets smarter over time.
        """
        try:
            # Extract structured data from the answer
            structured = await self.analyzer.extract_structure(
                query, result.get("answer", "")
            )

            # Store in pattern DB (for fast future matching)
            self.pattern.store_pattern(
                query=query,
                response=result,
                source=source,
                tags=structured.get("tags", []),
                algorithm=structured.get("algorithm"),
                steps=structured.get("steps", [])
            )

            # Store in knowledge base (for topic browsing)
            self.kb.store(
                topic=structured.get("topic", query[:60]),
                content=result.get("answer", ""),
                analysis=result.get("analysis", {}),
                source=source,
                tags=structured.get("tags", [])
            )

            logger.info(
                f"🧠 Learned & stored: topic='{structured.get('topic')}' "
                f"tags={structured.get('tags')}"
            )
        except Exception as e:
            logger.error(f"Learn/store failed: {e}")

    # ═══════════════════════════════════════════════════════════════
    #  UTILITIES
    # ═══════════════════════════════════════════════════════════════

    def _build_smart_prompt(
        self, query: str, context: Optional[Dict]
    ) -> str:
        """
        Build a focused, efficient prompt.
        Reduces token waste by being precise and structured.
        """
        ctx_str = ""
        if context:
            ctx_str = f"\nContext: {context}\n"

        return f"""You are JARVIS, an expert assistant. Answer with precision.
{ctx_str}
Query: {query}

Instructions:
1. Give a direct, accurate answer first
2. Provide step-by-step reasoning if applicable  
3. Include any relevant algorithm or pattern
4. Flag any uncertainty clearly
5. Be concise — no filler words

Answer:"""

    def _build_response(
        self,
        query: str,
        result: Dict,
        source: str,
        elapsed: float
    ) -> Dict[str, Any]:
        """Standardized response format for all sources."""
        return {
            "query":      query,
            "answer":     result.get("answer", ""),
            "analysis":   result.get("analysis", {}),
            "sources":    result.get("sources", []),
            "confidence": result.get("confidence", 0.0),
            "source":     source,
            "elapsed_ms": round(elapsed * 1000, 2),
            "timestamp":  datetime.utcnow().isoformat(),
            "from_cache": source in ("pattern_memory", "knowledge_base"),
            "learned":    source not in ("pattern_memory", "knowledge_base"),
        }

    def stats(self) -> Dict:
        """Return engine statistics."""
        return {
            "total_queries": self._query_count,
            "patterns_stored": self.pattern.count(),
            "kb_entries": self.kb.count(),
            "engine_version": "1.0.0"
        }
