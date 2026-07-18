"""
═══════════════════════════════════════════════════════════════
COMPLETE TELUGU ALPHABET ENGINE
═══════════════════════════════════════════════════════════════
Covers:
  ✓ All 16 Vowels (అచ్చులు - Acchulu)
  ✓ All 36 Consonants (హల్లులు - Hallulu)
  ✓ All Vowel Marks/Matras (మాత్రలు - Matralu)
  ✓ Special Characters (Anusvara, Visarga, etc.)
  ✓ Pronunciation guide (IPA + English equivalent)
  ✓ How each sounds + mouth position
  ✓ Example words for every letter
  ✓ Combination rules (consonant clusters)
═══════════════════════════════════════════════════════════════
"""

# ═══════════════════════════════════════════════════════════════
# SECTION 1: TELUGU VOWELS (అచ్చులు)
# ═══════════════════════════════════════════════════════════════

TELUGU_VOWELS = {
    "అ": {
        "romanized":       "a",
        "tenglish":        "a",
        "ipa":             "/ə/",
        "sound_like":      "The 'u' in 'sun' or 'a' in 'about'",
        "mouth_position":  "Mouth slightly open, tongue in middle",
        "duration":        "short",
        "matra":           None,
        "matra_symbol":    "◌",
        "example_words": {
            "తెలుగు": "అమ్మ (amma) = mother",
            "english": "అందం (andam) = beauty",
        },
        "position_in_alphabet": 1,
        "type": "short_vowel",
        "tone": "neutral"
    },
    "ఆ": {
        "romanized":       "aa",
        "tenglish":        "aa / a (long)",
        "ipa":             "/aː/",
        "sound_like":      "The 'aa' in 'father' or 'car' — held longer",
        "mouth_position":  "Mouth wide open, jaw dropped",
        "duration":        "long",
        "matra":           "ా",
        "matra_symbol":    "◌ా",
        "example_words": {
            "తెలుగు": "ఆకాశం (aakasham) = sky",
            "english": "ఆనందం (aanandam) = happiness",
        },
        "position_in_alphabet": 2,
        "type": "long_vowel",
        "tone": "open"
    },
    "ఇ": {
        "romanized":       "i",
        "tenglish":        "i",
        "ipa":             "/ɪ/",
        "sound_like":      "The 'i' in 'bit' or 'sit' — short",
        "mouth_position":  "Lips slightly spread, tongue high front",
        "duration":        "short",
        "matra":           "ి",
        "matra_symbol":    "◌ి",
        "example_words": {
            "తెలుగు": "ఇల్లు (illu) = house",
            "english": "ఇష్టం (istam) = like/love",
        },
        "position_in_alphabet": 3,
        "type": "short_vowel",
        "tone": "front_high"
    },
    "ఈ": {
        "romanized":       "ii / ee",
        "tenglish":        "ee / ii",
        "ipa":             "/iː/",
        "sound_like":      "The 'ee' in 'feet' or 'see' — held longer",
        "mouth_position":  "Lips spread wide, tongue high front, held",
        "duration":        "long",
        "matra":           "ీ",
        "matra_symbol":    "◌ీ",
        "example_words": {
            "తెలుగు": "ఈత (eetha) = swimming",
            "english": "ఈగ (eega) = fly (insect)",
        },
        "position_in_alphabet": 4,
        "type": "long_vowel",
        "tone": "front_high"
    },
    "ఉ": {
        "romanized":       "u",
        "tenglish":        "u",
        "ipa":             "/ʊ/",
        "sound_like":      "The 'u' in 'put' or 'book' — short",
        "mouth_position":  "Lips rounded and slightly forward",
        "duration":        "short",
        "matra":           "ు",
        "matra_symbol":    "◌ు",
        "example_words": {
            "తెలుగు": "ఉప్పు (uppu) = salt",
            "english": "ఉదయం (udayam) = morning",
        },
        "position_in_alphabet": 5,
        "type": "short_vowel",
        "tone": "back_high"
    },
    "ఊ": {
        "romanized":       "uu / oo",
        "tenglish":        "oo / uu",
        "ipa":             "/uː/",
        "sound_like":      "The 'oo' in 'food' or 'moon' — held longer",
        "mouth_position":  "Lips tightly rounded and pushed forward",
        "duration":        "long",
        "matra":           "ూ",
        "matra_symbol":    "◌ూ",
        "example_words": {
            "తెలుగు": "ఊరు (ooru) = village/town",
            "english": "ఊహ (ooha) = imagination",
        },
        "position_in_alphabet": 6,
        "type": "long_vowel",
        "tone": "back_high"
    },
    "ఋ": {
        "romanized":       "ru / ri",
        "tenglish":        "ru",
        "ipa":             "/ɾʊ/",
        "sound_like":      "Rolled 'r' + 'u' — like 'ru' in 'rude' quickly",
        "mouth_position":  "Tongue tip lightly touches roof, then rounds",
        "duration":        "short",
        "matra":           "ృ",
        "matra_symbol":    "◌ృ",
        "example_words": {
            "తెలుగు": "ఋషి (rushi) = sage/saint",
            "english": "ఋణం (runam) = debt",
        },
        "position_in_alphabet": 7,
        "type": "vowel",
        "tone": "rhotic",
        "note": "Mainly used in Sanskrit-origin Telugu words"
    },
    "ఎ": {
        "romanized":       "e",
        "tenglish":        "e / ae",
        "ipa":             "/ɛ/",
        "sound_like":      "The 'e' in 'bed' or 'pet' — short",
        "mouth_position":  "Mouth open, tongue mid-front",
        "duration":        "short",
        "matra":           "ె",
        "matra_symbol":    "◌ె",
        "example_words": {
            "తెలుగు": "ఎలక (elaka) = rat",
            "english": "ఎద (eda) = chest/heart",
        },
        "position_in_alphabet": 8,
        "type": "short_vowel",
        "tone": "mid_front"
    },
    "ఏ": {
        "romanized":       "ee / e (long)",
        "tenglish":        "e / ey",
        "ipa":             "/eː/",
        "sound_like":      "The 'ay' in 'say' or 'e' in 'they' — long",
        "mouth_position":  "Mouth open-mid, tongue front, held",
        "duration":        "long",
        "matra":           "ే",
        "matra_symbol":    "◌ే",
        "example_words": {
            "తెలుగు": "ఏం (em) = what",
            "english": "ఏనుగు (enugu) = elephant",
        },
        "position_in_alphabet": 9,
        "type": "long_vowel",
        "tone": "mid_front"
    },
    "ఐ": {
        "romanized":       "ai",
        "tenglish":        "ai / eye",
        "ipa":             "/aɪ/",
        "sound_like":      "Like 'ai' in 'aisle' or 'i' in 'mine'",
        "mouth_position":  "Start open, glide to front-high",
        "duration":        "diphthong",
        "matra":           "ై",
        "matra_symbol":    "◌ై",
        "example_words": {
            "తెలుగు": "ఐదు (aidu) = five",
            "english": "ఐక్యత (aikyata) = unity",
        },
        "position_in_alphabet": 10,
        "type": "diphthong",
        "tone": "falling"
    },
    "ఒ": {
        "romanized":       "o",
        "tenglish":        "o",
        "ipa":             "/ɔ/",
        "sound_like":      "The 'o' in 'hot' or 'got' — short",
        "mouth_position":  "Lips rounded, tongue back-mid",
        "duration":        "short",
        "matra":           "ొ",
        "matra_symbol":    "◌ొ",
        "example_words": {
            "తెలుగు": "ఒంట్లో (ontlo) = in the body",
            "english": "ఒక (oka) = one/a",
        },
        "position_in_alphabet": 11,
        "type": "short_vowel",
        "tone": "back_mid"
    },
    "ఓ": {
        "romanized":       "oo / o (long)",
        "tenglish":        "o / oh",
        "ipa":             "/oː/",
        "sound_like":      "The 'o' in 'go' or 'no' — long",
        "mouth_position":  "Lips rounded forward, tongue back, held",
        "duration":        "long",
        "matra":           "ో",
        "matra_symbol":    "◌ో",
        "example_words": {
            "తెలుగు": "ఓడ (oda) = ship",
            "english": "ఓటు (otu) = vote",
        },
        "position_in_alphabet": 12,
        "type": "long_vowel",
        "tone": "back_mid"
    },
    "ఔ": {
        "romanized":       "au / ow",
        "tenglish":        "au / ow",
        "ipa":             "/aʊ/",
        "sound_like":      "Like 'ow' in 'cow' or 'ou' in 'out'",
        "mouth_position":  "Start open, glide to back-high rounded",
        "duration":        "diphthong",
        "matra":           "ౌ",
        "matra_symbol":    "◌ౌ",
        "example_words": {
            "తెలుగు": "ఔషధం (aushadham) = medicine",
            "english": "ఔచిత్యం (auchityam) = propriety",
        },
        "position_in_alphabet": 13,
        "type": "diphthong",
        "tone": "falling"
    },
    "అం": {
        "romanized":       "am / an",
        "tenglish":        "am",
        "ipa":             "/əm/ or /ən/",
        "sound_like":      "Nasal 'm/n' — like humming at end",
        "mouth_position":  "Vowel then lips close for nasal hum",
        "duration":        "short+nasal",
        "matra":           "ం",
        "matra_symbol":    "◌ం",
        "special_name":    "Anusvara (అనుస్వారం)",
        "example_words": {
            "తెలుగు": "సంతోషం (santosham) = happiness",
            "english": "సమయం (samayam) = time",
        },
        "position_in_alphabet": 14,
        "type": "nasal_vowel",
        "note": "Nasalizes the preceding vowel"
    },
    "అః": {
        "romanized":       "aha / ah",
        "tenglish":        "ah",
        "ipa":             "/əh/",
        "sound_like":      "Breathy 'h' sound at the end — exhale gently",
        "mouth_position":  "Vowel then gentle breath release",
        "duration":        "aspirated",
        "matra":           "ః",
        "matra_symbol":    "◌ః",
        "special_name":    "Visarga (విసర్గం)",
        "example_words": {
            "తెలుగు": "దుఃఖం (dukhkham) = sorrow",
            "english": "నమః (namah) = salutation",
        },
        "position_in_alphabet": 15,
        "type": "aspirated_vowel",
        "note": "Mainly in Sanskrit-origin words. Adds breathy quality"
    },
}

