# arion/core/intent_engine.py

import re
import random
from typing import Dict, List, Optional

class IntentEngine:
    """
    Deep intent understanding system.
    Detects: jokes, sarcasm, roleplay, tests, real emotions, context shifts
    """

    JOKE_SIGNALS = [
        r'\bjoke\b', r'\bjokes\b', r'\bfunny\b', r'\blol\b', r'\bhaha\b', r'\bxd\b',
        r'\bkidding\b', r'\bjust kidding\b', r'\bjk\b', r'\bprank\b', r'\btroll\b',
        r'wrong answer', r'right answer', r'wrong ra', r'correct ra',
        r"you('re| are) fired", r'you lost (your |the )?job',
        r'(already |u )?lost the job', r'pack (ur|your) (things|bags|stuff)',
        r'you are (terminated|dismissed|done)', r'arion (fired|terminated)',
        r'ur (job|position) is (gone|lost|over)', r'job (poyindi|gone|over)',
        r'tappu cheppav', r'wrong answer cheppav', r'wrong bro', r'tappu ra',
        r'nee job poyindi', r'fired ra', r'fired ma', r'pack chesuko', r'vellipomma',
    ]

    REAL_DISTRESS = [
        r'i (actually|really) lost (my )?job', r'terminated (from|at)',
        r'fired from (my |the )?office', r'layoff', r'laid off',
        r'resignation', r'resigned', r'nijamga job poyindi', r'actually fired chesaru',
        r'chala tension ga undi', r'em cheyyalo teliadu', r'help kavali seriously',
        r'nijamga chala kష్టంగా undi',
    ]

    CONTEXT_INTENTS = {
        'joke':                 ['joke cheppu', 'tell me a joke', 'funny ga cheppu', 'navvinchu', 'oka joke ra', 'jokes unnaya'],
        'wrong_answer_game':    ['wrong answer', 'wrong ra', 'tappu cheppav', 'wrong bro', 'incorrect', 'nope', 'answer tappu'],
        'arion_fired_roleplay': ['you are fired', 'ur fired', "you're fired", 'already lost the job', 'pack ur things',
                                  'pack your things', 'you lost the job', 'job poyindi', 'fired ra', 'fired ma',
                                  'terminated', 'you are done', 'ur done', 'your job is lost', 'arion job poyindi',
                                  'pack chesuko', 'nee job poyindi'],
        'philosophy':           ['egg first', 'chicken first', 'egg or chicken', 'dinosaur first', 'which came first',
                                  'meaning of life', 'god exists', 'what is real', 'free will'],
        'emotional_real':       ['feeling sad', 'depressed', 'crying', 'heart broken', 'i hate my life',
                                  'chala sad ga undi', 'rodustu unna', 'em cheyyalo teliadu nijamga'],
        'mathematics':          ['calculate', 'solve', 'find x', 'equation', 'formula', 'percentage',
                                  'profit', 'loss', 'interest', 'trigonometry', 'math problem'],
        'casual':               ['hi', 'hello', 'hey', 'wassup', 'sup', 'ela unnav', 'em chestunnav', 'enti'],
    }

    RESPONSE_TYPES = {
        'joke':                 'tell_joke',
        'wrong_answer_game':    'defend_or_accept',
        'arion_fired_roleplay': 'arion_fired_joke',
        'philosophy':           'philosophical_answer',
        'emotional_real':       'emotional_support',
        'mathematics':          'math_solution',
        'casual':               'casual_chat',
        'general':              'general',
    }

    def __init__(self):
        self.conversation_contexts = {}
        print("[Intent Engine] Loaded")

    def detect_full_intent(self, message: str, phone_number: str, conversation_history: list = None) -> Dict:
        msg_lower = message.lower().strip()

        result = {
            'primary_intent': 'general', 'secondary_intents': [],
            'is_joke': False, 'is_sarcasm': False, 'is_roleplay': False, 'is_test': False,
            'is_real_distress': False, 'emotional_state': 'neutral',
            'topic': 'general', 'response_type': 'general', 'confidence': 0.5,
            'context_shift': False, 'private_info_risk': False, 'raw_message': message
        }

        # Check joke signals
        for pattern in self.JOKE_SIGNALS:
            if re.search(pattern, msg_lower, re.IGNORECASE):
                result['is_joke'] = True
                result['confidence'] = 0.9
                break

        # Check real distress (overrides joke flag)
        for pattern in self.REAL_DISTRESS:
            if re.search(pattern, msg_lower, re.IGNORECASE):
                result['is_real_distress'] = True
                result['is_joke'] = False
                result['emotional_state'] = 'distressed'
                result['confidence'] = 0.95
                break

        # Match specific intents
        for intent_name, triggers in self.CONTEXT_INTENTS.items():
            for trigger in triggers:
                if trigger.lower() in msg_lower:
                    result['primary_intent'] = intent_name
                    result['response_type'] = self.RESPONSE_TYPES.get(intent_name, 'general')
                    result['confidence'] = 0.85
                    break

        # Regex check for ARION-fired roleplay (higher precision)
        arion_fired_patterns = [
            r'(you|ur|arion).{0,10}(fired|terminated|lost.*job|job.*lost|job.*poy)',
            r'(already|pack).{0,20}(job|things|stuff|bags)',
            r'(you|ur).{0,5}(done|over|finished).{0,10}(job|work)',
        ]
        for pattern in arion_fired_patterns:
            if re.search(pattern, msg_lower, re.IGNORECASE):
                result['primary_intent'] = 'arion_fired_roleplay'
                result['is_joke'] = True
                result['is_roleplay'] = True
                result['response_type'] = 'arion_fired_joke'
                result['confidence'] = 0.95
                break

        # Context from history
        if conversation_history:
            for msg in conversation_history[-6:]:
                content = msg.get('content', '').lower()
                for pattern in self.JOKE_SIGNALS:
                    if re.search(pattern, content, re.IGNORECASE):
                        if not result['is_real_distress']:
                            result['is_joke'] = True
                        break

        result['topic'] = self._detect_topic(msg_lower)
        if not result['is_real_distress']:
            result['emotional_state'] = self._detect_emotion(msg_lower)

        self._update_context(phone_number, result)
        return result

    def _detect_topic(self, text: str) -> str:
        topic_keywords = {
            'mathematics':  ['calculate', 'solve', 'formula', 'equation', 'math', 'percentage', 'profit'],
            'philosophy':   ['egg', 'chicken', 'dinosaur', 'meaning', 'god', 'real', 'exist', 'free will'],
            'job':          ['job', 'work', 'office', 'fired', 'hired', 'salary', 'career', 'interview'],
            'joke':         ['joke', 'funny', 'laugh', 'haha', 'lol', 'navvinchu', 'jokes'],
            'relationship': ['love', 'girlfriend', 'boyfriend', 'crush', 'marriage', 'breakup'],
            'technology':   ['python', 'code', 'programming', 'software', 'app', 'bug', 'debug'],
            'exam':         ['exam', 'test', 'marks', 'study', 'rank', 'tcs', 'nqt', 'gate'],
        }
        for topic, keywords in topic_keywords.items():
            if any(kw in text for kw in keywords):
                return topic
        return 'general'

    def _detect_emotion(self, text: str) -> str:
        emotions = {
            'happy':   ['happy', 'excited', 'great', 'awesome', 'santhosham', '😊', '😄'],
            'sad':     ['sad', 'crying', 'depressed', 'lonely', 'dukkham', '😢', '😭'],
            'angry':   ['angry', 'frustrated', 'irritated', 'mad', 'kopam', '😠', '😡'],
            'playful': ['haha', 'lol', 'xd', '😂', '😜', 'funny', 'joke'],
            'urgent':  ['urgent', 'asap', 'fast', 'jaldi', 'quick', 'hurry'],
        }
        for emotion, signals in emotions.items():
            if any(s.lower() in text for s in signals):
                return emotion
        return 'neutral'

    def _update_context(self, phone: str, intent_result: Dict):
        ctx = self.conversation_contexts.setdefault(phone, {
            'history': [], 'last_topic': None, 'joke_streak': 0, 'is_testing_arion': False
        })
        ctx['joke_streak'] = ctx['joke_streak'] + 1 if intent_result['is_joke'] else 0
        ctx['is_testing_arion'] = intent_result['primary_intent'] in ['arion_fired_roleplay', 'knowledge_test', 'wrong_answer_game']
        ctx['last_topic'] = intent_result['topic']
        ctx['history'].append({'intent': intent_result['primary_intent'], 'is_joke': intent_result['is_joke'], 'topic': intent_result['topic']})
        ctx['history'] = ctx['history'][-10:]

    def get_user_context(self, phone: str) -> Dict:
        return self.conversation_contexts.get(phone, {})
