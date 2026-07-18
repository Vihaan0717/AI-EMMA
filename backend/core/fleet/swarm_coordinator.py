"""
NEXUS-X Swarm Coordinator — Agent-to-Agent Delegation & Synthesis
==================================================================
Replaces the old linear sequential pipeline with a dynamic swarm model:

  - Any agent can call `delegate(to_agent, sub_task)` mid-execution
  - The coordinator spawns a mini ReAct loop for the target agent
  - Results are returned to the requesting agent
  - Prevents circular delegation (A → B → A) with depth limits
  - Tracks the full delegation tree for audit/debugging

Architecture:
  Primary Agent (e.g., Hank)
    ├── delegates to Atlas (research)
    │     └── returns findings
    ├── delegates to Cosmos (science check)
    │     └── returns verification
    └── synthesizes final answer from all contributions
"""

import logging
import time
import json
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field

logger = logging.getLogger("SwarmCoordinator")

MAX_DELEGATION_DEPTH = 3          # Prevent infinite delegation chains
MAX_CONCURRENT_DELEGATIONS = 4   # Max sub-tasks per primary task


@dataclass
class DelegationRecord:
    """Record of a single delegation in the swarm."""
    from_agent: str
    to_agent: str
    task: str
    result: str = ""
    success: bool = False
    elapsed_ms: float = 0.0
    depth: int = 0


@dataclass
class SwarmTrace:
    """Full trace of all delegations in a swarm execution."""
    primary_agent: str
    primary_task: str
    delegations: List[DelegationRecord] = field(default_factory=list)
    total_agents_involved: int = 1
    total_elapsed_ms: float = 0.0


