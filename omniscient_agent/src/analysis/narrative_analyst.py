import os
import requests
import json
import logging
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NarrativeAnalyst:
    """Uses local LLM (Ollama) to perform deep philosophical and narrative analysis."""

    def __init__(self):
        self.base_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "llama3.1:latest")
        logger.info(f"Initialized NarrativeAnalyst with local Ollama model: {self.model} at {self.base_url}")

    def analyze_scene(self, transcript_segment: str, visual_context: str) -> str:
        prompt = f"Analyze the following scene. Transcript: {transcript_segment} Visual Context: {visual_context}. Provide a concise analysis focusing on Emotional Weight and Philosophical Value."
        
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            response = requests.post(f"{self.base_url}/api/generate", json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "No response returned from Ollama.")
        except Exception as e:
            logger.error(f"Failed to generate analysis via Ollama: {e}")
            return "Analysis failed."

    def extract_powerful_dialogues(self, transcript: str) -> List[Dict[str, str]]:
        """
        Extracts only the most powerful, memorable dialogues from a full transcript.
        Returns a list of dictionaries with 'speaker' and 'text'.
        """
        prompt = f"""
        Review the following transcript and extract the most powerful, philosophically profound, or emotionally resonant dialogues.
        Format the output as a clean list of quotes.
        
        Transcript:
        {transcript}
        """
        try:
            response = self.model.generate_content(prompt)
            # In a full implementation, we'd use Structured Outputs (JSON) to parse this reliably.
            # Returning raw text for now as a placeholder.
            return [{"quote": response.text}]
        except Exception as e:
            logger.error(f"Failed to extract dialogues: {e}")
            return []

if __name__ == "__main__":
    analyst = NarrativeAnalyst()
    print("NarrativeAnalyst initialized. Requires GEMINI_API_KEY to function.")
