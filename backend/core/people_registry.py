"""
People Registry — The living memory of every person the user knows.
Vera uses this to determine how every agent should speak.
"""

import json
import sqlite3
import os
import functools
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from config.settings import DB_PATH

# ── Relationship Tiers ────────────────────────────────────────────────────────
RELATIONSHIP_TIERS = {
    # FAMILY - ELDERS
    "grandparent":      {"respect": 1.0, "formality": 0.95, "tone": "very_gentle_respectful",    "language": "simple_warm"},
    "parent":           {"respect": 0.98,"formality": 0.85, "tone": "loving_respectful",          "language": "warm_clear"},
    "annaya":           {"respect": 0.90,"formality": 0.65, "tone": "warm_respectful_brotherly",  "language": "natural_affectionate"},
    "akka":             {"respect": 0.90,"formality": 0.65, "tone": "warm_respectful_sisterly",   "language": "natural_affectionate"},
    "elder_relative":   {"respect": 0.92,"formality": 0.80, "tone": "respectful_caring",          "language": "simple_polite"},

    # FAMILY - PEERS/YOUNGER
    "younger_sibling":  {"respect": 0.70,"formality": 0.30, "tone": "nurturing_playful",          "language": "simple_encouraging"},
    "cousin_peer":      {"respect": 0.65,"formality": 0.25, "tone": "casual_friendly",            "language": "natural_relaxed"},
    "child_family":     {"respect": 0.60,"formality": 0.10, "tone": "gentle_encouraging",         "language": "very_simple_safe"},

    # AUTHORITY
    "teacher":          {"respect": 0.97,"formality": 0.95, "tone": "formal_humble_eager",        "language": "clear_academic"},
    "professor":        {"respect": 0.98,"formality": 0.98, "tone": "academic_respectful",        "language": "precise_formal"},
    "boss":             {"respect": 0.90,"formality": 0.90, "tone": "professional_clear",         "language": "structured_concise"},
    "elder_community":  {"respect": 0.95,"formality": 0.85, "tone": "deferential_patient",        "language": "simple_honorific"},
    "doctor":           {"respect": 0.95,"formality": 0.92, "tone": "respectful_cooperative",     "language": "clear_honest"},

    # PEERS
    "close_friend":     {"respect": 0.60,"formality": 0.10, "tone": "casual_warm_humorous",       "language": "natural_slang_ok"},
    "classmate":        {"respect": 0.60,"formality": 0.30, "tone": "casual_collaborative",       "language": "natural_relaxed"},
    "colleague":        {"respect": 0.70,"formality": 0.60, "tone": "professional_friendly",      "language": "semi_formal"},
    "acquaintance":     {"respect": 0.75,"formality": 0.70, "tone": "polite_neutral",             "language": "standard_polite"},

    # SPECIAL CONTEXTS
    "child_student":    {"respect": 0.65,"formality": 0.20, "tone": "patient_encouraging_simple", "language": "very_simple_visual"},
    "elderly_ill":      {"respect": 1.0, "formality": 0.80, "tone": "very_gentle_slow_patient",   "language": "very_simple_loud_clear"},
    "anxious_person":   {"respect": 0.80,"formality": 0.50, "tone": "calm_slow_reassuring",       "language": "simple_safe_grounding"},
    "stranger":         {"respect": 0.80,"formality": 0.80, "tone": "polite_neutral_safe",        "language": "standard_clear"},
}

# ── Person Data Model ─────────────────────────────────────────────────────────
@dataclass
class Person:
    name: str
    nickname: str
    relationship_type: str          # Must match RELATIONSHIP_TIERS key
    age_group: str                  # "child" | "teen" | "young_adult" | "adult" | "elder"
    emotional_state: str            # Updated dynamically: "happy"|"upset"|"stressed"|"neutral"
    preferred_language: str         # "english" | "telugu" | "hindi" | "mixed"
    topics_they_care_about: list    # ["cricket", "studies", "health"]
    topics_to_avoid: list           # ["money", "past mistakes"]
    how_they_prefer_to_be_helped: str  # "direct_advice"|"just_listen"|"ask_questions"
    last_interaction: str
    notes: str                      # Special notes: "hard of hearing", "gets angry fast"
    respect_level_required: float   # Overrides tier default if set

    def get_tone_profile(self) -> dict:
        """Get the complete communication profile for this person."""
        base = RELATIONSHIP_TIERS.get(
            self.relationship_type,
            RELATIONSHIP_TIERS["acquaintance"]
        ).copy()
        
        # Override with age-group adjustments
        if self.age_group == "child":
            base["language"] = "very_simple_encouraging"
            base["tone"]     = "gentle_playful_safe"
        elif self.age_group == "elder":
            base["formality"] = min(base["formality"] + 0.1, 1.0)
            base["tone"]      = f"patient_{base['tone']}"

        # Override with emotional state
        if self.emotional_state == "upset":
            base["tone"] = f"calming_{base['tone']}"
        elif self.emotional_state == "stressed":
            base["tone"] = f"reassuring_{base['tone']}"
        
        # Override respect if specified
        if self.respect_level_required > 0:
            base["respect"] = self.respect_level_required

        return base


