import os
from groq import Groq
from dotenv import load_dotenv
import logging
import json
from datetime import datetime

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    logging.warning("GROQ_API_KEY is missing! Refiner will not work.")

client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

def refine_human_context(raw_text: str) -> dict:
    """
    Uses Groq API to analyze scraped text and extract persona updates, humor, and conversational skills.
    """
    if not client:
        return None

    prompt = f"""
    You are an AI Persona Engineer. I will provide you with raw text scraped from human conversational forums (e.g., CasualConversation, Showerthoughts).
    Your goal is to analyze this text and extract insights that an AI agent can use to upgrade its persona, learn human humor, and understand day-to-day feelings.

    RAW TEXT:
    {raw_text}

    Analyze the text and return a JSON object with the following structure exactly:
    {{
        "theme": "The general theme of the conversations",
        "human_insight": "A deep psychological or social insight learned from this text",
        "humor_or_quirk": "An example of humor, a quirk, or casual slang observed",
        "how_agent_can_adapt": "One specific way the AI agent should update its persona or response style based on this data"
    }}

    Return ONLY the valid JSON, no markdown formatting.
    """

    try:
        logging.info("Sending text to Groq API for refinement...")
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful AI that strictly outputs JSON."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.7,
            max_tokens=500
        )
        
        response_text = chat_completion.choices[0].message.content.strip()
        # Clean up if the model wrapped it in markdown
        if response_text.startswith("```json"):
            response_text = response_text[7:-3].strip()
            
        data = json.loads(response_text)
        data['timestamp'] = datetime.utcnow()
        return data

    except Exception as e:
        logging.error(f"Groq API Error: {e}")
        return None
