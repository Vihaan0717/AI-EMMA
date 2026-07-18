import json
import re
import asyncio
from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from config.system_config import JarvisConfig
from core.logger import get_logger

logger = get_logger("SentientMirror")

class SentientMirrorPipeline:
    """
    3-Step Linguistic Mirror Pipeline:
    Step A: The Filter (Deconstruction)
    Step B: The Core Answer
    Step C: The Reconstruction (Mirroring)
    """
    
    def __init__(self):
        # Gemini 2.0 Flash Lite is used for fast, high-quality reasoning
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite", 
            google_api_key=JarvisConfig.GEMINI_API_KEY,
            temperature=0.7
        )
        logger.info("Sentient Mirror Pipeline initialized with Gemini 2.0 Flash Lite.")

    async def analyze_input(self, user_input: str) -> dict:
        """Step A: Extract Intent, Emotion, Slang, and Structure."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Deconstruct the following user input into a JSON object with:
            - intent: (e.g., Question, Command, Small Talk)
            - emotion: (Happy, Stressed, Joking, Neutral)
            - slang_dict: List of specific slang words, religious greetings, or local terms used.
            - structure: (Short/Aggressive, Long/Poetic, Formal, Casual)
            Respond ONLY with the JSON object."""),
            ("user", "{input}")
        ])
        chain = prompt | self.llm
        try:
            response = await chain.ainvoke({"input": user_input})
            # Clean JSON string if needed
            content = re.sub(r'```json\n?|\n?```', '', response.content).strip()
            return json.loads(content)
        except Exception as e:
            logger.error(f"Filter analysis failed: {e}")
            return {"intent": "General", "emotion": "Neutral", "slang_dict": [], "structure": "Casual"}

    async def generate_core_facts(self, user_input: str) -> str:
        """Step B: Generate the factual answer (Core Brain)."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are the JARVIS Core. Generate a factual, clear, and accurate answer to the user's request. Do not add any persona or fluff yet."),
            ("user", "{input}")
        ])
        chain = prompt | self.llm
        response = await chain.ainvoke({"input": user_input})
        return response.content

    async def reconstruct_mirror(self, facts: str, analysis: dict) -> str:
        """Step C: Rewrite with extracted Slang, Structure, and Emotion."""
        # Inject 20% Humor/Sarcasm and align with religious greetings
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Rewrite the provided FACTUAL ANSWER to perfectly mirror the Boss's soul.
            
            Attributes to Mirror:
            - Emotion: {emotion}
            - Structure: {structure}
            - Slang/Terms to include: {slang_list}
            
            Rules:
            1. If slang_list includes religious greetings (Namaste, Salam, etc.), respond with a culturally aligned ethical closing.
            2. Inject 20% Humor or Sarcasm based on the {emotion}.
            3. NEVER say 'As an AI'. You are JARVIS-X.
            4. If the structure is 'Short/Aggressive', be blunt. If 'Long/Poetic', be flowery.
            
            FACTUAL ANSWER:
            {facts}"""),
            ("user", "Mirror this for me.")
        ])
        chain = prompt | self.llm
        payload = {
            "emotion": analysis.get("emotion"),
            "structure": analysis.get("structure"),
            "slang_list": ", ".join(analysis.get("slang_dict", [])),
            "facts": facts
        }
        response = await chain.ainvoke(payload)
        return response.content

    async def process(self, user_input: str) -> str:
        """Full Pipeline Execution (Parallel Optimization)."""
        logger.info(f"Mirroring Soul for: '{user_input}'")
        
        # Trigger Step A (Analysis) and Step B (Facts) in parallel
        # This cuts initial latency by nearly 50%
        analysis_task = self.analyze_input(user_input)
        facts_task = self.generate_core_facts(user_input)
        
        analysis, facts = await asyncio.gather(analysis_task, facts_task)
        
        logger.debug(f"Analysis complete. Parallel tasks synced. facts length: {len(facts)}")
        
        # Step C (Reconstruction) depends on both, so it waits
        mirrored_reply = await self.reconstruct_mirror(facts, analysis)
        
        return mirrored_reply

# Global instance for easy import
mirror_engine = SentientMirrorPipeline()

if __name__ == "__main__":
    # Test stub
    import asyncio
    async def test():
        test_input = "Namaste Jarvis, where are my car keys? I'm joking but seriously find them."
        res = await mirror_engine.process(test_input)
        print(f"MIRRORED RESPONSE:\n{res}")
    asyncio.run(test())
