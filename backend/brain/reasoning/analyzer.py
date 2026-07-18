"""
DeepAnalyzer — Linguistic and Logical analysis.
Zero AI-API dependency. 
Uses rule-based extraction, regex, and NLP-lite algorithms.
"""

import re
import json
import logging
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger("JARVIS.DeepAnalyzer")

class DeepAnalyzer:
    """
    Performs deep analysis on text and queries without external APIs.
    Responsible for:
      - Sentiment/Tone analysis
      - Keyword/Topic extraction
      - Logical structure extraction (Steps, Algorithms)
      - Pure logic reasoning (Basic arithmetic, truth tables, etc.)
    """

    def __init__(self):
        logger.info("✅ DeepAnalyzer ready — Rule-based mode")

    # ═══════════════════════════════════════════════════════════════
    #  TEXT ANALYSIS
    # ═══════════════════════════════════════════════════════════════

    async def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze text for sentiment, complexity, and keywords."""
        if not text:
            return {}

        sentiment = self._estimate_sentiment(text)
        complexity = self._estimate_complexity(text)
        keywords = self._extract_keywords(text)

        return {
            "sentiment":  sentiment,
            "complexity": complexity,
            "keywords":   keywords,
            "word_count": len(text.split()),
            "analyzed_at": datetime.utcnow().isoformat()
        }

    def _estimate_sentiment(self, text: str) -> str:
        """Estimate sentiment using a word list approach."""
        pos_words = {"good", "great", "excellent", "positive", "happy", "success", "work", "correct", "yes"}
        neg_words = {"bad", "poor", "error", "fail", "negative", "sad", "wrong", "no", "issue", "problem"}
        
        words = set(re.findall(r'\b\w+\b', text.lower()))
        pos_score = len(words & pos_words)
        neg_score = len(words & neg_words)

        if pos_score > neg_score: return "positive"
        if neg_score > pos_score: return "negative"
        return "neutral"

    def _estimate_complexity(self, text: str) -> str:
        """Estimate complexity based on sentence length and vocabulary."""
        sentences = re.split(r'[.!?]+', text)
        avg_sent_len = len(text.split()) / max(len(sentences), 1)
        
        if avg_sent_len > 25: return "high"
        if avg_sent_len > 15: return "medium"
        return "low"

    def _extract_keywords(self, text: str, limit: int = 5) -> List[str]:
        """Extract top keywords by frequency (excluding stopwords)."""
        stops = {"the", "and", "this", "that", "with", "from", "for", "was", "were", "been"}
        words = re.findall(r'\b\w{4,}\b', text.lower())
        freq = {}
        for w in words:
            if w not in stops:
                freq[w] = freq.get(w, 0) + 1
        
        sorted_keys = sorted(freq, key=freq.get, reverse=True)
        return sorted_keys[:limit]

    # ═══════════════════════════════════════════════════════════════
    #  STRUCTURE EXTRACTION
    # ═══════════════════════════════════════════════════════════════

    async def extract_structure(self, query: str, answer: str) -> Dict[str, Any]:
        """
        Extract topic, tags, steps, and algorithms from a response.
        Used for 'learning' from Ollama or Web results.
        """
        # Heuristic for topic
        topic = query.lower()
        topic = re.sub(r'^(what is|how to|who is|explain|tell me about)\s+', '', topic)
        topic = topic.strip()[:60]

        # Extract steps (look for numbered lists)
        steps = re.findall(r'(?m)^\d+\.\s+(.+)$', answer)
        if not steps:
            # Try bullet points
            steps = re.findall(r'(?m)^[\-\*]\s+(.+)$', answer)

        # Heuristic for algorithm
        algorithm = None
        if "algorithm" in answer.lower() or "procedure" in answer.lower():
            # Extract first code block if exists
            code_match = re.search(r'```(?:\w+)?\n([\s\S]+?)\n```', answer)
            if code_match:
                algorithm = code_match.group(1).strip()

        # Generate tags
        tags = self._extract_keywords(f"{query} {answer}", limit=3)
        if steps: tags.append("procedure")
        if algorithm: tags.append("algorithm")

        return {
            "topic":     topic,
            "tags":      tags,
            "steps":     steps,
            "algorithm": algorithm
        }

    # ═══════════════════════════════════════════════════════════════
    #  LOGIC REASONING
    # ═══════════════════════════════════════════════════════════════

    async def pure_logic_reason(self, query: str) -> Dict[str, Any]:
        """
        Perform pure logical or mathematical reasoning for basic queries.
        Fallback when all models fail.
        """
        query = query.lower().strip()

        # 1. Check for basic math
        math_match = re.search(r'(\d+)\s*([\+\-\*/])\s*(\d+)', query)
        if math_match:
            a, op, b = int(math_match.group(1)), math_match.group(2), int(math_match.group(3))
            try:
                if op == '+': res = a + b
                elif op == '-': res = a - b
                elif op == '*': res = a * b
                elif op == '/': res = a / b if b != 0 else "undefined"
                return {
                    "answer": f"The result of {a} {op} {b} is {res}.",
                    "confidence": 1.0,
                    "analysis": {"type": "math"}
                }
            except: pass

        # 2. Check for "hello" style queries
        if any(word in query for word in ["hello", "hi", "hey"]):
            return {
                "answer": "Hello! I am JARVIS. How can I assist you today?",
                "confidence": 0.95,
                "analysis": {"type": "greeting"}
            }

        # 3. Generic logic fallback
        return {
            "answer": f"I analyzed your query: '{query}'. However, I cannot provide a definitive answer using pure logic alone. I recommend checking the knowledge base or connecting to a local model.",
            "confidence": 0.3,
            "analysis": {"type": "failed_logic"}
        }
