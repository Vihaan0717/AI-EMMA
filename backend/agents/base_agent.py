import yaml
import json
import ollama
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from iq_core.memory_manager import AgentMemory

class AgentResponse(BaseModel):
    reasoning: List[str]
    answer: str
    confidence: float
    skill_delta: Dict[str, str] = Field(default_factory=dict)
    new_facts: List[str] = Field(default_factory=list)
    creative_leap: Optional[str] = None
    deeper_question: Optional[str] = None
    threat_model: Optional[str] = None
    growth_experiment: Optional[str] = None
    second_order_effects: Optional[str] = None
    governance_check: Optional[str] = None
    scenario_map: Optional[Dict[str, str]] = None
    explain_simply: Optional[str] = None
    synthesis_insight: Optional[str] = None
    blind_spots: Optional[List[str]] = None

class BaseAgent:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.config_dir = Path("config/agents")
        self.state_dir = Path("data/agents/state")
        self.config_path = self.config_dir / f"{agent_id}.yaml"
        self.state_path = self.state_dir / f"{agent_id}_state.json"
        
        if not self.config_path.exists():
            raise FileNotFoundError(f"Agent config not found: {self.config_path}")
        
        with open(self.config_path, "r", encoding="utf-8") as f:
            self.cfg = yaml.safe_load(f)
        
        self.name = self.cfg["name"]
        self.model = self.cfg.get("model", "llama3.1:8b")
        self.system_prompt = self.cfg["system_prompt"]
        self.skills = self.cfg.get("skills", {})
        
        # Load state if exists
        self.state = self._load_state()
        
        # Working memory (Tier 1)
        self.working_memory = []
        self.memory = AgentMemory(agent_id)

    def _load_state(self) -> Dict[str, Any]:
        if self.state_path.exists():
            with open(self.state_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "skills": self.cfg.get("skills", {}),
            "knowledge": [],
            "iq_history": [],
            "xp": 0,
            "level": 1
        }

    def vocalize_thought(self, text: str):
        """Speak a thought out loud using the agent's unique voice."""
        try:
            from services.voice_speaker import VoiceSpeaker
            speaker = VoiceSpeaker()
            speaker.speak(text, agent_id=self.agent_id)
        except Exception as e:
            pass

    def save_state(self):
        self.state_dir.mkdir(parents=True, exist_ok=True)
        with open(self.state_path, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=2)
        # Also sync to procedural memory
        self.memory.update_procedural(skill_delta=self.state["skills"])

    def chat(self, user_input: str, context: Optional[str] = None) -> AgentResponse:
        # Inject relevant semantic memory
        semantic_context = self.memory.recall_semantic(user_input)
        full_context = context or ""
        if semantic_context:
            full_context += f"\nRelevant past knowledge: {' '.join(semantic_context)}"

        prompt = f"CoT: {user_input}"
        if full_context:
            prompt = f"Context: {full_context}\n\n{prompt}"
        
        messages = [
            {'role': 'system', 'content': self.system_prompt},
            {'role': 'user', 'content': prompt}
        ]
        
        try:
            response = ollama.chat(model=self.model, messages=messages)
            content = response['message']['content']
            
            # Extract JSON
            json_str = content
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "{" in content:
                start = content.find("{")
                end = content.rfind("}")
                if start != -1 and end != -1:
                    json_str = content[start:end+1]
            
            data = json.loads(json_str)
            parsed_response = AgentResponse(**data)
            
            # Update working memory (Tier 1)
            self.working_memory.append({"input": user_input, "output": parsed_response.dict()})
            if len(self.working_memory) > 10:
                self.working_memory.pop(0)
            
            # Store in Episodic (Tier 2)
            self.memory.add_episodic({"input": user_input, "output": parsed_response.dict()})
            
            # Store new facts in Semantic (Tier 3)
            for fact in parsed_response.new_facts:
                self.memory.add_semantic(fact)
                
            # Apply skill deltas to state & Procedural (Tier 4)
            if parsed_response.skill_delta:
                for skill, level in parsed_response.skill_delta.items():
                    self.state["skills"][skill] = level
                self.save_state()
                
            return parsed_response
        except Exception as e:
            return AgentResponse(
                reasoning=["Failed to process response", str(e)],
                answer=f"Error processing agent output: {str(e)}",
                confidence=0.0
            )

    async def think(self, prompt: str, parsed_input: Any = None) -> AgentResponse:
        """Async version of chat for the live engine."""
        return self.chat(prompt)

    def apply_skill_delta(self, skill_delta: Dict[str, str]):
        """Apply skill updates from the live learning protocol."""
        if isinstance(skill_delta, dict):
            # If it's a single delta {name, level, info}
            if "name" in skill_delta and "level" in skill_delta:
                self.state["skills"][skill_delta["name"]] = skill_delta["level"]
            else:
                # If it's multiple deltas {skill: level}
                for skill, level in skill_delta.items():
                    self.state["skills"][skill] = level
            self.save_state()

    def update_iq(self, score: float):
        self.state["iq_history"].append(score)
        if len(self.state["iq_history"]) > 30:
            self.state["iq_history"].pop(0)
        self.save_state()
