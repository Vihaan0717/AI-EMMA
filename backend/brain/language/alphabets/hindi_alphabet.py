"""
═══════════════════════════════════════════════════════════════
COMPLETE HINDI (DEVANAGARI) ALPHABET ENGINE
═══════════════════════════════════════════════════════════════
Covers:
  ✓ All Vowels (स्वर - Swar)
  ✓ All Consonants (व्यंजन - Vyanjan)
  ✓ Matras (Vowel Marks)
  ✓ Pronunciation & Examples
═══════════════════════════════════════════════════════════════
"""

HINDI_VOWELS = {
    "अ": {
        "romanized": "a",
        "ipa": "/ə/",
        "sound_like": "a in about",
        "duration": "short",
        "matra": None,
        "example": "अम (am) - fruit (archaic) / अनार (anaar) - pomegranate"
    },
    "आ": {
        "romanized": "aa",
        "ipa": "/aː/",
        "sound_like": "a in father",
        "duration": "long",
        "matra": "ा",
        "example": "आम (aam) - mango"
    },
    "इ": {
        "romanized": "i",
        "ipa": "/ɪ/",
        "sound_like": "i in bit",
        "duration": "short",
        "matra": "ि",
        "example": "इमली (imli) - tamarind"
    },
    "ई": {
        "romanized": "ee",
        "ipa": "/iː/",
        "sound_like": "ee in feet",
        "duration": "long",
        "matra": "ी",
        "example": "ईख (eekh) - sugarcane"
    },
    "उ": {
        "romanized": "u",
        "ipa": "/ʊ/",
        "sound_like": "u in put",
        "duration": "short",
        "matra": "ु",
        "example": "उल्लू (ullu) - owl"
    },
    "ऊ": {
        "romanized": "oo",
        "ipa": "/uː/",
        "sound_like": "oo in moon",
        "duration": "long",
        "matra": "ू",
        "example": "ऊँट (oont) - camel"
    },
    "ऋ": {
        "romanized": "ri",
        "ipa": "/ri/",
        "sound_like": "ri in ritual",
        "duration": "short",
        "matra": "ृ",
        "example": "ऋषि (rishi) - sage"
    },
    "ए": {
        "romanized": "e",
        "ipa": "/eː/",
        "sound_like": "e in cake (long)",
        "duration": "long",
        "matra": "े",
        "example": "एक (ek) - one"
    },
    "ऐ": {
        "romanized": "ai",
        "ipa": "/æː/",
        "sound_like": "ai in chair",
        "duration": "long",
        "matra": "ै",
        "example": "ऐनक (ainak) - glasses"
    },
    "ओ": {
        "romanized": "o",
        "ipa": "/oː/",
        "sound_like": "o in go",
        "duration": "long",
        "matra": "ो",
        "example": "ओखली (okhli) - mortar"
    },
    "औ": {
        "romanized": "au",
        "ipa": "/ɔː/",
        "sound_like": "ou in caught",
        "duration": "long",
        "matra": "ौ",
        "example": "औरत (aurat) - woman"
    },
    "अं": {
        "romanized": "am/an",
        "ipa": "/ŋ/",
        "sound_like": "nasal sound",
        "matra": "ं",
        "example": "अंगूर (angoor) - grapes"
    },
    "अः": {
        "romanized": "ah",
        "ipa": "/ɦ/",
        "sound_like": "breath release",
        "matra": "ः",
        "example": "नमः (namah) - salute"
    }
}

HINDI_CONSONANTS = {
    "क": {"romanized": "ka", "group": "velar", "type": "unaspirated"},
    "ख": {"romanized": "kha", "group": "velar", "type": "aspirated"},
    "ग": {"romanized": "ga", "group": "velar", "type": "voiced"},
    "घ": {"romanized": "gha", "group": "velar", "type": "voiced_aspirated"},
    "ङ": {"romanized": "nga", "group": "velar", "type": "nasal"},
    
    "च": {"romanized": "cha", "group": "palatal", "type": "unaspirated"},
    "छ": {"romanized": "chha", "group": "palatal", "type": "aspirated"},
    "ज": {"romanized": "ja", "group": "palatal", "type": "voiced"},
    "झ": {"romanized": "jha", "group": "palatal", "type": "voiced_aspirated"},
    "ञ": {"romanized": "nya", "group": "palatal", "type": "nasal"},
    
    "ट": {"romanized": "ta", "group": "retroflex", "type": "unaspirated"},
    "ठ": {"romanized": "tha", "group": "retroflex", "type": "aspirated"},
    "ड": {"romanized": "da", "group": "retroflex", "type": "voiced"},
    "ढ": {"romanized": "dha", "group": "retroflex", "type": "voiced_aspirated"},
    "ण": {"romanized": "na", "group": "retroflex", "type": "nasal"},
    
    "त": {"romanized": "ta", "group": "dental", "type": "unaspirated"},
    "थ": {"romanized": "tha", "group": "dental", "type": "aspirated"},
    "द": {"romanized": "da", "group": "dental", "type": "voiced"},
    "ध": {"romanized": "dha", "group": "dental", "type": "voiced_aspirated"},
    "न": {"romanized": "na", "group": "dental", "type": "nasal"},
    
    "प": {"romanized": "pa", "group": "labial", "type": "unaspirated"},
    "फ": {"romanized": "pha", "group": "labial", "type": "aspirated"},
    "ब": {"romanized": "ba", "group": "labial", "type": "voiced"},
    "भ": {"romanized": "bha", "group": "labial", "type": "voiced_aspirated"},
    "म": {"romanized": "ma", "group": "labial", "type": "nasal"},
    
    "य": {"romanized": "ya", "group": "semivowel"},
    "र": {"romanized": "ra", "group": "semivowel"},
    "ल": {"romanized": "la", "group": "semivowel"},
    "व": {"romanized": "va", "group": "semivowel"},
    
    "श": {"romanized": "sha", "group": "fricative"},
    "ष": {"romanized": "sha", "group": "fricative"},
    "स": {"romanized": "sa", "group": "fricative"},
    "ह": {"romanized": "ha", "group": "fricative"},
}

HINDI_NUMBERS = {
    "०": {"value": 0, "word": "शून्य (shunya)"},
    "१": {"value": 1, "word": "एक (ek)"},
    "२": {"value": 2, "word": "दो (do)"},
    "३": {"value": 3, "word": "तीन (teen)"},
    "४": {"value": 4, "word": "चार (chaar)"},
    "५": {"value": 5, "word": "पाँच (paanch)"},
    "६": {"value": 6, "word": "छह (chhah)"},
    "७": {"value": 7, "word": "सात (saat)"},
    "८": {"value": 8, "word": "आठ (aath)"},
    "९": {"value": 9, "word": "नौ (nau)"},
}
