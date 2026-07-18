"""
A2.5 Predictive Gate — The Anti-Hallucination Firewall
Brain analog: Predictive Coding (Friston/Clark Free Energy framework)

Purpose: Reject or flag inputs/outputs that contradict the world model
         without verification. This is the single most important layer
         for preventing fabrication.
"""
from __future__ import annotations
import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import numpy as np

logger = logging.getLogger("nexus.predictive_gate")


# ─────────────────────────────────────────────────────────────────────
# Decision types
# ─────────────────────────────────────────────────────────────────────
class GateDecision(str, Enum):
    PASS = "pass"                       # Expected, low surprise
    PASS_WITH_FLAG = "pass_flagged"     # Plausible but needs verification
    REJECT = "reject"                   # Contradicts established memory
    REQUIRE_HUMAN = "require_human"     # High surprise, escalate to Boss
    REQUIRE_VERIFICATION = "verify"     # Send to Atlas for fact-check


@dataclass
class GateResult:
    decision: GateDecision
    confidence: float                   # 0.0–1.0
    prediction_error: float             # semantic distance
    reason: str
    contradicting_memories: list[str] = field(default_factory=list)
    supporting_memories: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "decision": self.decision.value,
            "confidence": self.confidence,
            "prediction_error": self.prediction_error,
            "reason": self.reason,
            "contradicting": self.contradicting_memories,
            "supporting": self.supporting_memories,
            "ts": self.timestamp.isoformat(),
        }


# ─────────────────────────────────────────────────────────────────────
# The Gate
# ─────────────────────────────────────────────────────────────────────
class PredictiveGate:
    """
    Inserts between A2 (Memory Recall) and A3 (Comprehension).
    
    Usage:
        gate = PredictiveGate(qdrant_client, embedder)
        result = await gate.evaluate(input_text, recalled_memories)
        if result.decision == GateDecision.REJECT:
            return "I don't have reliable information on that."
    """

    # Tunable thresholds — calibrate against your domain
    LOW_ERROR_THRESHOLD = 0.25          # below = expected
    HIGH_ERROR_THRESHOLD = 0.65         # above = surprising
    CONTRADICTION_THRESHOLD = 0.80      # cosine distance for "opposes"
    MIN_CONTRADICTING_MEMORIES = 3      # how many must oppose to reject
    MIN_MEMORY_CONFIDENCE = 0.6         # ignore low-confidence memories in gate

    def __init__(self, qdrant_client, embedder, audit_log=None):
        self.qdrant = qdrant_client
        self.embedder = embedder
        self.audit_log = audit_log      # Supabase logger (optional)

    # -----------------------------------------------------------------
    async def evaluate(
        self,
        input_content: str,
        recalled_memories: list[dict],
        context: dict | None = None,
    ) -> GateResult:
        """
        Main entry point. Evaluates whether `input_content` is consistent
        with the world model represented by `recalled_memories`.
        """
        context = context or {}

        # 1. Embed the incoming claim
        input_vec = await self.embedder.embed(input_content)

        # 2. Generate prediction from prior model (weighted centroid)
        prediction_vec, prior_strength = self._build_prediction(recalled_memories)

        # 3. Compute prediction error
        if prediction_vec is None:
            # No prior knowledge — treat as novel, flag for verification
            return GateResult(
                decision=GateDecision.REQUIRE_VERIFICATION,
                confidence=0.4,
                prediction_error=1.0,
                reason="no_prior_knowledge",
            )

        error = self._cosine_distance(input_vec, prediction_vec)

        # 4. Find contradicting & supporting memories
        contradicting, supporting = self._classify_memories(
            input_vec, recalled_memories
        )

        # 5. Decision tree
        result = self._decide(error, prior_strength, contradicting, supporting)

        # 6. Audit
        if self.audit_log:
            await self.audit_log.record_gate_decision(
                input_content, result, context
            )

        logger.info(
            f"[PredictiveGate] decision={result.decision} "
            f"err={error:.3f} contradicts={len(contradicting)}"
        )
        return result

    # -----------------------------------------------------------------
    def _build_prediction(
        self, memories: list[dict]
    ) -> tuple[np.ndarray | None, float]:
        """Weighted centroid of high-confidence relevant memories."""
        usable = [
            m for m in memories
            if m.get("confidence", 0) >= self.MIN_MEMORY_CONFIDENCE
            and m.get("vector") is not None
        ]
        if not usable:
            return None, 0.0

        vectors = np.array([m["vector"] for m in usable])
        weights = np.array([
            m["confidence"] * (m.get("access_count", 1) ** 0.5)
            for m in usable
        ])
        weights = weights / weights.sum()
        centroid = (vectors * weights[:, None]).sum(axis=0)
        prior_strength = min(1.0, len(usable) / 5.0)  # saturates at 5 memories
        return centroid, prior_strength

    # -----------------------------------------------------------------
    def _classify_memories(
        self, input_vec: np.ndarray, memories: list[dict]
    ) -> tuple[list[str], list[str]]:
        """Split memories into those that contradict vs. support input."""
        contradicting, supporting = [], []
        for m in memories:
            if m.get("vector") is None:
                continue
            dist = self._cosine_distance(input_vec, np.array(m["vector"]))

            # Contradiction = high distance AND high-confidence memory
            if (dist > self.CONTRADICTION_THRESHOLD
                and m.get("confidence", 0) > self.MIN_MEMORY_CONFIDENCE):
                contradicting.append(m["id"])
            elif dist < 0.3:
                supporting.append(m["id"])
        return contradicting, supporting

    # -----------------------------------------------------------------
    def _decide(
        self,
        error: float,
        prior_strength: float,
        contradicting: list[str],
        supporting: list[str],
    ) -> GateResult:
        # Hard reject: too many high-confidence memories disagree
        if len(contradicting) >= self.MIN_CONTRADICTING_MEMORIES:
            return GateResult(
                decision=GateDecision.REJECT,
                confidence=0.9,
                prediction_error=error,
                reason=f"contradicts_{len(contradicting)}_memories",
                contradicting_memories=contradicting,
                supporting_memories=supporting,
            )

        # Low surprise or short social chatter: pass silently
        if error < self.LOW_ERROR_THRESHOLD or len(input_content) < 40:
            return GateResult(
                decision=GateDecision.PASS,
                confidence=0.95,
                prediction_error=error,
                reason="expected_or_social",
                supporting_memories=supporting,
            )

        # Mid surprise: pass but verify
        if error < self.HIGH_ERROR_THRESHOLD:
            return GateResult(
                decision=GateDecision.PASS_WITH_FLAG,
                confidence=0.6,
                prediction_error=error,
                reason="plausible_unverified",
                supporting_memories=supporting,
            )

        # High surprise with weak priors: verify externally
        if prior_strength < 0.4:
            return GateResult(
                decision=GateDecision.REQUIRE_VERIFICATION,
                confidence=0.4,
                prediction_error=error,
                reason="high_surprise_weak_priors",
            )

        # High surprise with strong priors: escalate to Boss
        return GateResult(
            decision=GateDecision.REQUIRE_HUMAN,
            confidence=0.3,
            prediction_error=error,
            reason="high_surprise_strong_priors",
            contradicting_memories=contradicting,
        )

    # -----------------------------------------------------------------
    @staticmethod
    def _cosine_distance(a: np.ndarray, b: np.ndarray) -> float:
        denom = np.linalg.norm(a) * np.linalg.norm(b)
        if denom == 0:
            return 1.0
        return float(1.0 - np.dot(a, b) / denom)
