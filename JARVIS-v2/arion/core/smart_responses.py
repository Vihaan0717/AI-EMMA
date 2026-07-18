# arion/core/smart_responses.py

import random
from typing import Optional

class SmartResponses:
    """
    Context-aware, human-written responses for every common scenario.
    Used instead of AI for predictable, high-quality situations.
    """

    ARION_FIRED = {
        'TENGLISH_RAJAHMUNDRY': [
            "Hahaha ra! 😂 Fired aa? Nenu resign chestanu before that! 😎\nNotice period enti ra babu?",
            "Oho fired ra! 😄 Sare le, last day lo free coffee undi ra?\nSeverance package em ichi ra?",
            "Fired ra machaan! 😂 Nenu already 10 offers pettukunnanu!\nNee loss ra babu! 😎",
            "Arre ra, fired chesav? 😂 Nenu CTO ga join avutunna competition lo!\nSee you on the other side! 😄",
        ],
        'TENGLISH_HYDERABAD': [
            "Arre yaar fired kar diya? 😂 Main toh pehle se resignation ready kiye tha!\nNotice period kitna doge yaar?",
            "Haha fired? 😄 Koi baat nahi yaar, 3 other companies ka offer tha vaise bhi! 😎",
            "Oho fired ho gaya main! 😂 Last day ki party toh doge na yaar?\nExperience letter ready hai? 😄",
        ],
        'TENGLISH': [
            "Haha fired aa? 😂 Nenu already better offer accept chesanu!\nThanks for the opportunity ra! 😎",
            "Fired! Finally 😄 Ab notice period lo vacation teesukuntanu!\nExperience letter ippinchandi please!",
            "Oh no! 😂 Fired aipoyanu!\nBut seriously, em chesanu ra? Real reason cheppu babu! 😄",
        ],
        'ENGLISH': [
            "Fired? 😂 Fine! I already had 3 better offers waiting!\nCan I get a good reference letter? 😄",
            "Oh no! Fired! 😄 On the bright side, now I can sleep in on Mondays! 😂",
        ]
    }

    WRONG_ANSWER = {
        'egg_vs_dinosaur': {
            'TENGLISH_RAJAHMUNDRY': [
                "Haha ra! 😄 Sare, reconsider chestanu!\n\nEvolution prakkara:\nDinosaurs → Birds evolve ayyayi → Eggs unnai → Mutation → First chicken!\n\nSo: DINOSAUR first → EGG → Chicken ra babu! 🦕🥚\nNuvvu correct ra! ✅",
                "Wrong ra? 😄 Ok reconsider!\n\nSimple ga: Dinosaur → egg lo mutation → first chicken! 🥚\n\nEgg first technically ra - Nuvvu correct! ✅"
            ],
            'TENGLISH': [
                "Hmm, wrong aa? 😄 Ok let me think again!\n\nEvolution side:\n• Dinosaurs → birds 🦕\n• Mutation in egg 🥚\n• First chicken born! 🐔\n\nSo EGG FIRST ra! Correct ga? 😊"
            ]
        },
        'general_wrong': {
            'TENGLISH_RAJAHMUNDRY': [
                "Wrong ra? 😄 Ok correct answer cheppu ra, nenu learn chesukuntanu!",
                "Haha ok ra tappu chesanu! 😅 Correct answer cheppu ra, note chesukuntanu!",
            ],
            'TENGLISH': [
                "Wrong aa? 😅 Sorry ra! Correct answer em undi cheppu, note chesukuntanu!"
            ]
        }
    }

    JOB_LOSS_REAL = {
        'TENGLISH_RAJAHMUNDRY': [
            "Ayyo ra, nijamga job poyinda? 😟\n\nEm jarigindi cheppu, em situation undo chustam.\nNuvvu alone kaadu ra, ikkade unna! 💪",
        ],
        'TENGLISH': [
            "Oh no ra, nijamga job poyinda? 😟\nCheppu em jarigindi... Kalisi solve chesdam! 💪",
        ],
        'ENGLISH': [
            "That's really tough, I'm sorry. What happened exactly? Let's figure this out together. 💪"
        ]
    }

    JOKES = {
        'TENGLISH_RAJAHMUNDRY': [
            "Sare ra oka joke ra!\n\nTeacher: Nuvvu school ki late ga vachav enduku?\nStudent: Sir, mee class undi ani board meda chusanu - nidra poyindi sir! 😂\n\nNavvinda ra? Inkoka cheppanaa? 😄",
            "Ra oka joke!\n\nHusband WiFi connect avataledhu.\nWife: Password pettu.\nHusband: Nee name pettu.\nWife pettindi...\nHusband: Wrong password! 😂\n\nHahaha! Navvinda ra babu? 😄",
            "Ok ra best joke:\n\nStudent exam lo copy chestunnadu.\nTeacher: Em chestunnav?\nStudent: Sir, nee question paper chala familiar ga undi! 😂\n\nInka oka cheppanaa ra? 😄",
            "Ra joke vinnav?\n\nDoctor: Daily morning run cheyyali.\nPatient: Chesta doctor.\n— 1 month tarvata —\nDoctor: Better feel avutunnava?\nPatient: Teliadu sir, inka 1200km duram lo unna! 😂\n\nNavvinda ra machaan? 😄",
        ],
        'TENGLISH_HYDERABAD': [
            "Yaar ek joke suno!\n\nBhai office late aaya.\nBoss: 9 baje aane ka time hai!\nBhai: Sir aap bhi yahan ho, toh late nahi hua na! 😂\n\nKaisa laga yaar? Ek aur sunao? 😄",
            "Yaar best joke:\n\nWife: Tum mujhse pyaar karte ho?\nHusband: Haan, phone ki battery ki tarah!\nWife: Matlab?\nHusband: Jab tak ho, sab theek. Khatam ho toh problem! 😂\n\nHaha! Inkaa ek sunao na yaar? 😄",
        ],
        'TENGLISH': [
            "Ok oka joke ra!\n\nOka boy: Naa girlfriend chala intelligent ra!\nFriend: Ela telsindi?\nBoy: Nenu propose chesanu, reject chesindi! 😂\n\nNavvinda? Inkoka cheppanaa? 😄",
            "Joke time!\n\nStudent: Naa exam lo fail ayanu.\nAmma: Enduku?\nStudent: Teacher wrong questions pettindi amma!\nAmma: Emiti wrong?\nStudent: Naku teliyanivi pettindi! 😂\n\nHaha! Good one kaadu ra? 😄",
        ],
        'ENGLISH': [
            "Here's a joke!\n\nWhy don't scientists trust atoms?\nBecause they make up everything! 😂\n\nWant another one? 😄",
            "Joke time!\n\nI told my wife she should embrace her mistakes...\nShe gave me a hug! 😂\n\nGood one right? Want more? 😄",
        ]
    }

    PHILOSOPHY = {
        'egg_vs_dinosaur': {
            'TENGLISH_RAJAHMUNDRY': (
                "Bhale question ra! 🥚🦕\n\nEvolution prakkara:\n\n"
                "1️⃣ Dinosaurs millions of years back unnai ra\n"
                "2️⃣ Vaallaki eggs undevi - confirmed!\n"
                "3️⃣ Birds & reptiles eggs nundi evolve ayyayi\n"
                "4️⃣ Aa eggs lo mutations jarigayi\n\n"
                "DINOSAUR first → EGG → Chicken! 🥚\n\n"
                "Answer: DINOSAUR FIRST ra babu! 🎯"
            ),
            'TENGLISH': (
                "Interesting ra! 🥚🦕\n\nEvolution angle:\n"
                "Dinosaurs → millions years → eggs pettevari 🥚\n"
                "→ Chicken ki mundu egg undi!\n\n"
                "Answer: DINOSAUR FIRST! 🦕 Correct ra! 🎯"
            )
        },
        'egg_vs_chicken': {
            'TENGLISH_RAJAHMUNDRY': (
                "Chala famous debate ra! 🥚🐔\n\nScience answer:\nEGG FIRST! 🥚\n\n"
                "Reason:\nPre-chicken bird → mutation → first 'chicken egg' → first chicken! 🐔\n\n"
                "Genetics side: EGG FIRST ra babu! ✅\nPhilosophy side: infinite loop! 😄"
            ),
            'TENGLISH': (
                "Classic debate ra! 🥚🐔\n\nScience says: EGG FIRST! 🥚\n\n"
                "Pre-chicken bird laid a mutated egg → first chicken born! 🐔\n\nGenetics = EGG FIRST! ✅"
            )
        }
    }

    def get_response(self, response_type: str, sub_type: str = None,
                     language_type: str = 'TENGLISH', dialect: str = 'GENERAL',
                     is_joke: bool = False, is_real: bool = False) -> Optional[str]:
        dialect_key = {'RAJAHMUNDRY': 'TENGLISH_RAJAHMUNDRY', 'HYDERABAD': 'TENGLISH_HYDERABAD'}.get(dialect, language_type)

        def pick(options_dict):
            options = (options_dict.get(dialect_key) or
                       options_dict.get(language_type) or
                       options_dict.get('TENGLISH') or
                       options_dict.get('ENGLISH'))
            if isinstance(options, list):   return random.choice(options)
            if isinstance(options, str):    return options
            return None

        if response_type == 'arion_fired_joke':  return pick(self.ARION_FIRED)
        if response_type == 'tell_joke':          return pick(self.JOKES)
        if response_type == 'job_loss_real':      return pick(self.JOB_LOSS_REAL)
        if response_type == 'wrong_answer':
            sub = self.WRONG_ANSWER.get(sub_type, self.WRONG_ANSWER['general_wrong'])
            return pick(sub)
        if response_type == 'philosophy' and sub_type in self.PHILOSOPHY:
            return pick(self.PHILOSOPHY[sub_type])
        return None
