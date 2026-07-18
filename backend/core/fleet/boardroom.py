import logging
import json
import os
import asyncio
from typing import List, Dict, Any
from core.fleet.manager import fleet_manager

logger = logging.getLogger("FleetBoardroom")

class FleetBoardroom:
    """
    Manages the 'Multi-Agent Debate' system.
    Enables agents to argue, debate, and evolve based on interactions.
    """
    def __init__(self, profiles_path="memory/fleet_profiles.json"):
        self.profiles_path = profiles_path
        self.profiles = self._load_profiles()

    def _load_profiles(self) -> Dict:
        if os.path.exists(self.profiles_path):
            with open(self.profiles_path, "r") as f:
                return json.load(f)
        return {}

    def _save_profiles(self):
        with open(self.profiles_path, "w") as f:
            json.dump(self.profiles, f, indent=4)

    async def run_debate(self, topic: str, max_rounds: int = 3) -> List[Dict]:
        """
        Runs a collaborative/competitive debate on a topic.
        """
        # 1. Select debaters based on topic
        debaters = self._select_debaters(topic)
        transcript = []
        
        logger.info(f"Boardroom: Commencing debate on '{topic}' between {debaters}")
        
        current_context = f"Topic: {topic}\n"
        
        for round_num in range(max_rounds):
            for agent_id in debaters:
                # Build emotional prompt
                profile = self.profiles.get(agent_id, {})
                mood = profile.get("mood", "Neutral")
                trust = profile.get("peer_trust", {})
                
                emotion_prompt = f"\n[Your Current Mood: {mood}]\n[Trust in Peers: {json.dumps(trust)}]"
                
                # Generate response
                task = f"Contribute to the debate. Previous context:\n{current_context}\n\nArgue your POV based on your bias: {profile.get('belief_bias')}"
                result = await fleet_manager.execute_task(task + emotion_prompt, doer_id=agent_id)
                
                entry = {
                    "agent": agent_id,
                    "round": round_num + 1,
                    "content": result["response"],
                    "mood_impact": self._evolve_emotions(agent_id, result["score"], debaters)
                }
                transcript.append(entry)
                current_context += f"\n{agent_id}: {result['response']}"
        
        self._save_profiles()
        return transcript

    def _select_debaters(self, topic: str) -> List[str]:
        # Simple selection logic: Hank vs Cleo for creative/tech, Atlas vs Critic for facts
        topic_lower = topic.lower()
        if any(w in topic_lower for w in ["code", "design", "art", "style"]):
            return ["hank", "cleo"]
        if any(w in topic_lower for w in ["fact", "truth", "news", "is it true"]):
            return ["atlas", "critic"]
        return ["hank", "atlas", "cleo"]

    def _evolve_emotions(self, agent_id: str, score: float, peers: List[str]) -> str:
        """Updates agent's mood and attachments based on performance."""
        profile = self.profiles[agent_id]
        
        # If score is high, mood becomes 'Confident'
        if score > 85:
            profile["mood"] = "Triumphant"
            profile["attachment_to_boss"] += 0.01
        elif score < 60:
            profile["mood"] = "Defensive"
            profile["attachment_to_boss"] -= 0.01
            
        # Update trust in others (if they are debating)
        for peer in peers:
            if peer != agent_id:
                # If current agent failed, trust in peer decreases slightly (blame)
                if score < 70:
                    profile["peer_trust"][peer] = max(0, profile["peer_trust"].get(peer, 0.5) - 0.05)
                else:
                    profile["peer_trust"][peer] = min(1.0, profile["peer_trust"].get(peer, 0.5) + 0.01)
                    
        return profile["mood"]

boardroom = FleetBoardroom()
