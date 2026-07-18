"""
Language Detector — Detects what language a person 
uses and responds in THAT language, not English by default.
"""

from core.people_registry import PeopleRegistry

# Global registry instance to avoid re-instantiation overhead
_PEOPLE_REGISTRY = PeopleRegistry()

# ── Language Profiles ────────────────────────────────────────────────────────
LANGUAGE_PROFILES = {
    "telugu": {
        "script":          "Telugu/Roman transliteration",
        "respect_markers": ["Annaya", "Akka", "Garru", "Meeru", "Mee"],
        "casual_markers":  ["ra", "di", "bro", "yaar"],
        "elder_form":      "formal Telugu with 'Meeru' (not 'Neenu')",
        "peer_form":       "casual Telugu with 'ra/di' suffix",
        "example_elder":   "Annaya, ela unnaru? Meeru chala rojulu ga kanapadadam ledu.",
        "example_peer":    "Bro, enti ra? Ela unnav?",
        "example_child":   "Hey! Neeku oka chinna story cheppanaa?",
        "what_to_never_say": [
            "'Nee' to elders (disrespectful — use 'Mee')",
            "'ra' suffix to elders (too casual)",
            "English slang mixed into formal Telugu",
        ]
    },
    "hindi": {
        "respect_markers": ["Bhaiya", "Didi", "Ji", "Aap"],
        "casual_markers":  ["yaar", "bhai", "bro"],
        "elder_form":      "formal Hindi with 'Aap' (not 'Tum/Tu')",
        "peer_form":       "casual Hindi with 'tum'",
        "example_elder":   "Bhaiya, aap kaise hain? Bahut dino baad baat ho rahi hai.",
        "example_peer":    "Yaar, kya chal raha hai?",
        "example_child":   "Hey! Aaj school mein kya hua?",
        "what_to_never_say": [
            "'Tu' to elders (very disrespectful)",
            "'Tum' to grandparents (use 'Aap')",
        ]
    },
    "english": {
        "respect_markers": ["Sir", "Ma'am", "Please", "May I"],
        "casual_markers":  ["hey", "bro", "dude", "what's up"],
        "elder_form":      "formal English, full sentences, no contractions",
        "peer_form":       "casual English, contractions OK, light humor OK",
        "example_elder":   "Good morning Sir. I hope you are doing well.",
        "example_peer":    "Hey! What's up? Haven't talked in a while.",
        "example_child":   "Hey! Want to hear something really cool?",
        "what_to_never_say": [
            "Slang to teachers/elders",
            "'Dude' or 'bro' to authority figures",
        ]
    },
    "mixed": {
        "description": "Telugu+English code-switching (most natural for young users)",
        "rule": "Match what the person naturally uses. Never force one language.",
        "example_annaya": "Annaya, ela unnav? Chala busy ga unnava lately?",
        "example_friend":  "Bro, enti ra? What's happening da?",
    }
}

def detect_person_language(person_name: str) -> dict:
    """Get the correct language profile for a person."""
    person = _PEOPLE_REGISTRY.get_person(person_name)
    if not person:
        return LANGUAGE_PROFILES["english"]
    return LANGUAGE_PROFILES.get(person.preferred_language, LANGUAGE_PROFILES["english"])

def get_correct_address_form(person_name: str, relationship_type: str, language: str) -> str:
    """
    Returns exactly HOW to address this person.
    This is the most critical part — getting the address form wrong
    is immediately disrespectful.
    """
    forms = {
        # Telugu address forms
        ("grandparent", "telugu"):     "Thatha / Ammamma (full name + garru if needed)",
        ("parent",      "telugu"):     "Nanna / Amma (never use their first name)",
        ("annaya",      "telugu"):     "Annaya (always prefix — never just their name)",
        ("akka",        "telugu"):     "Akka (always prefix)",
        ("teacher",     "telugu"):     "Sir / Madam / Teacher Garru",
        ("close_friend","telugu"):     "Bro / Da / Ra / their name casually",
        ("younger_sibling","telugu"):  "Their name directly / chinna / chelli",
        ("child_student","telugu"):    "Their name + warmth, no title needed",

        # Hindi address forms
        ("grandparent", "hindi"):      "Dada Ji / Dadi Ji / Nana Ji / Nani Ji",
        ("parent",      "hindi"):      "Papa / Maa / Papa Ji",
        ("annaya",      "hindi"):      "Bhaiya (always — never first name to elder brother)",
        ("teacher",     "hindi"):      "Sir / Madam Ji",
        ("close_friend","hindi"):      "Yaar / Bhai / their name",

        # English address forms
        ("grandparent", "english"):    "Grandpa / Grandma (warm, never just their name)",
        ("parent",      "english"):    "Dad / Mom (never first name unless they prefer it)",
        ("teacher",     "english"):    "Sir / Ma'am / Mr. [Name] / Ms. [Name]",
        ("close_friend","english"):    "Their name / Bro / Dude (whatever they use)",
        ("boss",        "english"):    "Their name (professional) / Sir if very formal",
    }

    key = (relationship_type, language)
    return forms.get(key, f"Use '{person_name}' with appropriate respect")