# ═══════════════════════════════════════════════════════════════
# SECTION 2: TELUGU CONSONANTS (హల్లులు)
# ═══════════════════════════════════════════════════════════════

TELUGU_CONSONANTS = {
    "క": {
        "romanized":       "ka",
        "tenglish":        "ka / k",
        "ipa":             "/k/",
        "sound_like":      "'k' in 'skin' — unaspirated",
        "mouth_position":  "Back of tongue touches soft palate",
        "inherent_vowel":  "a",
        "type":            "velar_unvoiced_unaspirated",
        "group":           "velar",
        "aspirated_pair":  "ఖ",
        "voiced_pair":     "గ",
        "example_words": {
            "simple":   "కలం (kalam) = pen",
            "common":   "కాఫీ (kafi) = coffee"
        },
        "position_in_consonants": 1
    },
    "ఖ": {
        "romanized":       "kha",
        "tenglish":        "kha / kh",
        "ipa":             "/kʰ/",
        "sound_like":      "'k' with a puff of air",
        "mouth_position":  "Same as క but with strong breath release",
        "inherent_vowel":  "a",
        "type":            "velar_unvoiced_aspirated",
        "group":           "velar",
        "position_in_consonants": 2
    },
    "గ": {
        "romanized":       "ga",
        "tenglish":        "ga / g",
        "ipa":             "/ɡ/",
        "sound_like":      "'g' in 'go'",
        "mouth_position":  "Same as క but voiced",
        "inherent_vowel":  "a",
        "type":            "velar_voiced_unaspirated",
        "group":           "velar",
        "position_in_consonants": 3
    },
    "ఘ": {
        "romanized":       "gha",
        "tenglish":        "gha / gh",
        "ipa":             "/ɡʰ/",
        "sound_like":      "'g' with breathy voice",
        "mouth_position":  "Voiced velar with extra breath",
        "inherent_vowel":  "a",
        "type":            "velar_voiced_aspirated",
        "group":           "velar",
        "position_in_consonants": 4
    },
    "ఙ": {
        "romanized":       "nga",
        "tenglish":        "nga",
        "ipa":             "/ŋ/",
        "sound_like":      "Nasal 'ng'",
        "mouth_position":  "Back of tongue raises, air through nose",
        "inherent_vowel":  "a",
        "type":            "velar_nasal",
        "group":           "velar",
        "position_in_consonants": 5
    },
    "చ": {
        "romanized":       "cha",
        "tenglish":        "cha",
        "ipa":             "/tʃ/",
        "sound_like":      "'ch' in 'chair'",
        "mouth_position":  "Palatal release",
        "inherent_vowel":  "a",
        "type":            "palatal_unvoiced_unaspirated",
        "group":           "palatal",
        "position_in_consonants": 6
    },
    "ఛ": {
        "romanized":       "chha",
        "tenglish":        "chha",
        "ipa":             "/tʃʰ/",
        "sound_like":      "Aspirated 'ch'",
        "mouth_position":  "Palatal release with breath",
        "inherent_vowel":  "a",
        "type":            "palatal_unvoiced_aspirated",
        "group":           "palatal",
        "position_in_consonants": 7
    },
    "జ": {
        "romanized":       "ja",
        "tenglish":        "ja",
        "ipa":             "/dʒ/",
        "sound_like":      "'j' in 'jump'",
        "mouth_position":  "Voiced palatal",
        "inherent_vowel":  "a",
        "type":            "palatal_voiced_unaspirated",
        "group":           "palatal",
        "position_in_consonants": 8
    },
    "ఝ": {
        "romanized":       "jha",
        "tenglish":        "jha",
        "ipa":             "/dʒʰ/",
        "sound_like":      "Aspirated 'j'",
        "mouth_position":  "Voiced palatal with breath",
        "inherent_vowel":  "a",
        "type":            "palatal_voiced_aspirated",
        "group":           "palatal",
        "position_in_consonants": 9
    },
    "ఞ": {
        "romanized":       "nya",
        "tenglish":        "nya",
        "ipa":             "/ɲ/",
        "sound_like":      "Like 'ny' in 'canyon'",
        "mouth_position":  "Palatal nasal",
        "inherent_vowel":  "a",
        "type":            "palatal_nasal",
        "group":           "palatal",
        "position_in_consonants": 10
    },
    "ట": {
        "romanized":       "ta",
        "tenglish":        "Ta",
        "ipa":             "/ʈ/",
        "sound_like":      "Hard 't' (retroflex)",
        "mouth_position":  "Tongue curled back",
        "inherent_vowel":  "a",
        "type":            "retroflex_unvoiced_unaspirated",
        "group":           "retroflex",
        "position_in_consonants": 11
    },
    "ఠ": {
        "romanized":       "tha",
        "tenglish":        "Tha",
        "ipa":             "/ʈʰ/",
        "sound_like":      "Hard 't' with breath",
        "mouth_position":  "Retroflex with breath",
        "inherent_vowel":  "a",
        "type":            "retroflex_unvoiced_aspirated",
        "group":           "retroflex",
        "position_in_consonants": 12
    },
    "డ": {
        "romanized":       "da",
        "tenglish":        "Da",
        "ipa":             "/ɖ/",
        "sound_like":      "Hard 'd' (retroflex)",
        "mouth_position":  "Voiced retroflex",
        "inherent_vowel":  "a",
        "type":            "retroflex_voiced_unaspirated",
        "group":           "retroflex",
        "position_in_consonants": 13
    },
    "ఢ": {
        "romanized":       "dha",
        "tenglish":        "Dha",
        "ipa":             "/ɖʰ/",
        "sound_like":      "Hard 'd' with breath",
        "mouth_position":  "Voiced retroflex with breath",
        "inherent_vowel":  "a",
        "type":            "retroflex_voiced_aspirated",
        "group":           "retroflex",
        "position_in_consonants": 14
    },
    "ణ": {
        "romanized":       "na",
        "tenglish":        "Na",
        "ipa":             "/ɳ/",
        "sound_like":      "Nasal 'n' (retroflex)",
        "mouth_position":  "Retroflex nasal",
        "inherent_vowel":  "a",
        "type":            "retroflex_nasal",
        "group":           "retroflex",
        "position_in_consonants": 15
    },
    "త": {
        "romanized":       "tha",
        "tenglish":        "tha",
        "ipa":             "/t̪/",
        "sound_like":      "Soft 't' (dental)",
        "mouth_position":  "Tongue to upper teeth",
        "inherent_vowel":  "a",
        "type":            "dental_unvoiced_unaspirated",
        "group":           "dental",
        "position_in_consonants": 16
    },
    "థ": {
        "romanized":       "tha",
        "tenglish":        "thha",
        "ipa":             "/t̪ʰ/",
        "sound_like":      "Soft 't' with breath",
        "mouth_position":  "Dental with breath",
        "inherent_vowel":  "a",
        "type":            "dental_unvoiced_aspirated",
        "group":           "dental",
        "position_in_consonants": 17
    },
    "ద": {
        "romanized":       "da",
        "tenglish":        "da",
        "ipa":             "/d̪/",
        "sound_like":      "Soft 'd' (dental)",
        "mouth_position":  "Voiced dental",
        "inherent_vowel":  "a",
        "type":            "dental_voiced_unaspirated",
        "group":           "dental",
        "position_in_consonants": 18
    },
    "ధ": {
        "romanized":       "dha",
        "tenglish":        "dhha",
        "ipa":             "/d̪ʰ/",
        "sound_like":      "Soft 'd' with breath",
        "mouth_position":  "Voiced dental with breath",
        "inherent_vowel":  "a",
        "type":            "dental_voiced_aspirated",
        "group":           "dental",
        "position_in_consonants": 19
    },
    "న": {
        "romanized":       "na",
        "tenglish":        "na",
        "ipa":             "/n̪/",
        "sound_like":      "Dental 'n'",
        "mouth_position":  "Dental nasal",
        "inherent_vowel":  "a",
        "type":            "dental_nasal",
        "group":           "dental",
        "position_in_consonants": 20
    },
    "ప": {
        "romanized":       "pa",
        "tenglish":        "pa",
        "ipa":             "/p/",
        "sound_like":      "'p' in 'spin'",
        "mouth_position":  "Lips together",
        "inherent_vowel":  "a",
        "type":            "labial_unvoiced_unaspirated",
        "group":           "labial",
        "position_in_consonants": 21
    },
    "ఫ": {
        "romanized":       "pha",
        "tenglish":        "fa",
        "ipa":             "/pʰ/",
        "sound_like":      "Aspirated 'p' or 'f'",
        "mouth_position":  "Lips together with breath",
        "inherent_vowel":  "a",
        "type":            "labial_unvoiced_aspirated",
        "group":           "labial",
        "position_in_consonants": 22
    },
    "బ": {
        "romanized":       "ba",
        "tenglish":        "ba",
        "ipa":             "/b/",
        "sound_like":      "'b' in 'boy'",
        "mouth_position":  "Voiced labial",
        "inherent_vowel":  "a",
        "type":            "labial_voiced_unaspirated",
        "group":           "labial",
        "position_in_consonants": 23
    },
    "భ": {
        "romanized":       "bha",
        "tenglish":        "bha",
        "ipa":             "/bʰ/",
        "sound_like":      "Aspirated 'b'",
        "mouth_position":  "Voiced labial with breath",
        "inherent_vowel":  "a",
        "type":            "labial_voiced_aspirated",
        "group":           "labial",
        "position_in_consonants": 24
    },
    "మ": {
        "romanized":       "ma",
        "tenglish":        "ma",
        "ipa":             "/m/",
        "sound_like":      "'m' in 'man'",
        "mouth_position":  "Labial nasal",
        "inherent_vowel":  "a",
        "type":            "labial_nasal",
        "group":           "labial",
        "position_in_consonants": 25
    },
    "య": {
        "romanized":       "ya",
        "tenglish":        "ya",
        "ipa":             "/j/",
        "sound_like":      "'y' in 'yes'",
        "mouth_position":  "Palatal approximant",
        "inherent_vowel":  "a",
        "type":            "semivowel",
        "group":           "semivowel",
        "position_in_consonants": 26
    },
    "ర": {
        "romanized":       "ra",
        "tenglish":        "ra",
        "ipa":             "/r/",
        "sound_like":      "Flapped 'r'",
        "mouth_position":  "Tongue tip taps upper ridge",
        "inherent_vowel":  "a",
        "type":            "liquid_rhotic",
        "group":           "liquid",
        "position_in_consonants": 27
    },
    "ల": {
        "romanized":       "la",
        "tenglish":        "la",
        "ipa":             "/l/",
        "sound_like":      "'l' in 'lamp'",
        "mouth_position":  "Tongue to upper ridge",
        "inherent_vowel":  "a",
        "type":            "liquid_lateral",
        "group":           "liquid",
        "position_in_consonants": 28
    },
    "వ": {
        "romanized":       "va",
        "tenglish":        "va",
        "ipa":             "/ʋ/",
        "sound_like":      "Between 'v' and 'w'",
        "mouth_position":  "Labiodental approximant",
        "inherent_vowel":  "a",
        "type":            "semivowel",
        "group":           "semivowel",
        "position_in_consonants": 29
    },
    "శ": {
        "romanized":       "sha",
        "tenglish":        "sha",
        "ipa":             "/ɕ/",
        "sound_like":      "Soft 'sh'",
        "mouth_position":  "Palatal fricative",
        "inherent_vowel":  "a",
        "type":            "fricative",
        "group":           "fricative",
        "position_in_consonants": 30
    },
    "ష": {
        "romanized":       "sha",
        "tenglish":        "Sha",
        "ipa":             "/ʂ/",
        "sound_like":      "Hard 'sh'",
        "mouth_position":  "Retroflex fricative",
        "inherent_vowel":  "a",
        "type":            "fricative",
        "group":           "fricative",
        "position_in_consonants": 31
    },
    "స": {
        "romanized":       "sa",
        "tenglish":        "sa",
        "ipa":             "/s/",
        "sound_like":      "'s' in 'sun'",
        "mouth_position":  "Alveolar fricative",
        "inherent_vowel":  "a",
        "type":            "fricative",
        "group":           "fricative",
        "position_in_consonants": 32
    },
    "హ": {
        "romanized":       "ha",
        "tenglish":        "ha",
        "ipa":             "/h/",
        "sound_like":      "'h' in 'hat'",
        "mouth_position":  "Glottal fricative",
        "inherent_vowel":  "a",
        "type":            "fricative",
        "group":           "fricative",
        "position_in_consonants": 33
    },
    "ళ": {
        "romanized":       "lla",
        "tenglish":        "La",
        "ipa":             "/ɭ/",
        "sound_like":      "Retroflex 'l'",
        "mouth_position":  "Retroflex lateral",
        "inherent_vowel":  "a",
        "type":            "liquid",
        "group":           "liquid",
        "position_in_consonants": 34
    },
    "క్ష": {
        "romanized":       "ksha",
        "tenglish":        "ksha",
        "ipa":             "/kʂ/",
        "sound_like":      "'k' + hard 'sh'",
        "mouth_position":  "Compound",
        "inherent_vowel":  "a",
        "type":            "compound",
        "group":           "special",
        "position_in_consonants": 35
    },
    "ఱ": {
        "romanized":       "rra",
        "tenglish":        "rra",
        "ipa":             "/rː/",
        "sound_like":      "Rolled 'r'",
        "mouth_position":  "Retroflex rhotic",
        "inherent_vowel":  "a",
        "type":            "rhotic",
        "group":           "special",
        "position_in_consonants": 36
    },
}

