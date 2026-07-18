import json
import logging
import asyncio
import os
from typing import List, Dict
from nexus.agents.evaluator_agent import EvaluatorAgent

logger = logging.getLogger("nexus.learning.optimizer")

class PatternOptimizer:
    """
    Pattern Optimizer — The "Dreaming" Layer.
    Runs periodically to consolidate short-term feedback into long-term patterns.
    """
    def __init__(self, evaluator: EvaluatorAgent, knowledge_path: str = "data/knowledge_graph.json"):
        self.evaluator = evaluator
        self.knowledge_path = knowledge_path
        self._ensure_knowledge_base()

    def _ensure_knowledge_base(self):
        if not os.path.exists(self.knowledge_path):
            with open(self.knowledge_path, "w", encoding="utf-8") as f:
                json.dump({"patterns": [], "rules": {}}, f)

    async def optimize_patterns(self):
        """Analyzes recent feedback and extracts new rules."""
        logger.info("PatternOptimizer: Commencing pattern consolidation loop...")
        
        corrections = self.evaluator.get_corrections()
        if not corrections:
            logger.info("PatternOptimizer: No new corrections found. Skipping.")
            return

        new_rules = []
        for corr in corrections:
            # Analyze correction to extract a rule
            # Rule format: { "if": "...", "then": "..." }
            rule = self._extract_rule_from_correction(corr)
            if rule:
                new_rules.append(rule)

        if new_rules:
            self._update_knowledge_base(new_rules)
            logger.info(f"PatternOptimizer: Successfully extracted {len(new_rules)} new rules.")

    def _extract_rule_from_correction(self, correction_data: Dict) -> Optional[Dict]:
        """
        Heuristic to turn a user correction into a reusable rule.
        """
        # Placeholder for complex logic
        # Example: User said "it should be 'Annaya' not 'Bro'"
        # Rule: { "context": "elder_brother", "preferred_address": "Annaya" }
        user_input = correction_data.get("user_input", "")
        agent_response = correction_data.get("agent_response", "")
        correction = correction_data.get("correction_extracted", "")

        if not correction: return None

        return {
            "trigger": user_input[:50],
            "rejected_pattern": agent_response[:50],
            "correct_pattern": correction,
            "timestamp": correction_data.get("timestamp")
        }

    def _update_knowledge_base(self, new_rules: List[Dict]):
        with open(self.knowledge_path, "r", encoding="utf-8") as f:
            kb = json.load(f)
        
        kb["patterns"].extend(new_rules)
        # Keep only unique/latest patterns
        kb["patterns"] = kb["patterns"][-500:] 
        
        with open(self.knowledge_path, "w", encoding="utf-8") as f:
            json.dump(kb, f, indent=4, ensure_ascii=False)

    async def run_periodic(self, interval_seconds: int = 3600):
        """Runs the optimizer every N seconds."""
        while True:
            await self.optimize_patterns()
            await asyncio.sleep(interval_seconds)
