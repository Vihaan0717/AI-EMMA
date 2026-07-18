import logging
from enum import Enum
from typing import Dict, Any, List

logger = logging.getLogger("ExecutiveA14")

class NexusMode(Enum):
    ENGINEER = "engineer"
    BUDDY    = "buddy"
    SCHOLAR  = "scholar"
    PASSIVE  = "passive"

class MissionBrief:
    def __init__(self, mode: NexusMode, lead_agent: str, priorities: List[str], focus: str):
        self.mode = mode
        self.lead_agent = lead_agent
        self.priorities = priorities
        self.focus = focus

class ExecutiveA14:
    """
    A14 Executive Decision Layer.
    Orchestrates the Fleet based on environment, time, and user intent.
    """
    def __init__(self, fleet_manager):
        self.fleet = fleet_manager
        self.current_mode = NexusMode.BUDDY
        self.mode_configs = {
            NexusMode.ENGINEER: MissionBrief(
                mode=NexusMode.ENGINEER,
                lead_agent="hank",
                priorities=["hank", "atlas", "critic"],
                focus="Technical building, low-latency code, and logical verification."
            ),
            NexusMode.BUDDY: MissionBrief(
                mode=NexusMode.BUDDY,
                lead_agent="arion",
                priorities=["arion", "cleo"],
                focus="Cultural connection, Hyderabad slang, and creative ideas."
            ),
            NexusMode.SCHOLAR: MissionBrief(
                mode=NexusMode.SCHOLAR,
                lead_agent="critic",
                priorities=["critic", "atlas", "hank", "cleo"],
                focus="Autonomous learning, linguistic verification, and walking simulations."
            ),
            NexusMode.PASSIVE: MissionBrief(
                mode=NexusMode.PASSIVE,
                lead_agent="atlas",
                priorities=["atlas"],
                focus="Linguistic candidate detection and background research."
            )
        }

    async def set_mode(self, mode: NexusMode):
        """Switches the system mode and issues a new Mission Brief to the fleet."""
        if mode == self.current_mode:
            return

        self.current_mode = mode
        brief = self.mode_configs[mode]
        
        logger.info(f"[A14] COMMAND: Switching to {mode.value.upper()} Mode.")
        logger.info(f"[A14] MISSION BRIEF: Lead={brief.lead_agent} | Focus={brief.focus}")
        
        # Apply to fleet
        if hasattr(self.fleet, "apply_mission_brief"):
            await self.fleet.apply_mission_brief(brief)

    def decide_mode(self, input_text: str, source: str) -> NexusMode:
        """Heuristic-based mode selection based on input context."""
        text = input_text.lower()
        
        if any(w in text for w in ["code", "build", "fix", "debug", "python", "script"]):
            return NexusMode.ENGINEER
        if any(w in text for w in ["nexus, listen", "idi nerchuko", "learn this"]):
            return NexusMode.SCHOLAR
        if source in ["whatsapp", "telegram"] or any(w in text for w in ["buddy", "arion", "chala", "bagundi"]):
            return NexusMode.BUDDY
            
        return self.current_mode
