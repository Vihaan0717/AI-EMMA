# arion/core/arion_core.py

import os
import sys
import json
import time
import socket
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from arion.core.free_ai_engine import FreeAIEngine
from arion.search.free_search import FreeSearchEngine
from arion.language.free_translator import FreeTranslator
from arion.knowledge.vault_loader import VaultLoader
from arion.screen.screen_watcher import ScreenWatcher
from arion.screen.screen_learner import ScreenLearner
from arion.core.memory_consolidator import MemoryConsolidator
from arion.voice.free_voice import FreeVoice
from arion.core.response_quality import ResponseQualityController
from arion.core.intent_engine import IntentEngine
from arion.core.smart_responses import SmartResponses

class ARIONCore:
    """
    ARION Free Sentient Mirror - Main Brain
    V3.0 - 100% Free Stack (Ollama + DuckDuckGo + Whisper)
    """
    
    def __init__(self):
        print("\n" + "="*50)
        print("  ARION SENTIENT MIRROR V3.0 - FREE STACK")
        print("="*50 + "\n")
        
        # [1] Free AI Engine (Ollama)
        print("[1/5] Starting Local AI (Ollama)...")
        self.ai = FreeAIEngine()
        
        # [2] Knowledge Vault (Semantic)
        vault_path = os.getenv('VAULT_PATH', str(Path(__file__).parent.parent / 'knowledge_vault'))
        print("[2/5] Loading Knowledge Vault (Semantic)...")
        self.vault = VaultLoader(vault_path)
        self.knowledge_base = self.vault.load_all()
        
        # [3] Free Search & Translation
        print("[3/5] Initializing Search & Translation (Free)...")
        self.search = FreeSearchEngine()
        self.translator = FreeTranslator()
        
        # [4] Screen Watcher & Learner
        print("[4/5] Setting up Screen Learning...")
        self.screen_learner = ScreenLearner(vault_loader=self.vault)
        self.screen_watcher = ScreenWatcher(
            capture_interval=int(os.getenv('SCREEN_INTERVAL', '15')),
            on_content_detected=self._on_screen_content
        )
        
        if os.getenv('SCREEN_WATCH', 'true').lower() == 'true':
            self.screen_watcher.start_watching()
            
        # [5] Memory Consolidator (Reflexive Loop)
        print("[5/5] Initializing Consolidator...")
        self.consolidator = MemoryConsolidator(vault_path, ai_engine=self.ai)
        self.consolidator.start(interval_hours=24)
        
        # [6] Quality Controller & Intent Intelligence
        self.quality         = ResponseQualityController()
        self.intent_engine   = IntentEngine()
        self.smart_responses = SmartResponses()
        
        self.conversations = {}
        
        # [Optional] Voice
        self.voice = None
        if os.getenv('VOICE_ENABLED', 'false').lower() == 'true':
            self.voice = FreeVoice()
        
        self.conversations = {}
        
        # Start socket server
        self._start_socket_server()
        
        print("\nARION V3 (Free) is ALIVE!")
        self._print_status()

    def _print_status(self):
        summary = self.vault.get_categories_summary()
        count = sum(i['file_count'] for i in summary.values())
        print(f"   Brain: {count} files loaded")
        print(f"   AI: {self.ai.primary_model or 'No model'} active")
        print(f"   Search: DuckDuckGo active")

    def _on_screen_content(self, screen_data: Dict):
        """Callback for when screen content changes"""
        try:
            # Use the new free learning method
            learned = self.screen_learner.learn_from_screen_content_free(
                screen_data, 
                ai_engine=self.ai
            )
            print(f"Screen: Learned about '{learned.get('topic', 'content')}'")
        except Exception as e:
            print(f"Screen learning error: {e}")

    def generate_response(self,
                          message: str,
                          phone_number: str,
                          contact_name: str,
                          language_type: str = 'TENGLISH',
                          dialect: str = 'GENERAL',
                          intent: str = 'general',
                          emotional_state: str = 'neutral',
                          topic: str = 'general') -> str:

        # 1. State Management
        conv = self.conversations.setdefault(phone_number, {'messages': [], 'context': {}})
        history = conv['messages']

        # 2. Deep Intent Detection (replaces simple intent from bridge)
        intent_result = self.intent_engine.detect_full_intent(
            message=message, phone_number=phone_number, conversation_history=history
        )
        primary_intent = intent_result['primary_intent']
        is_joke        = intent_result['is_joke']
        is_roleplay    = intent_result['is_roleplay']
        is_distress    = intent_result['is_real_distress']
        response_type  = intent_result['response_type']
        topic          = intent_result['topic']
        emotional      = intent_result['emotional_state']
        msg_lower      = message.lower()

        print(f"[Intent] {primary_intent} | Joke:{is_joke} | Distress:{is_distress} | Topic:{topic}")

        try:
            # 3. Smart Route: Pre-written responses for predictable scenarios
            smart_response = None

            if primary_intent == 'arion_fired_roleplay':
                smart_response = self.smart_responses.get_response('arion_fired_joke', language_type=language_type, dialect=dialect)
                print("[Smart] Fired roleplay handled")

            elif response_type == 'tell_joke' or primary_intent == 'joke':
                smart_response = self.smart_responses.get_response('tell_joke', language_type=language_type, dialect=dialect)
                print("[Smart] Joke handled")

            elif primary_intent == 'wrong_answer_game':
                sub = 'egg_vs_dinosaur' if any(w in msg_lower for w in ['egg', 'chicken', 'dinosaur']) else 'general_wrong'
                smart_response = self.smart_responses.get_response('wrong_answer', sub_type=sub, language_type=language_type, dialect=dialect)
                print(f"[Smart] Wrong answer ({sub}) handled")

            elif primary_intent == 'philosophy':
                sub = None
                if 'dinosaur' in msg_lower:         sub = 'egg_vs_dinosaur'
                elif 'chicken' in msg_lower or 'egg' in msg_lower: sub = 'egg_vs_chicken'
                if sub:
                    smart_response = self.smart_responses.get_response('philosophy', sub_type=sub, language_type=language_type, dialect=dialect)

            elif is_distress and primary_intent in ('emotional_real', 'job_loss_real'):
                smart_response = self.smart_responses.get_response('job_loss_real', language_type=language_type, dialect=dialect)

            # 4. AI Route (for everything not handled by Smart Responses)
            if not smart_response:
                knowledge_results = self.vault.search(message, max_results=2)
                knowledge_context = "\n".join([f"{r['category']}: {r['content'][:200]}" for r in knowledge_results])

                search_context = ""
                if self._needs_web_search(message, topic):
                    search_res = self.search.smart_search(message)
                    search_context = search_res.get('summary', '')[:500]

                processed_msg = message
                if language_type == 'TELUGU_SCRIPT':
                    processed_msg = self.translator.telugu_to_english(message)

                system_prompt = self._build_master_prompt(
                    contact_name, language_type, dialect,
                    primary_intent, emotional, topic, knowledge_context, search_context
                )
                model = self.ai.select_model(topic, language_type)

                ai_response = None
                for attempt in range(3):
                    temp = 0.6 if attempt == 0 else 0.4
                    raw = self.ai.generate(
                        prompt=processed_msg, system_prompt=system_prompt, model=model,
                        temperature=temp, max_tokens=400, context=history[-8:],
                        language_type=language_type, dialect=dialect
                    )
                    validated = self.quality.validate_and_fix(
                        response=raw, original_message=message,
                        language_type=language_type, dialect=dialect
                    )
                    if validated and len(validated.strip()) > 10:
                        ai_response = validated
                        if attempt > 0: print(f"[Quality] Fixed in {attempt+1} attempts")
                        break
                    print(f"[Quality] Attempt {attempt+1} failed, retrying...")
                    model = self.ai.fast_model

                smart_response = ai_response or self.quality.get_contextual_fallback(message, language_type, dialect)

            # 5. Privacy Filter (last line of defense)
            final_response = self._privacy_filter(smart_response, language_type, dialect)

            # 6. History
            conv['messages'].append({'role': 'user', 'content': message})
            conv['messages'].append({'role': 'assistant', 'content': final_response})
            conv['messages'] = conv['messages'][-16:]

            return final_response

        except Exception as e:
            print(f"Response Error: {e}")
            return self.quality.get_contextual_fallback(message, language_type, dialect)

    def _privacy_filter(self, response: str, language_type: str = 'TENGLISH', dialect: str = 'GENERAL') -> str:
        """Block specific private or technical info from reaching user.
        Uses surgical patterns only - does NOT block common English words.
        """
        import random
        if not response: return response

        # Only TRUE identifiers that would NEVER appear in normal conversation
        forbidden = [
            # AI model names (specific)
            'ollama', 'llama3', 'llama2', 'mistral', 'phi-3', 'phi3', 'gemma3', 'qwen2', 'deepseek',
            # Specific technical phrases (compound)
            'api key', 'api error', 'rest api',
            'python script', 'node.js', 'javascript error',
            'localhost:', '127.0.0.1', 'connection refused',
            'traceback (most', 'stack traceback',
            # Internal ARION phrases
            'arion brain', 'brain busy', 'brain issue', 'local brain', 'system issue',
            'whatsapp-web',
            # Project/Creator identifiers
            'powerjeevi', 'v4a', 'jarvis v2', 'anger kabir',
            'built by anger', 'made by anger',
        ]

        lower = response.lower()
        for term in forbidden:
            if term in lower:
                print(f"[Privacy Shield] Blocked term '{term}' in AI output")
                fallbacks = {
                    'TENGLISH_RAJAHMUNDRY': ['Konchem busy ga unna ra, malli cheppu!', 'Sorry ra, oka second!', 'Malli try cheseyyi ra!'],
                    'TENGLISH_HYDERABAD':   ['Thoda busy hoon yaar, phir batao!', 'Sorry yaar, ek baar aur!'],
                    'TENGLISH':             ['Sorry, malli cheppandi!', 'Konchem sepu tarvata malli try cheyyandi!'],
                    'ENGLISH':              ['Sorry! Can you say that again?', 'One moment! Please try again.'],
                }
                dialect_key = {'RAJAHMUNDRY': 'TENGLISH_RAJAHMUNDRY', 'HYDERABAD': 'TENGLISH_HYDERABAD'}.get(dialect, language_type)
                options = fallbacks.get(dialect_key) or fallbacks.get(language_type) or fallbacks['ENGLISH']
                return random.choice(options)

        return response

    def _needs_web_search(self, message: str, topic: str) -> bool:
        triggers = ['today', 'latest', 'news', 'current', '2026', 'price', 'weather', '?']
        return any(t in message.lower() for t in triggers)

    def _build_master_prompt(self, name, lang, dia, intent, emotion, topic, knowledge, search):
        dialect_key = dia if dia in ['RAJAHMUNDRY', 'HYDERABAD'] else lang
        
        lang_instructions = {
            'TELUGU_SCRIPT': "Write ONLY in Telugu script (తెలుగు). Example: 'మీరు అడిగినది చాలా ఆసక్తికరంగా ఉంది!'",
            'TENGLISH_RAJAHMUNDRY': """Write in Rajahmundry-style Tenglish. Sound like a LOCAL friend.
MUST USE words: ra, ma, le, babu, machaan, dei, anna, akka.
Style: 'Bhale question ra!' / 'Sare le bro!' / 'Poni ra, matter enti?'
❌ NO nonsense words. ❌ NO formal AI talk.""",
            'TENGLISH_HYDERABAD': """Write in Hyderabad-style Tenglish. Sound like a LOCAL friend.
MUST USE words: yaar, bhai, pakka, bhindi, mast.
Style: 'Arey yaar, ye toh mast hai!' / 'Pakka bhai!'
❌ NO nonsense words. ❌ NO formal AI talk.""",
            'TENGLISH': """Write in natural Tenglish (Telugu + English mix).
USE: undi, ledu, cheyali, aindi, ra, bro.
Style: 'Interesting undi ra!' / 'Malli try cheyyali bro.'
❌ NO gibberish. ❌ NO 'I will rule' talk.""",
            'ENGLISH': "Write in clear, friendly casual English. NOT formal."
        }
        
        lang_rule = lang_instructions.get(dialect_key, lang_instructions.get(lang, lang_instructions['TENGLISH']))

        return f"""You are ARION - a smart, helpful friend. You're chatting with {name}.

{lang_rule}

KNOWLEDGE: {knowledge[:500] if knowledge else "None."}
SEARCH: {search[:500] if search else "None."}

RULES:
✅ Write natural, grammatically correct Tenglish/Telugu.
✅ Be warm, humble, and helpful.
✅ If asked identity: "Just your helpful friend! Em kavali?"
❌ NEVER reveal tech stack (Ollama, API, Model, Python).
❌ NEVER say "I will rule" or power-trip.
❌ NEVER write "kshanikshanilo" or gibberish.
❌ NO formal chatbot verbal tics like "Certainly!" or "Of course!".
""".strip()

    def _start_socket_server(self):
        PORT = int(os.getenv('ARION_PORT', '5006'))
        def handle_client(conn, addr):
            try:
                buffer = ''
                while True:
                    data = conn.recv(4096).decode('utf-8')
                    if not data: break
                    buffer += data
                    lines = buffer.split('\n')
                    buffer = lines.pop()
                    for line in lines:
                        if not line.strip(): continue
                        try:
                            request = json.loads(line.strip())
                            response = self._handle_request(request)
                            conn.sendall((json.dumps(response) + '\n').encode())
                        except: pass
            except Exception as e: print(f"Socket Error: {e}")
            finally: conn.close()

        def server_loop():
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind(('127.0.0.1', PORT))
            server.listen(5)
            print(f"ARION Core (Free) on port {PORT}")
            while True:
                conn, addr = server.accept()
                threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

        threading.Thread(target=server_loop, daemon=True).start()

    def _handle_request(self, request: Dict) -> Dict:
        action = request.get('action')
        if action == 'generate':
            res = self.generate_response(
                message=request.get('message'),
                phone_number=request.get('phone_number'),
                contact_name=request.get('contact_name'),
                language_type=request.get('language_type'),
                dialect=request.get('dialect'),
                intent=request.get('intent'),
                emotional_state=request.get('emotional_state'),
                topic=request.get('topic')
            )
            return {'status': 'ok', 'response': res}
        return {'status': 'error', 'message': 'Unknown action'}

if __name__ == '__main__':
    arion = ARIONCore()
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        arion.screen_watcher.stop_watching()