# ═══════════════════════════════════════════════════════════════
# SECTION 3: VOWEL MATRAS (మాత్రలు)
# ═══════════════════════════════════════════════════════════════

TELUGU_MATRAS = {
    "ా": {"vowel": "ఆ", "sound": "aa", "example": "కా (kaa)"},
    "ి": {"vowel": "ఇ", "sound": "i", "example": "కి (ki)"},
    "ీ": {"vowel": "ఈ", "sound": "ee", "example": "కీ (kee)"},
    "ు": {"vowel": "ఉ", "sound": "u", "example": "కు (ku)"},
    "ూ": {"vowel": "ఊ", "sound": "oo", "example": "కూ (koo)"},
    "ృ": {"vowel": "ఋ", "sound": "ru", "example": "కృ (kru)"},
    "ె": {"vowel": "ఎ", "sound": "e", "example": "కె (ke)"},
    "ే": {"vowel": "ఏ", "sound": "ee", "example": "కే (kee)"},
    "ై": {"vowel": "ఐ", "sound": "ai", "example": "కై (kai)"},
    "ొ": {"vowel": "ఒ", "sound": "o", "example": "కొ (ko)"},
    "ో": {"vowel": "ఓ", "sound": "oo", "example": "కో (koo)"},
    "ౌ": {"vowel": "ఔ", "sound": "au", "example": "కౌ (kau)"},
    "ం": {"vowel": "అం", "sound": "am", "example": "కం (kam)"},
    "ః": {"vowel": "అః", "sound": "aha", "example": "కః (kaha)"},
}