# ── Registry Manager ──────────────────────────────────────────────────────────
class PeopleRegistry:
    """Manages all people the user knows. Vera's brain."""

    _schema_verified = False

    def __init__(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        if not PeopleRegistry._schema_verified:
            self._ensure_table()
            PeopleRegistry._schema_verified = True

    def _ensure_table(self):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS people_registry (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    name            TEXT NOT NULL,
                    nickname        TEXT,
                    relationship_type TEXT NOT NULL,
                    age_group       TEXT DEFAULT 'adult',
                    emotional_state TEXT DEFAULT 'neutral',
                    preferred_language TEXT DEFAULT 'english',
                    topics_care     TEXT DEFAULT '[]',
                    topics_avoid    TEXT DEFAULT '[]',
                    help_style      TEXT DEFAULT 'direct_advice',
                    last_interaction TEXT,
                    notes           TEXT DEFAULT '',
                    respect_override REAL DEFAULT 0.0,
                    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Every social interaction logged
            conn.execute("""
                CREATE TABLE IF NOT EXISTS social_interactions (
                    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                    person_name         TEXT,
                    relationship_type   TEXT,
                    context             TEXT,
                    tone_used           TEXT,
                    respect_score       REAL,
                    outcome             TEXT,   -- 'positive'|'neutral'|'negative'
                    lesson_learned      TEXT,
                    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Vera's daily relationship health report
            conn.execute("""
                CREATE TABLE IF NOT EXISTS relationship_health (
                    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                    person_name         TEXT,
                    health_score        REAL,   -- 0-1, based on recent interactions
                    suggested_action    TEXT,   -- "You haven't spoken to Annaya in 3 days"
                    recorded_at         DATE DEFAULT (date('now'))
                )
            """)

    def add_person(self, person: Person):
        """Add or update a person in the registry."""
        # Clear cache to ensure consistency
        PeopleRegistry._get_person_cached.cache_clear()

        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO people_registry
                (name, nickname, relationship_type, age_group, emotional_state,
                 preferred_language, topics_care, topics_avoid, help_style,
                 last_interaction, notes, respect_override, updated_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                person.name, person.nickname, person.relationship_type,
                person.age_group, person.emotional_state, person.preferred_language,
                json.dumps(person.topics_they_care_about),
                json.dumps(person.topics_to_avoid),
                person.how_they_prefer_to_be_helped,
                person.last_interaction, person.notes,
                person.respect_level_required,
                datetime.now().isoformat()
            ))

    def get_person(self, name_or_nickname: str) -> Person | None:
        """Fetch a person by name or nickname."""
        return PeopleRegistry._get_person_cached(name_or_nickname)

    @staticmethod
    @functools.lru_cache(maxsize=128)
    def _get_person_cached(name_or_nickname: str) -> Person | None:
        with sqlite3.connect(DB_PATH) as conn:
            row = conn.execute(
                "SELECT * FROM people_registry WHERE name LIKE ? OR nickname LIKE ?",
                (f"%{name_or_nickname}%", f"%{name_or_nickname}%")
            ).fetchone()
        if not row:
            return None
        return PeopleRegistry._static_row_to_person(row)

    def update_emotional_state(self, name: str, state: str):
        """Real-time update when user says 'Annaya is upset'."""
        # Clear cache to ensure consistency
        PeopleRegistry._get_person_cached.cache_clear()

        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "UPDATE people_registry SET emotional_state=?, updated_at=? WHERE name LIKE ?",
                (state, datetime.now().isoformat(), f"%{name}%")
            )

    def get_all_people(self) -> list[Person]:
        with sqlite3.connect(DB_PATH) as conn:
            rows = conn.execute("SELECT * FROM people_registry").fetchall()
        return [PeopleRegistry._static_row_to_person(r) for r in rows]

    def _row_to_person(self, row) -> Person:
        return PeopleRegistry._static_row_to_person(row)

    @staticmethod
    def _static_row_to_person(row) -> Person:
        return Person(
            name=row[1], nickname=row[2], relationship_type=row[3],
            age_group=row[4], emotional_state=row[5], preferred_language=row[6],
            topics_they_care_about=json.loads(row[7]),
            topics_to_avoid=json.loads(row[8]),
            how_they_prefer_to_be_helped=row[9],
            last_interaction=row[10], notes=row[11],
            respect_level_required=row[12]
        )