class SwarmCoordinator:
    """
    Manages inter-agent delegation within the fleet.
    When an agent needs help from another specialist, it calls `delegate()`
    which spawns a mini ReAct execution for the target agent.
    """

    def __init__(self):
        self._active_chains: Dict[str, Set[str]] = {}  # task_id → set of agents already in chain
        self._ai_engine = None
        self._personas = None
        logger.info("SwarmCoordinator initialized.")

    def set_ai_engine(self, engine):
        self._ai_engine = engine

    def set_personas(self, personas):
        self._personas = personas

    async def delegate(
        self,
        from_agent: str,
        to_agent: str,
        task: str,
        depth: int = 0,
        chain_id: str = None
    ) -> str:
        """
        Delegate a sub-task from one agent to another.

        Args:
            from_agent: ID of the requesting agent
            to_agent: ID of the target agent
            task: The sub-task description
            depth: Current delegation depth (for recursion control)
            chain_id: Unique chain ID to track circular references

        Returns:
            The target agent's response as a string
        """
        # ── Safety checks ────────────────────────────────────────────
        if depth >= MAX_DELEGATION_DEPTH:
            msg = f"SWARM: Delegation depth limit ({MAX_DELEGATION_DEPTH}) reached. Returning partial."
            logger.warning(msg)
            return msg

        if chain_id is None:
            chain_id = f"swarm_{int(time.time() * 1000)}"

        # Circular reference check
        if chain_id not in self._active_chains:
            self._active_chains[chain_id] = set()
        if to_agent.lower() in self._active_chains[chain_id]:
            msg = f"SWARM: Circular delegation detected ({from_agent} → {to_agent}). Blocked."
            logger.warning(msg)
            return msg
        self._active_chains[chain_id].add(to_agent.lower())

        logger.info(
            f"SWARM: {from_agent} → {to_agent} (depth={depth}, chain={chain_id}): "
            f"'{task[:80]}...'"
        )

        start = time.perf_counter()

        try:
            result = await self._execute_delegate(to_agent, task, depth, chain_id)
        except Exception as e:
            logger.error(f"SWARM: Delegation to {to_agent} failed: {e}")
            result = f"Delegation error: {e}"
        finally:
            # Cleanup chain tracking
            if chain_id in self._active_chains:
                self._active_chains[chain_id].discard(to_agent.lower())
                if not self._active_chains[chain_id]:
                    del self._active_chains[chain_id]

        elapsed = round((time.perf_counter() - start) * 1000, 2)
        logger.info(f"SWARM: {to_agent} completed in {elapsed}ms (result={len(result)} chars)")

        return result

    async def _execute_delegate(
        self,
        agent_id: str,
        task: str,
        depth: int,
        chain_id: str
    ) -> str:
        """
        Execute a delegated sub-task using a lightweight ReAct loop.
        Uses fewer steps than the primary loop (max 3 steps for sub-tasks).
        """
        if not self._ai_engine:
            return "ERROR: AI engine not available for delegation."

        if not self._personas:
            from core.fleet.personas import FleetPersonas
            self._personas = FleetPersonas()

        persona = self._personas.get_persona(agent_id)

        # Build a delegation-specific system prompt
        from core.fleet.react_engine import react_engine
        system_prompt = react_engine.build_react_system_prompt(
            persona["system_prompt"],
            agent_id
        )

        # Add delegation context
        system_prompt += (
            f"\n\n[DELEGATION CONTEXT]\n"
            f"You have been delegated a sub-task by another agent.\n"
            f"Focus ONLY on this specific sub-task. Be concise and precise.\n"
            f"Delegation depth: {depth + 1}/{MAX_DELEGATION_DEPTH}\n"
        )

        # Execute with reduced step limit for sub-tasks
        trace = await react_engine.execute(
            agent_id=agent_id,
            task=task,
            system_prompt=system_prompt,
            ai_engine=self._ai_engine,
            temperature=persona.get("temperature", 0.5),
            max_steps=3  # Shorter loop for delegated tasks
        )

        return trace.final_answer

    async def multi_delegate(
        self,
        from_agent: str,
        delegations: List[Dict[str, str]]
    ) -> Dict[str, str]:
        """
        Delegate multiple sub-tasks in parallel.

        Args:
            from_agent: The requesting agent
            delegations: List of {"agent": "target_id", "task": "description"}

        Returns:
            Dict mapping agent_id to their response
        """
        import asyncio

        if len(delegations) > MAX_CONCURRENT_DELEGATIONS:
            logger.warning(f"SWARM: Too many delegations ({len(delegations)}). Capping at {MAX_CONCURRENT_DELEGATIONS}.")
            delegations = delegations[:MAX_CONCURRENT_DELEGATIONS]

        chain_id = f"multi_{int(time.time() * 1000)}"
        tasks = []
        for d in delegations:
            target = d.get("agent", "")
            sub_task = d.get("task", "")
            tasks.append(self.delegate(from_agent, target, sub_task, chain_id=chain_id))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        response = {}
        for i, d in enumerate(delegations):
            agent = d.get("agent", f"agent_{i}")
            if isinstance(results[i], Exception):
                response[agent] = f"Error: {results[i]}"
            else:
                response[agent] = results[i]

        return response

    def get_agent_capabilities_summary(self) -> str:
        """
        Generate a summary of all agents and their specializations.
        Useful for agents deciding who to delegate to.
        """
        from core.fleet.personas import FleetPersonas

        lines = ["[FLEET AGENT CAPABILITIES]"]
        for agent_id, persona in FleetPersonas.PERSONAS.items():
            if agent_id == "critic":
                continue  # Critic is internal, not delegatable
            lines.append(f"  - {agent_id.upper()} ({persona['role']}): {persona.get('memory_focus', 'General')}")

        lines.append("")
        lines.append("Use [TOOL_CALL] {\"tool\": \"delegate\", \"params\": {\"target_agent\": \"agent_id\", \"sub_task\": \"description\"}} [/TOOL_CALL] to delegate.")
        return "\n".join(lines)


# ── Global Singleton ──────────────────────────────────────────────
swarm_coordinator = SwarmCoordinator()
