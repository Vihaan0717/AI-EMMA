import aiohttp
import json

class AnalystAgent:
    """
    Critic/Analyst Agent.
    Uses a local LLM via Ollama to read markdown text, extract insights, 
    categorize domains, and evaluate credibility.
    """
    def __init__(self, model_name="llama3.1", ollama_url="http://localhost:11434/api/generate"):
        self.model_name = model_name
        self.ollama_url = ollama_url

    async def analyze(self, markdown_text: str) -> dict:
        """
        Analyzes the text and returns a structured JSON containing insights.
        """
        prompt = f"""
        Analyze the following text. Extract core insights, categorize the domain, 
        and evaluate information credibility. Return the output as valid JSON with keys: 
        'insights' (list of strings), 'domain' (string), 'credibility_score' (1-10).
        
        Text:
        {markdown_text[:4000]} # Truncated for context limit
        """
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.ollama_url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    try:
                        result = json.loads(data.get("response", "{}"))
                        return result
                    except json.JSONDecodeError:
                        return {"error": "Failed to parse JSON", "raw": data.get("response")}
                else:
                    raise Exception(f"Ollama request failed: {response.status}")
