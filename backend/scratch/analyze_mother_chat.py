import zipfile
import PyPDF2
import json
import os
import re
import asyncio
from pathlib import Path

# Explicitly load .env first so keys are available
from dotenv import load_dotenv
load_dotenv()

from core.ai_engine import AIEngine

async def analyze_chat():
    print("Starting Mother Chat analysis...")
    zip_path = Path("WhatsApp Chat with Amma.zip")
    if not zip_path.exists():
        print(f"Error: {zip_path} not found.")
        return

    # Extract text from the PDF in the zip
    full_text = ""
    with zipfile.ZipFile(zip_path) as z:
        with z.open("WhatsApp Chat with Amma.pdf") as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            print(f"Total PDF pages: {len(reader.pages)}")
            
            # Sample pages from the beginning, middle, and end to avoid token overflow
            total_pages = len(reader.pages)
            pages_to_read = []
            if total_pages <= 20:
                pages_to_read = list(range(total_pages))
            else:
                # Samples
                pages_to_read = list(range(0, 10)) + list(range(total_pages // 2 - 5, total_pages // 2 + 5)) + list(range(total_pages - 10, total_pages))
            
            for page_num in pages_to_read:
                page = reader.pages[page_num]
                text = page.extract_text()
                if text:
                    full_text += text + "\n"

    print(f"Extracted {len(full_text)} characters of text samples.")

    # Call AI Engine to analyze style
    os.environ["USE_CLOUD_PRIMARY"] = "True"  # Force Gemini for deep reasoning
    engine = AIEngine()
    await engine.initialize()

    prompt = f"""
    Analyze the following chat transcript between a mother ("Amma") and her child.
    Identify the mother's texting style, vocabulary, tone, phrases, and typical behavior.
    Pay attention to:
    1. Language: Does she use Tenglish, Telugu script, or English? (Look for Telugu words like "kanna", "tinnava", "ekkadunnav", "babu", etc.)
    2. Tone: How does she show affection? How does she show concern? How does she scold when she is angry or worried?
    3. Specific phrases or signatures she uses frequently.
    4. Typical responses related to food, health, and waking up/sleeping timings.
    
    CHAT SAMPLES:
    \"\"\"
    {full_text[:6000]}
    \"\"\"

    Output a JSON profile of the mother persona configuration containing:
    {{
       "language": "tenglish" or "telugu" or "english",
       "affectionate_terms": ["list of terms like kanna, babu"],
       "scolding_phrases": ["list of typical scolding phrases in her style"],
       "concern_phrases": ["typical questions showing concern about health, food, timings"],
       "daily_checks": ["typical messages sent during morning or meal times"],
       "tone_instructions": "guidance on how the AI should react and talk exactly like her"
    }}
    Return only valid JSON inside code block.
    """

    response = await engine.generate(prompt)
    await engine.close()

    try:
        # Extract JSON
        json_match = re.search(r"```json\s*(.*?)\s*```", response, re.DOTALL)
        if json_match:
            json_data = json.loads(json_match.group(1))
        else:
            json_data = json.loads(response.strip())
        
        # Save config
        config_dir = Path("config")
        config_dir.mkdir(exist_ok=True)
        config_path = config_dir / "mother_persona.json"
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=4, ensure_ascii=False)
        print(f"Successfully compiled and saved mother persona to {config_path}")
    except Exception as e:
        print(f"Failed to parse AI response as JSON: {e}")
        print("Raw response was:")
        print(response)

if __name__ == "__main__":
    asyncio.run(analyze_chat())
