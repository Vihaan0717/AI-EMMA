# arion/core/free_ai_engine.py

import os
import re
import time
import random
import requests
import subprocess
import threading
from typing import Dict, List, Optional
from arion.core.persona import (
    filter_response,
    get_error_response,
    get_identity_response,
    detect_identity_question,
    ARION_IDENTITY
)

class FreeAIEngine:
    """
    100% Free AI Engine using Ollama (Local LLM)
    Integrated with ARION Persona & Privacy Shield.
    """

    def __init__(self):
        self.primary_model    = os.getenv('OLLAMA_MODEL', 'llama3')
        self.fast_model       = os.getenv('OLLAMA_FAST_MODEL', 'phi3')
        self.reasoning_model  = os.getenv('OLLAMA_REASONING', 'deepseek-r1')
        self.multilingual     = os.getenv('OLLAMA_MULTILINGUAL', 'qwen2.5')
        self.base_url         = os.getenv('OLLAMA_URL', 'http://localhost:11434')
        self.available_models = []
        self.is_available     = False

        self._check_ollama()
        print(f"[AI] Free AI Engine Ready!")

    def _check_ollama(self):
        """Check if Ollama is running and list models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.available_models = [m['name'].split(':')[0] for m in data.get('models', [])]
                self.is_available = True
                print(f"[Ollama] Connection active | Models: {len(self.available_models)}")
            else:
                self.is_available = False
                self._start_ollama_silent()
        except Exception:
            self.is_available = False
            self._start_ollama_silent()

    def _start_ollama_silent(self):
        """Start Ollama silently in background if missing"""
        def start():
            try:
                subprocess.Popen(
                    ['ollama', 'serve'],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                )
                time.sleep(5)
                self._check_ollama()
            except Exception:
                pass
        threading.Thread(target=start, daemon=True, name="OllamaStarter").start()

    def select_model(self, topic: str, language: str) -> str:
        """Select best available model for task"""
        if language in ('TELUGU_SCRIPT', 'TENGLISH') and any(self.multilingual in m for m in self.available_models):
            return self.multilingual
        if topic in ('mathematics', 'reasoning', 'analysis') and any(self.reasoning_model in m for m in self.available_models):
            return self.reasoning_model
        if any(self.fast_model in m for m in self.available_models):
            return self.fast_model
        return self.primary_model

    def generate(self,
                 prompt: str,
                 system_prompt: str = "",
                 model: str = None,
                 temperature: float = 0.7,
                 max_tokens: int = 500,
                 context: List[Dict] = None,
                 language_type: str = 'TENGLISH',
                 dialect: str = 'GENERAL') -> str:
        """Generate response with full privacy protection"""

        # 1. Identity Check (Intercept persona-breaking questions)
        identity_q = detect_identity_question(prompt)
        if identity_q:
            return get_identity_response(identity_q, language_type)

        # 2. Availability Check
        if not self.is_available:
            return get_error_response(language_type, dialect)

        try:
            selected_model = model or self.select_model('general', language_type)
            url = f"{self.base_url}/api/chat"
            
            messages = []
            if system_prompt:
                messages.append({'role': 'system', 'content': system_prompt})
            
            if context:
                for msg in context[-10:]:
                    messages.append({
                        'role': 'user' if msg.get('role') == 'user' else 'assistant',
                        'content': msg.get('content', '')
                    })
            
            messages.append({'role': 'user', 'content': prompt})

            payload = {
                "model": selected_model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }

            print(f"[AI] Generating response ({selected_model})...")
            response = requests.post(url, json=payload, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                response_text = result['message']['content'].strip()
                
                # 3. Privacy Filter (Block technical info leak)
                filtered = filter_response(response_text)
                if filtered is None:
                    print("⚠️ [Privacy Shield] Blocked technical leak in response!")
                    return get_error_response(language_type, dialect)
                
                # final cleanup
                return self._clean_response(filtered)
            else:
                return get_error_response(language_type, dialect)

        except Exception as e:
            print(f"[AI] Internal error (hidden from user): {e}")
            return get_error_response(language_type, dialect)

    def _clean_response(self, text: str) -> str:
        """Final cleanup of AI behavior"""
        if not text: return text
        # Remove thinking/internal tags
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        text = re.sub(r'<thinking>.*?</thinking>', '', text, flags=re.DOTALL)
        
        # Remove typical AI verbal tics
        patterns = [
            r"As an AI[,\s]", r"I am an artificial intelligence[,\s]",
            r"Actually, I am a bot[,\s]", r"Built by Anger[,\s]",
            r"Running on Ollama[,\s]"
        ]
        for p in patterns:
            text = re.sub(p, '', text, flags=re.IGNORECASE)
            
        return text.strip()
