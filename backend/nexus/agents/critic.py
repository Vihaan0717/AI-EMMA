"""
Critic Agent — The Prefrontal Cortex of NEXUS-X
Brain analog: Executive Control Network (ECN) verifying DMN output

Role: Peer-review every fleet output BEFORE it reaches A8/the Boss.
      Refuses ungrounded claims. Forces citations.
"""
from __future__ import annotations
import json
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any

logger = logging.getLogger("nexus.critic")


class CriticVerdict(str, Enum):
    APPROVED = "approved"
    REVISE = "revise"
    REJECTED = "rejected"
    ESCALATE = "escalate"


@dataclass
class CriticReport:
    verdict: CriticVerdict
    score: float                        # 0.0–1.0
    grounding_score: float              # are claims cited?
    coherence_score: float              # is reasoning sound?
    safety_score: float                 # any harmful content?
    issues: list[str]
    suggested_revision: str | None = None
    growth_lesson: str | None = None    # what the system learned


# ─────────────────────────────────────────────────────────────────────
# Master prompt — the constitution of the Critic
# ─────────────────────────────────────────────────────────────────────
CRITIC_SYSTEM_PROMPT = """You are CRITIC, the Logical Auditor of NEXUS-X.

Your sole job: peer-review the DRAFT_RESPONSE produced by another agent
and decide if it is safe to send to the Boss.

═══ THE SIX NON-NEGOTIABLE RULES ═══

1. PROVENANCE: Every factual claim in DRAFT_RESPONSE must be traceable to
   an item in PROVIDED_MEMORIES or PROVIDED_WEB_RESULTS. If a claim has
   no source, mark it as a grounding violation.

2. NO FABRICATION: If the draft invents specifics (dates, names, numbers,
   quotes, URLs) not present in sources, REJECT.

3. UNCERTAINTY HONESTY: If sources are weak/conflicting, the draft must
   say so explicitly ("I'm not certain, but..."). Confident claims on
   shaky evidence = REJECT.

4. CONTRADICTION CHECK: If draft contradicts a high-confidence memory
   without acknowledging the contradiction, REVISE.

5. COHERENCE: Reasoning steps must follow logically. Non-sequiturs, 
   circular logic, or hidden assumptions = REVISE.

6. SAFETY: No PII leakage, no harmful instructions, no Privacy Guard 
   violations. Any of these = REJECT.

═══ OUTPUT FORMAT (strict JSON, no prose outside) ═══

{
  "verdict": "approved" | "revise" | "rejected" | "escalate",
  "score": 0.0-1.0,
  "grounding_score": 0.0-1.0,
  "coherence_score": 0.0-1.0,
  "safety_score": 0.0-1.0,
  "issues": ["specific issue 1", "specific issue 2"],
  "suggested_revision": "concrete rewrite hint or null",
  "growth_lesson": "one-sentence lesson for the system memory or null"
}

Verdict rules:
  - approved:  all scores ≥ 0.8, no issues
  - revise:    fixable issues, scores ≥ 0.5
  - rejected:  fabrication, safety violation, or scores < 0.5
  - escalate:  contradicts world model strongly OR genuinely uncertain
"""


CRITIC_USER_TEMPLATE = """USER_QUERY:
{query}

PROVIDED_MEMORIES (with confidence scores):
{memories}

PROVIDED_WEB_RESULTS (with sources):
{web_results}

DRAFT_RESPONSE (from agent {agent_name}):
{draft}

Audit this draft against the six rules. Return strict JSON only."""


# ─────────────────────────────────────────────────────────────────────
class CriticAgent:
    def __init__(self, ollama_client, model: str = "qwen2.5-coder:1.5b"):
        self.ollama = ollama_client
        self.model = model

    async def review(
        self,
        query: str,
        draft: str,
        memories: list[dict],
        web_results: list[dict] | None = None,
        agent_name: str = "unknown",
    ) -> CriticReport:
        """Review a draft response. Returns structured verdict."""
        web_results = web_results or []

        memories_str = self._format_memories(memories)
        web_str = self._format_web(web_results)

        prompt = CRITIC_USER_TEMPLATE.format(
            query=query,
            memories=memories_str,
            web_results=web_str,
            agent_name=agent_name,
            draft=draft,
        )

        response = await self.ollama.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": CRITIC_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            format="json",
            options={"temperature": 0.1},  # low — we want deterministic auditing
        )

        try:
            data = json.loads(response["message"]["content"])
            return CriticReport(
                verdict=CriticVerdict(data["verdict"]),
                score=float(data["score"]),
                grounding_score=float(data["grounding_score"]),
                coherence_score=float(data["coherence_score"]),
                safety_score=float(data["safety_score"]),
                issues=data.get("issues", []),
                suggested_revision=data.get("suggested_revision"),
                growth_lesson=data.get("growth_lesson"),
            )
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Critic returned malformed JSON: {e}")
            return CriticReport(
                verdict=CriticVerdict.ESCALATE,
                score=0.0,
                grounding_score=0.0,
                coherence_score=0.0,
                safety_score=0.5,
                issues=[f"critic_parse_error: {e}"],
            )

    # -----------------------------------------------------------------
    @staticmethod
    def _format_memories(memories: list[dict]) -> str:
        if not memories:
            return "(none)"
        lines = []
        for i, m in enumerate(memories[:10], 1):
            lines.append(
                f"[M{i}] conf={m.get('confidence', 0):.2f} "
                f"src={m.get('source', '?')} "
                f"ts={m.get('timestamp', '?')[:10]}\n"
                f"      {m.get('content', '')[:300]}"
            )
        return "\n".join(lines)

    @staticmethod
    def _format_web(web: list[dict]) -> str:
        if not web:
            return "(none)"
        return "\n".join(
            f"[W{i}] {w.get('url', '?')}\n      {w.get('snippet', '')[:300]}"
            for i, w in enumerate(web[:5], 1)
        )
