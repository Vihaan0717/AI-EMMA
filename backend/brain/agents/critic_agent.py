import os
import aiohttp
import datetime

class CriticAgent:
    """
    Evaluates failures from the simulation loop and generates "Lessons Learned" markdown files.
    """
    def __init__(self, model_name="llama3.1", ollama_url="http://localhost:11434/api/generate", lessons_dir="./knowledge_vault/lessons_learned"):
        self.model_name = model_name
        self.ollama_url = ollama_url
        self.lessons_dir = lessons_dir
        os.makedirs(self.lessons_dir, exist_ok=True)

    async def reflect_on_failure(self, task_description: str, error_log: str) -> str:
        """
        Analyzes the failure and creates a lesson learned.
        """
        prompt = f"""
        You are an AI Critic. The web agent failed a task.
        Task: {task_description}
        Error/Log: {error_log}
        
        Analyze why it failed and write a brief, actionable "Lesson Learned" that can be injected 
        into the agent's system prompt tomorrow to prevent this failure. Keep it concise.
        """
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.ollama_url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    lesson = data.get("response", "").strip()
                    
                    # Save lesson to file
                    date_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = os.path.join(self.lessons_dir, f"lesson_{date_str}.md")
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(f"# Lesson Learned: {date_str}\n\n**Task:** {task_description}\n\n**Lesson:**\n{lesson}\n")
                        
                    return filename
                else:
                    raise Exception(f"Ollama request failed: {response.status}")
