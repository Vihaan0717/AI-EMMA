import asyncio
import os
import sys
import logging
import random
from pathlib import Path

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from backend.core.ai_engine import AIEngine
from backend.search.web_brain import WebBrain
from backend.config.system_config import JarvisConfig
from backend.core.fleet.local_db import fleet_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger("scholar_learning_loop")

# Standard syllabus subjects for study if none provided
TOPICS = [
    # Biology
    "Cellular Respiration and ATP production",
    "DNA replication mechanisms and transcription enzymes",
    "CRISPR-Cas9 gene editing and ethics",
    
    # Physics
    "Quantum entanglement and superposition",
    "General Relativity and gravitational lensing",
    "Thermodynamics laws and entropy",
    
    # Chemistry
    "Covalent vs Ionic bonding and molecular geometry",
    "Catalysis and activation energy barriers",
    "Electrochemistry and redox cell potentials",
    
    # Movies / Stories
    "The hero's journey narrative archetype in storytelling",
    "Orson Welles and the cinematography of Citizen Kane",
    "The evolution of CGI in cinema",
    
    # Music
    "The Circle of Fifths and chord progressions",
    "Pentatonic scale modes and jazz improvisation",
    "ABC notation format and digital transcription"
]

class ScholarLearningLoop:
    def __init__(self):
        self.ai = AIEngine()
        self.web = WebBrain()
        
    async def initialize(self):
        await self.ai.initialize()
        
    async def run_study_cycle(self, topic: str = None) -> str:
        """Runs a complete self-contained research and learning cycle."""
        if not topic:
            topic = random.choice(TOPICS)
            
        logger.info(f"📚 Starting study cycle on: '{topic}'")
        
        # 1. Search & Learn
        research_raw = await self.web.learn(topic)
        
        # Format research material for LLM
        research_context = ""
        if research_raw.get('source') == 'wikipedia':
            research_context = research_raw.get('content', '')
        elif research_raw.get('source') == 'youtube':
            videos = research_raw.get('videos', [])
            research_context = "\n\n".join([f"Video: {v['title']}\nURL: {v['url']}\nTranscript/Description: {v['transcript']}" for v in videos])
        elif research_raw.get('source') == 'educational_sites':
            articles = research_raw.get('articles', [])
            research_context = "\n\n".join([f"Article: {a['title']}\nURL: {a['url']}\nContent: {a['content']}" for a in articles])
        elif 'documents' in research_raw:
            research_context = "\n\n".join([doc.get('text', '') for doc in research_raw['documents']])
        elif 'papers' in research_raw:
            papers = research_raw.get('papers', [])
            research_context = "\n\n".join([f"Paper: {p['title']}\nAuthors: {', '.join(p['authors'])}\nSummary: {p['summary']}" for p in papers])
            
        if not research_context:
            research_context = f"Perform general study on {topic}."
            
        # 2. Synthesize with Cosmos Agent Persona
        system_prompt = (
            "You are COSMOS, the Polymath and Academic Scholar of NEXUS-X.\n"
            "Create a comprehensive, highly informative study guide / research note based on the research content.\n"
            "Format the output as a clean Markdown file with YAML frontmatter tags.\n"
            "Make sure to cover:\n"
            "1. What it is (Core Definition)\n"
            "2. The true underlying meaning / deep concept explanation\n"
            "3. Practical application: where, how, and why it is used in the real world\n"
            "4. Cross-discipline connections (e.g. connecting biology to chemistry, or music to math/physics)\n"
            "Keep the tone engaging, precise, and educational."
        )
        
        prompt = (
            f"Topic: {topic}\n\n"
            f"Research Material:\n{research_context[:10000]}\n\n"
            f"Synthesize the guide now:"
        )
        
        logger.info("Generating study guide via AIEngine...")
        study_guide = await self.ai.generate(prompt=prompt, system=system_prompt, temperature=0.3)
        
        # 3. Save to Knowledge Vault
        safe_filename = "".join([c if c.isalnum() or c in (' ', '_', '-') else '' for c in topic]).strip().replace(' ', '_')
        vault_dir = Path("knowledge_vault/Scholar")
        vault_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = vault_dir / f"{safe_filename}.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(study_guide)
            
        logger.info(f"✅ Study guide saved successfully to: {output_file}")
        
        # 4. Log to Fleet Database (Share knowledge / update agent updates)
        try:
            fleet_db.add_correction_note("cosmos", f"Self-Learning: {topic}", f"Successfully studied and wrote guide to {output_file}")
        except Exception as e:
            logger.warning(f"Failed to log to database: {e}")
            
        return str(output_file)

async def main():
    loop = ScholarLearningLoop()
    await loop.initialize()
    
    # Check if a custom topic was passed via command line args
    custom_topic = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
    
    filepath = await loop.run_study_cycle(custom_topic)
    print(f"\n[SUCCESS] Learning cycle completed. Output: {filepath}")
    
    await loop.web.close()
    await loop.ai.close()

if __name__ == "__main__":
    asyncio.run(main())