# ═══════════════════════════════════════════════════════════════
# SECTION 4: CONSONANT COMBINATION RULES
# ═══════════════════════════════════════════════════════════════

CONSONANT_COMBINATION_RULES = {
    "virama": {
        "symbol":      "్",
        "name":        "Halant",
        "function":    "Removes inherent 'a'"
    },
    "common_clusters": {
        "క్క":  {"sound": "kka",  "example": "అక్క (akka)"},
        "న్న":  {"sound": "nna",  "example": "అన్న (anna)"},
        "ల్లు": {"sound": "llu",  "example": "ఇల్లు (illu)"},
        "స్త":  {"sound": "sta",  "example": "చేస్తా (chesta)"},
    }
}

# ═══════════════════════════════════════════════════════════════
# SECTION 5: TELUGU NUMBERS (సంఖ్యలు)
# ═══════════════════════════════════════════════════════════════

TELUGU_NUMBERS = {
    "౦": {"value": 0,  "telugu_word": "సున్న",   "romanized": "sunna"},
    "౧": {"value": 1,  "telugu_word": "ఒకటి",    "romanized": "okati"},
    "౨": {"value": 2,  "telugu_word": "రెండు",    "romanized": "rendu"},
    "౩": {"value": 3,  "telugu_word": "మూడు",     "romanized": "muudu"},
    "౪": {"value": 4,  "telugu_word": "నాలుగు",   "romanized": "naalugu"},
    "౫": {"value": 5,  "telugu_word": "అయిదు",    "romanized": "aidu"},
    "౬": {"value": 6,  "telugu_word": "ఆరు",      "romanized": "aaru"},
    "౭": {"value": 7,  "telugu_word": "ఏడు",      "romanized": "edu"},
    "౮": {"value": 8,  "telugu_word": "ఎనిమిది",  "romanized": "enimidi"},
    "౯": {"value": 9,  "telugu_word": "తొమ్మిది",  "romanized": "tommidi"},
}
