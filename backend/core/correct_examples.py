# core/correct_examples.py
"""
These are the CORRECT messages Vera should generate.
Used as few-shot training examples AND as test cases.
"""

CORRECT_EXAMPLES = {

    "annaya_normal": {
        "situation": "Checking in with Annaya casually",
        "language": "Telugu/Mixed",
        "bubbles": [
            "Annaya, ela unnav?",
            "Chala rojulu ayindi ra matladadam. Busy gaa unnava?"
        ],
        "why_correct": [
            "Starts with 'Annaya' — proper address form",
            "Uses 'unnav' not 'unnaru' — appropriate for elder brother (slightly formal but warm)",
            "No 'Boss', no 'Nee enti ra', no English slang",
            "Short natural bubbles like real WhatsApp"
        ],
        "wrong_version": "Ento, Nee enti ra? How's it going, Boss?"
    },

    "annaya_upset": {
        "situation": "Annaya is upset, need to approach carefully",
        "language": "Telugu/Mixed",
        "bubbles": [
            "Annaya...",
            "Meeru okay ga unnara? Emi ayindi ra?",
            "Nenu ikkade unnanu. Matladali ante cheppandi, vinataniki ready ga unnanu."
        ],
        "why_correct": [
            "Starts softly with just 'Annaya...' — shows you noticed",
            "Uses 'Meeru' + 'unnara' — respectful form for elder",
            "'Nenu ikkade unnanu' = I am here — emotional safety",
            "Lets him lead — doesn't push"
        ]
    },

    "teacher_question": {
        "situation": "Asking teacher a doubt after getting an answer wrong",
        "language": "English (formal)",
        "bubbles": [
            "Good morning Ma'am.",
            "I got that answer wrong and I want to understand why.",
            "Could you please explain the correct approach? I want to learn it properly."
        ],
        "why_correct": [
            "Formal greeting first",
            "Honest admission without making excuses",
            "'Please' and 'properly' show genuine respect",
            "No markdown, no bullet points — clean human message"
        ]
    },

    "grandmother_message": {
        "situation": "Sending a message to grandmother",
        "language": "Telugu",
        "bubbles": [
            "Ammamma, ela unnaru?",
            "Meeru bagunnara? Nenu meeru gurinchi aalochistunna.",
            "Phone chestunanaa, pick up cheyandi."
        ],
        "why_correct": [
            "'Ammamma' — correct address",
            "'Meeru' and 'unnaru' — highest respect form",
            "Simple short sentences — easy for elder to read",
            "Warm and caring, not transactional"
        ]
    },

    "close_friend": {
        "situation": "Catching up with best friend",
        "language": "Mixed (Telugu/English)",
        "bubbles": [
            "Bro, enti ra?",
            "Chala days aindi da matladadam. What's happening?"
        ],
        "why_correct": [
            "Casual 'Bro' and 'ra' — appropriate for close friend",
            "Natural code-switching (Telugu + English)",
            "Short, punchy, real"
        ]
    },

    "child_helping": {
        "situation": "Helping a young child with something",
        "language": "Simple English/Telugu",
        "bubbles": [
            "Hey! Want me to show you something?",
            "It's really easy, don't worry.",
            "We can do it together!"
        ],
        "why_correct": [
            "Enthusiastic and warm — matches child's energy",
            "No pressure words",
            "Short sentences — child-appropriate",
            "'Together' — inclusive and encouraging"
        ]
    }
}
