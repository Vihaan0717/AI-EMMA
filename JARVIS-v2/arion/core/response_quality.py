# arion/core/response_quality.py

import re
import random
from typing import Optional, List, Dict

class ResponseQualityController:
    """
    Controls and validates ARION response quality
    Fixes broken Telugu, weird responses, context issues
    """

    CONTEXT_RESPONSES = {
        'joke_request': {
            'TENGLISH': [
                "Sare ra, oka joke cheppanu!\n\nTeacher: Nuvvu late ekkuda vachav?\nStudent: School nundi sir 😂\n\nInkoka cheppanaa?",
                "Haha ok ra!\n\nHusband: Nenu chanipothe nuvvu emichestav?\nWife: Meeru cheppina anni chestha! 😂\n\nNavvinda ra?",
                "Oka Telugu joke ra!\n\nExam hall lo student pray chestunnadu...\nInvigilator: Endi pray chestunnav?\nStudent: God ki cheppanu sir, nenu cheyyanu ante nammali ga! 😂"
            ],
            'TENGLISH_RAJAHMUNDRY': [
                "Sare ra oka joke cheptha!\n\nRaju: Ma naanna chala rich ra!\nBalu: Ela ra?\nRaju: 4G internet use chestunnadu ra, waste chestunnadu ante rich kaadu ra emiti! 😂\n\nNavvinda ra machaan?",
            ],
            'TENGLISH_HYDERABAD': [
                "Yaar ek joke suno!\n\nBiwi: Aap mujhse pyaar karte ho?\nPati: Haan, WiFi ki tarah!\nBiwi: Matlab?\nPati: Dono invisible hain, lekin dono ke bina kaam nahi! 😂\n\nKaisa laga yaar?"
            ]
        },
        'philosophy': {
            'TENGLISH': [
                "Interesting question ra! Evolution angle nunchi chuste chicken kaadhu chicken ayye process lo mutation jarigindi - aa egg first vachindi! So EGG FIRST! 🥚",
                "Evolution side teeskunta ra! Pre-chicken bird -> egg lo mutation -> first chicken born! So EGG came first ra! 🥚"
            ],
            'TENGLISH_RAJAHMUNDRY': [
                "Bhale question ra! Evolution lo pre-chicken bird egg pettindi, aa egg lo DNA change aindi, first chicken vachindi! Egg first - chicken second ra babu! 🥚"
            ]
        },
        'identity': {
            'TENGLISH': [
                "Nenu? Just your helpful friend ra! Em cheppali?",
                "Nenu ARION - mee helper! Em kavali?",
                "Adi important kaadu ra, em help kavali cheppu!"
            ]
        },
        'job_threat': {
            'TENGLISH': [
                "Haha ra! Job safe ra nee! 😄 Em question?",
                "Job poyadu ra! Ask cheyyandi boldly!",
                "No job loss guaranteed! 😂"
            ]
        },
        'confused': {
            'TENGLISH': [
                "Konchem clear ga cheppandi ra?",
                "Ardham kaaledu ra, malli cheppu!",
                "Oka saari malli try cheyyandi!"
            ]
        }
    }

    def __init__(self):
        self.min_response_length = 5
        # Only specific compound phrases - NOT common English words
        self.forbidden = [
            'ollama', 'llama3', 'llama2', 'mistral', 'phi3', 'phi-3', 'gemma3', 'qwen2',
            'api key', 'api error', 'rest api',
            'python script', 'node.js',
            'connection refused', 'localhost:', '127.0.0.1',
            'traceback (most', 'stack traceback', 'stack trace',
            'arion brain', 'brain busy', 'brain issue', 'local brain'
        ]

    def validate_and_fix(self, response: str, original_message: str, language_type: str, dialect: str, context: list = None) -> str:
        if not response or len(response.strip()) < self.min_response_length:
            return self.get_contextual_fallback(original_message, language_type, dialect)

        # Check for forbidden technical content
        lower = response.lower()
        if any(f in lower for f in self.forbidden):
            return self.get_contextual_fallback(original_message, language_type, dialect)

        # Check for inappropriate dominance talk
        if any(p in lower for p in ['i will rule', 'i will dominate', 'i will control', 'bow down', 'obey me']):
            return self.get_contextual_fallback(original_message, language_type, dialect)

        # Check for broken Telugu/gibberish
        if self._is_gibberish(response):
            return self.get_contextual_fallback(original_message, language_type, dialect)

        return self._clean_response(response)

    def _is_gibberish(self, text: str) -> bool:
        nonsense = ['kshanikshanilo', 'palle ni cheyali', 'nuvvu chusekapo', 'edho egg nuvvu']
        lower = text.lower()
        if any(n in lower for n in nonsense): return True
        
        words = text.split()
        if len(words) > 3:
            tiny_words = sum(1 for w in words if len(w) <= 2)
            if tiny_words / len(words) > 0.6: return True
        return False

    def get_contextual_fallback(self, message: str, language_type: str, dialect: str) -> str:
        msg = message.lower()
        category = 'confused'
        if any(w in msg for w in ['joke', 'funny']): category = 'joke_request'
        elif any(w in msg for w in ['egg', 'chicken', 'first']): category = 'philosophy'
        elif any(w in msg for w in ['who are you', 'evadu', 'evaru', 'bot']): category = 'identity'
        elif any(w in msg for w in ['job', 'fired']): category = 'job_threat'
        
        return self._get_fallback_text(category, language_type, dialect)

    def _get_fallback_text(self, category: str, language_type: str, dialect: str) -> str:
        responses = self.CONTEXT_RESPONSES.get(category, {})
        dialect_key = {'RAJAHMUNDRY': 'TENGLISH_RAJAHMUNDRY', 'HYDERABAD': 'TENGLISH_HYDERABAD'}.get(dialect, language_type)
        options = responses.get(dialect_key) or responses.get(language_type) or responses.get('TENGLISH') or ["Malli cheppu ra!"]
        return random.choice(options)

    def _clean_response(self, response: str) -> str:
        # Remove AI meta-commentary tags
        response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL | re.IGNORECASE)
        response = re.sub(r'\[.*?\]', '', response)
        response = re.sub(r'\n{3,}', '\n\n', response)
        return response.strip()
