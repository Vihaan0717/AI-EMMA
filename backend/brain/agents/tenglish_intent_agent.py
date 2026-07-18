import logging
from typing import Dict, Any, Optional
from core.ai_engine import AIEngine
from config.system_config import JarvisConfig

logger = logging.getLogger("Nexus.TenglishIntentAgent")

class TenglishIntentAgent:
    """
    Specialized Agent to handle Telugu/English (Tenglish) inputs.
    Translates to English internal representation and extracts intent.
    """
    def __init__(self, ai_engine: Optional[AIEngine] = None):
        self.ai = ai_engine or AIEngine()
        self.system_prompt = """
You are the NEXUS-X Linguistic Interface. Your job is to process 'Tenglish' (Telugu + English mixed) inputs from the user.

TASK:
1. Translate the input into clear, grammatical English.
2. Identify the USER INTENT (e.g., COMMAND, QUESTION, CHAT, FEEDBACK, FINANCE, PLANNING).
3. Extract KEY ENTITIES (names, dates, amounts, objects).
4. Identify the MOOD/TONE (Happy, Frustrated, Neutral, Urgent).

OUTPUT FORMAT (JSON ONLY):
{
  "original": "input text",
  "english_translation": "translated text",
  "intent": "primary_intent",
  "entities": { ... },
  "mood": "detected_mood",
  "is_task": true/false
}

Example 1:
Input: "Jarvis, repu podunne 7 am ki nannu lepu. Important test undi."
Output: {
  "original": "Jarvis, repu podunne 7 am ki nannu lepu. Important test undi.",
  "english_translation": "Jarvis, wake me up tomorrow morning at 7 am. I have an important test.",
  "intent": "COMMAND",
  "entities": {"time": "7 am", "date": "tomorrow", "event": "important test"},
  "mood": "Neutral/Focused",
  "is_task": true
}

Example 2:
Input: "Ee answer naaku nachaledu, inkosari cheppu logic thoti."
Output: {
  "original": "Ee answer naaku nachaledu, inkosari cheppu logic thoti.",
  "english_translation": "I didn't like this answer, tell me again with logic.",
  "intent": "FEEDBACK",
  "entities": {"action": "retry", "modifier": "with logic"},
  "mood": "Frustrated",
  "is_task": true
}
"""

    async def parse(self, text: str) -> Dict[str, Any]:
        """Parses the Tenglish text into a structured object."""
        logger.info(f"Parsing Tenglish input: {text}")
        
        try:
            response = await self.ai.generate(
                prompt=f"Input: \"{text}\"",
                system=self.system_prompt,
                temperature=0.1
            )
            
            import json
            import re
            
            # Strip markdown code blocks if LLM wraps in ```json ... ```
            clean = re.sub(r"```(?:json)?", "", response).strip()
            
            # Find the outermost JSON object
            start = clean.find("{")
            end = clean.rfind("}") + 1
            if start != -1 and end > start:
                try:
                    return json.loads(clean[start:end])
                except json.JSONDecodeError:
                    # Last resort: try to find any valid JSON object
                    for match in re.finditer(r'\{[^{}]*\}', clean):
                        try:
                            return json.loads(match.group())
                        except json.JSONDecodeError:
                            continue
            
            logger.warning("Failed to extract JSON from TenglishIntentAgent response.")
            return {"original": text, "error": "JSON parsing failed", "raw_response": response[:200]}
                
        except Exception as e:
            logger.error(f"TenglishIntentAgent error: {e}")
            return {"original": text, "error": str(e)}

if __name__ == "__main__":
    # Quick test
    import asyncio
    async def test():
        agent = TenglishIntentAgent()
        result = await agent.parse("Repu evening movie ki veldham, ticket book chey.")
        print(result)
    
    asyncio.run(test())
