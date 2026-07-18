# arion/screen/screen_learner.py

import json
import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

class ScreenLearner:
    """
    ARION analyzes screen content
    Supports legacy GPT-4 Vision and new FREE Ollama-based learning.
    """
    
    def __init__(self, vault_loader=None, memory=None):
        self.vault_loader = vault_loader
        self.memory = memory
        self.learned_from_screen = []
        self.learning_journal_path = Path('arion/knowledge_vault/Agent_Self/Learning_Journal')
        self.learning_journal_path.mkdir(parents=True, exist_ok=True)
        
        # Lazy load OpenAI only if needed
        self._openai_client = None
        
        print("Screen Learner initialized")

    @property
    def openai_client(self):
        if self._openai_client is None:
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key and not api_key.startswith('sk-proj-xxxx'):
                from openai import OpenAI
                self._openai_client = OpenAI(api_key=api_key)
        return self._openai_client

    def learn_from_screen_content_free(self, screen_data: Dict, ai_engine) -> Dict:
        """
        Process screen content using the FREE AI Engine (Ollama)
        """
        text = screen_data.get('text', '')
        content_type = screen_data.get('content_type', 'general')
        timestamp = screen_data.get('timestamp', datetime.now().isoformat())
        
        if len(text.strip()) < 50:
            return {'status': 'skipped', 'reason': 'content too short'}
        
        # Use Ollama to analyze the text content
        prompt = f"""
Analyze this screen content and extract knowledge.
Content Type: {content_type}
Text: {text[:1500]}

Return JSON:
{{
  "topic": "main topic",
  "key_concepts": ["concept1", "concept2"],
  "facts_learned": ["fact1", "fact2"],
  "summary": "comprehensive summary",
  "domain": "psychology/math/etc"
}}
"""
        try:
            analysis_raw = ai_engine.generate(prompt, system_prompt="You are ARION's visual learning system.", model=ai_engine.fast_model)
            
            # Simple JSON extraction
            json_match = re.search(r'\{.*\}', analysis_raw, re.DOTALL)
            analysis = json.loads(json_match.group()) if json_match else {}
        except Exception:
            analysis = {
                'topic': content_type,
                'summary': text[:200],
                'domain': 'general',
                'key_concepts': [],
                'facts_learned': []
            }

        knowledge_entry = {
            'source': 'screen_capture',
            'timestamp': timestamp,
            'content_type': content_type,
            'raw_text': text[:1000],
            'analysis': analysis,
            'topic': analysis.get('topic', content_type),
            'domain': analysis.get('domain', 'general'),
            'summary': analysis.get('summary', text[:300])
        }
        
        self.learned_from_screen.append(knowledge_entry)
        self._save_to_journal(knowledge_entry)
        
        # Update vault loader if available
        if self.vault_loader:
            file_tid = f"screen_{timestamp.replace(':', '-')}"
            self.vault_loader.knowledge_base[file_tid] = {
                'id': file_tid,
                'title': f"Screen: {knowledge_entry['topic']}",
                'path': f"screen_captures/{file_tid}",
                'category': knowledge_entry['domain'],
                'content': knowledge_entry['summary'],
                'metadata': {'source': 'screen'},
                'word_count': len(text.split()),
                'loaded_at': timestamp,
                'summary': knowledge_entry['summary'][:200]
            }
            
        return knowledge_entry

    def _save_to_journal(self, entry: Dict):
        """Save learned content to Learning Journal"""
        try:
            date_str = datetime.now().strftime('%Y-%m-%d')
            journal_file = self.learning_journal_path / f"{date_str}_screen_learning.md"
            
            content = f"""
## {datetime.now().strftime('%H:%M:%S')} - Screen Learning
**Topic:** {entry.get('topic', 'Unknown')}
**Domain:** {entry.get('domain', 'Unknown')}
**Summary:** {entry.get('summary', 'No summary')}
---
"""
            with open(journal_file, 'a', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            print(f"Journal save error: {e}")

    def get_recent_learnings(self, limit: int = 10) -> List[Dict]:
        return self.learned_from_screen[-limit:]
