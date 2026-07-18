import json
from agents.agent_registry import get_all_agents, get_agent
from iq_core.memory_manager import AgentMemory

DEBATE_TOPICS = {
    "monday":    "What is the single biggest risk to our system right now?",
    "tuesday":   "What should we build next and why?",
    "wednesday": "What did we get wrong this week?",
    "thursday":  "How do we make the system 10x more valuable?",
    "friday":    "What would we do differently if we started over today?",
}

class DebateSession:
    def __init__(self, topic_day: str = "monday"):
        self.topic = DEBATE_TOPICS.get(topic_day.lower(), DEBATE_TOPICS["monday"])
        self.agents = get_all_agents()

    def run_debate(self):
        print(f"--- DEBATE SESSION: {self.topic} ---")
        
        # 1. Gather all perspectives
        responses = {}
        for agent in self.agents:
            if agent.agent_id in ["zero", "iris", "sage", "rex"]:
                continue # These have special roles later
            
            print(f"{agent.name} is thinking...")
            resp = agent.chat(f"DEBATE TOPIC: {self.topic}. Provide your unique perspective.")
            responses[agent.agent_id] = resp.dict()

        # 2. Zero Issues Verdict
        zero = get_agent("zero")
        print("Zero is issuing a verdict...")
        verdict_prompt = f"Topic: {self.topic}\nAgent Perspectivies: {json.dumps(responses)}\n\nReview all perspectives and issue a final strategic verdict."
        verdict = zero.chat(verdict_prompt)
        
        # 3. Iris Synthesizes
        iris = get_agent("iris")
        print("Iris is synthesizing insights...")
        synthesis_prompt = f"Topic: {self.topic}\nPerspectives & Verdict: {json.dumps({'responses': responses, 'verdict': verdict.dict()})}\n\nFind the hidden pattern or synthesis everyone missed."
        synthesis = iris.chat(synthesis_prompt)
        
        # 4. Sage Explains Simply
        sage = get_agent("sage")
        print("Sage is simplifying...")
        sage_prompt = f"Explain this debate and synthesis simply for a newcomer: {synthesis.answer}"
        explanation = sage.chat(sage_prompt)
        
        # 5. Rex Documents
        rex = get_agent("rex")
        print("Rex is documenting...")
        rex_prompt = f"Document this decision and the rationale: {json.dumps({'topic': self.topic, 'verdict': verdict.dict(), 'synthesis': synthesis.dict()})}"
        documentation = rex.chat(rex_prompt)
        
        result = {
            "topic": self.topic,
            "verdict": verdict.dict(),
            "synthesis": synthesis.dict(),
            "explanation": explanation.dict(),
            "documentation": documentation.dict()
        }
        
        # Update shared memory?
        # For now, let's just log it to Zero's episodic memory
        zero.memory.add_episodic({"type": "debate_result", "data": result})
        
        print("--- DEBATE COMPLETE ---")
        return result

if __name__ == "__main__":
    import datetime
    day = datetime.datetime.now().strftime("%A").lower()
    session = DebateSession(day)
    session.run_debate()
