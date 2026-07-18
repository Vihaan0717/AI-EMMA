"""
Memory Learner — ARION's Organic Brain Growth.

Passively listens to every owner message.
Extracts facts. Tracks confidence. Builds a living profile.
Learns like a friend — through time and attention.
Never asks a form. Never guesses. Only uses what it knows.
"""

import json
import re
import asyncio
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    import aiohttp
except ImportError:
    aiohttp = None


class MemoryLearner:

    CONFIDENCE_THRESHOLD_TO_USE = 0.60  # Must be this sure to use in prompts
    CONFIDENCE_CURVE = {                 # mentions → confidence
        1: 0.25, 2: 0.45, 3: 0.60,
        4: 0.72, 5: 0.82, 7: 0.90, 10: 0.95
    }

    # ── Extraction Patterns ──────────────────────────────────────────────────
    # (category.subcategory, regex, extracted_meaning)
    EXTRACTION_PATTERNS = [

        # ── Family ───────────────────────────────────────────────────────────
        (r"\b(amma|mom|mother)\b.{0,30}(called|messaged|said|told|asked|coming|sick|okay|fine|home)",
         "family.mother", "mentioned and active in owner's life"),
        (r"\b(nanna|dad|father)\b.{0,30}(called|said|told|angry|okay|fine|sick)",
         "family.father", "exists and in contact"),
        (r"\b(akka|sister|chelli)\b.{0,30}(said|okay|happy|sad|college|studying|working)",
         "family.sister", "exists, part of life"),
        (r"\b(anna|brother|tammudu)\b.{0,30}(said|okay|called|told)",
         "family.brother", "exists"),
        (r"\bfamily\b.{0,20}(okay|fine|good|well)",
         "family.general_status", "family is doing okay"),

        # ── Location ─────────────────────────────────────────────────────────
        (r"\b(in|at|from|reached|back in)\s+(hyderabad|hyd)\b",
         "location.cities_visited", "spends time in Hyderabad"),
        (r"\b(in|at|from|reached|back in)\s+(bangalore|blr|bengaluru)\b",
         "location.cities_visited", "spends time in Bangalore"),
        (r"\b(in|at|from|reached|back in)\s+(rajahmundry|rajam)\b",
         "location.home_city", "home city likely Rajahmundry"),
        (r"\b(in|at|from|reached|back in)\s+(vizag|visakhapatnam)\b",
         "location.cities_visited", "spends time in Vizag"),
        (r"\bgoing home\b|\bback home\b",
         "location.has_hometown", "travels back to hometown"),

        # ── Work ─────────────────────────────────────────────────────────────
        (r"\b(office|work|meeting|standup|client|project|deadline|sprint)\b",
         "work.currently_employed", "actively working"),
        (r"\b(wfh|work from home|working from home)\b",
         "work.style", "has WFH capability"),
        (r"\b(hate|tired of|bored of|frustrated with).{0,15}(work|office|project|meetings)\b",
         "work.stress_level", "work causes stress"),
        (r"\b(new project|new job|joined|switched|got a job)\b",
         "work.career_event", "career change or new role"),
        (r"\b(tech|software|coding|developer|engineer|it job|startup)\b",
         "work.field", "works in tech/software"),
        (r"\b(weekend off|sunday off|holiday|leave today)\b",
         "work.schedule", "has days off from work"),

        # ── Health ───────────────────────────────────────────────────────────
        (r"\b(sick|fever|cold|headache|vomiting|not well|ill|body ache)\b",
         "health.current", "currently unwell"),
        (r"\b(better now|recovered|feeling good|healthy now)\b",
         "health.current", "recovered / currently healthy"),
        (r"\b(gym|workout|exercise|run|jogging|yoga|walked)\b",
         "health.fitness", "exercises regularly"),
        (r"\b(no sleep|didn't sleep|couldn't sleep|insomnia|3am|4am still awake)\b",
         "health.sleep", "has sleep issues"),
        (r"\b(slept well|good sleep|woke up fresh)\b",
         "health.sleep", "sleeps okay when relaxed"),

        # ── Mood & Emotional Patterns ─────────────────────────────────────────
        (r"\b(hate|can't stand|pisses me off|so annoying|irritating)\b",
         "personality.pet_peeves", "has strong dislikes"),
        (r"\b(love|adore|obsessed with|can't live without|favorite|fav)\b",
         "personality.loves", "has strong preferences"),
        (r"\b(anxious|overthinking|stressed|pressure|tension)\b",
         "personality.stress_style", "internalizes stress"),
        (r"\b(haha|lmao|lol|😂|🤣|funny ra|hilarious|scene ra)\b",
         "personality.humor", "has active sense of humor"),
        (r"\b(sad|depressed|low|down|bore|empty|lonely)\b",
         "mood.negative_triggers", "experiences low moods"),
        (r"\b(happy|excited|mast|kiraak|bagunna|feeling good)\b",
         "mood.positive_triggers", "experiences high moments"),

        # ── Daily Routine ─────────────────────────────────────────────────────
        (r"\b(woke up|just woke|morning ra|good morning)\b",
         "routine.morning_active", "communicates in mornings"),
        (r"\b(late night|1am|2am|3am|can't sleep|still up)\b",
         "routine.night_owl", "stays up late"),
        (r"\b(lunch|eating|food|tiffin|dinner|breakfast)\b",
         "routine.meal_mentions", "mentions meals in conversation"),

        # ── Relationships ─────────────────────────────────────────────────────
        (r"\b(my friend|best friend|my bro|my guy|close friend)\b",
         "relationships.has_close_friends", "has close friends"),
        (r"\b(she is|my girl|girlfriend|gf|gf ra)\b",
         "relationships.romantic", "may have romantic relationship"),
        (r"\b(he is|boyfriend|bf)\b",
         "relationships.romantic", "may have romantic relationship"),
        (r"\b(miss him|miss her|miss them|been a while since)\b",
         "relationships.misses_people", "emotionally attached to others"),

        # ── Interests & Hobbies ───────────────────────────────────────────────
        (r"\b(playing|game|gaming|pubg|bgmi|valorant|chess|cricket|football)\b",
         "interests.gaming_sports", "plays games or sports"),
        (r"\b(music|song|playlist|singer|artist|album|spotify)\b",
         "interests.music", "interested in music"),
        (r"\b(movie|film|series|netflix|amazon|ott|watched)\b",
         "interests.entertainment", "watches movies/shows"),
        (r"\b(reading|book|novel|manga|article)\b",
         "interests.reading", "reads occasionally"),
        (r"\b(food|eating out|restaurant|hotel|biriyani|pizza|coffee)\b",
         "interests.food", "enjoys food experiences"),

        # ── Goals & Ambitions ─────────────────────────────────────────────────
        (r"\b(want to|planning to|goal|dream|trying to|learning|studying)\b",
         "goals.active_aspirations", "has active goals or learning"),
        (r"\b(business|startup|my own|freelance|side project)\b",
         "goals.entrepreneurial", "has entrepreneurial interest"),
        (r"\b(abroad|usa|uk|canada|visa|passport|migrate|move to)\b",
         "goals.abroad_plans", "considering moving abroad"),

        # ── Communication Style ───────────────────────────────────────────────
        (r"\b(ra|da|bhai|bro|mama|mowa)\b",
         "style.uses_regional_fillers", "uses Telugu/regional fillers naturally"),
        (r"😂|🤣|😎|🔥|💀|😅|🙏",
         "style.uses_emojis", "uses emojis in conversation"),
    ]

    def __init__(
        self,
        profile_path: str = "arion/memory/owner_learned_profile.json",
        ollama_url: str = "http://localhost:11434",
        model: str = "qwen2.5-coder:7b"
    ):
        self.profile_path = profile_path
        self.ollama_url = ollama_url
        self.model = model
        self.profile = self._load_profile()
        print(
            f"[MemoryLearner] Loaded profile. "
            f"Known facts: {self._count_facts()}", flush=True
        )

    # ── Main Entry ───────────────────────────────────────────────────────────

    async def process_owner_message(
        self, text: str, semantic_english: str
    ) -> list[str]:
        """
        Called on every owner message.
        Extracts facts. Updates confidence. Returns list of new learnings.
        """
        new_learnings = []
        check_text = (text + " " + semantic_english).lower()

        # 1. Regex-based pattern extraction (fast, always runs)
        for pattern, fact_path, fact_value in self.EXTRACTION_PATTERNS:
            if re.search(pattern, check_text, re.IGNORECASE):
                print(f"[MemoryLearner] Pattern matched: '{pattern}' -> {fact_path}", flush=True)
                updated = self._update_fact(fact_path, fact_value, text)
                if updated:
                    new_learnings.append(f"{fact_path} = {fact_value}")

        # 2. LLM-based deep extraction (for longer, complex messages)
        if len(semantic_english.split()) > 6 and aiohttp:
            llm_facts = await self._llm_extract_insights(semantic_english)
            for path, value in llm_facts.items():
                updated = self._update_fact(path, value, semantic_english)
                if updated:
                    new_learnings.append(f"{path} = {value}")

        # 3. Update conversation count
        self.profile["meta"]["total_conversations"] = \
            self.profile["meta"].get("total_conversations", 0) + 1
        self.profile["meta"]["last_updated"] = datetime.now().isoformat()

        if new_learnings:
            self._save_profile()
            for item in new_learnings:
                print(f"[MemoryLearner] 🧠 Learned: {item}", flush=True)

        return new_learnings

    # ── Context Retrieval ─────────────────────────────────────────────────────

    def get_relevant_context(self, semantic_english: str) -> str:
        """
        Returns only HIGH CONFIDENCE facts relevant to this message.
        Used by Orchestrator to inject into system prompt.
        """
        relevant = []
        sem = semantic_english.lower()

        topic_map = {
            "family": ["family", "amma", "mom", "mother", "nanna", "dad",
                       "sister", "akka", "brother", "anna"],
            "work":   ["work", "office", "project", "job", "busy", "meeting",
                       "deadline", "client"],
            "health": ["health", "sick", "tired", "sleep", "gym",
                       "fever", "not well", "feeling"],
            "location": ["where", "place", "city", "home", "there"],
            "mood":   ["mood", "sad", "happy", "stressed", "okay", "feeling",
                       "excited", "bored"],
            "interests": ["game", "music", "movie", "food", "reading",
                          "watching", "playing"],
            "goals":  ["plan", "want", "goal", "trying", "learning",
                       "dream", "future"]
        }

        triggered_categories = set()
        for category, keywords in topic_map.items():
            if any(kw in sem for kw in keywords):
                triggered_categories.add(category)

        # Extract high-confidence facts from triggered categories
        for category in triggered_categories:
            cat_data = self.profile.get(category, {})
            for key, data in cat_data.items():
                if not isinstance(data, dict):
                    continue
                conf = data.get("confidence", 0)
                if conf >= self.CONFIDENCE_THRESHOLD_TO_USE:
                    relevant.append(
                        f"[KNOWN | conf={conf}] "
                        f"{category}.{key}: {data.get('value', 'noted')}"
                        f"{' — ' + data['notes'] if data.get('notes') else ''}"
                    )

        # Always append unknowns to prevent hallucination
        unknowns = self._get_unknowns(triggered_categories)
        if unknowns:
            relevant.append(
                f"[UNKNOWN — DO NOT GUESS]: {', '.join(unknowns)}"
            )

        return "\n".join(relevant) if relevant else ""

    def get_personality_snapshot(self) -> str:
        """
        Returns a compact personality description for system prompt.
        Only uses high-confidence personality facts.
        """
        parts = []
        personality = self.profile.get("personality", {})
        style = self.profile.get("style", {})
        routine = self.profile.get("routine", {})

        checks = [
            (personality.get("humor", {}), "Has active sense of humor"),
            (personality.get("stress_style", {}), "Internalizes stress"),
            (style.get("uses_regional_fillers", {}), "Speaks with Telugu fillers naturally"),
            (style.get("uses_emojis", {}), "Uses emojis"),
            (routine.get("night_owl", {}), "Tends to stay up late"),
        ]

        for data, description in checks:
            if isinstance(data, dict) and data.get("confidence", 0) >= 0.6:
                parts.append(description)

        return ". ".join(parts) if parts else ""

    # ── Fact Management ───────────────────────────────────────────────────────

    def _update_fact(
        self, path: str, value: str, source_text: str
    ) -> bool:
        """
        Navigates to fact location. Updates confidence. Returns True if upgraded.
        """
        keys = path.split(".")
        node = self.profile

        for key in keys[:-1]:
            if key not in node:
                node[key] = {}
            node = node[key]

        final_key = keys[-1]

        if final_key not in node:
            node[final_key] = {
                "value": value,
                "confidence": self.CONFIDENCE_CURVE[1],
                "mentions": 1,
                "notes": "",
                "first_seen": datetime.now().isoformat(),
                "last_seen": datetime.now().isoformat()
            }
            return True  # New fact

        else:
            existing = node[final_key]
            prev_mentions = existing.get("mentions", 1)
            new_mentions = prev_mentions + 1

            # Find closest confidence from curve
            curve_key = max(
                [k for k in self.CONFIDENCE_CURVE.keys() if k <= new_mentions],
                default=1
            )
            new_confidence = self.CONFIDENCE_CURVE[curve_key]
            prev_confidence = existing.get("confidence", 0)

            existing["mentions"] = new_mentions
            existing["confidence"] = new_confidence
            existing["last_seen"] = datetime.now().isoformat()

            # If value is same, keep. If different, note the variation.
            if existing["value"] != value:
                existing["notes"] = (
                    f"Also seen as: {value}"
                    if not existing["notes"]
                    else existing["notes"]
                )

            # Return True only when crossing confidence threshold
            crossed_threshold = (
                prev_confidence < self.CONFIDENCE_THRESHOLD_TO_USE
                and new_confidence >= self.CONFIDENCE_THRESHOLD_TO_USE
            )
            return crossed_threshold

    def _get_unknowns(self, categories: set) -> list:
        """
        Returns list of things we still don't know about triggered categories.
        """
        unknowns = []
        want_to_know = {
            "family": ["father_status", "family_size"],
            "work":   ["exact_role", "company_name"],
            "health": ["chronic_conditions"],
            "location": ["exact_city"],
            "mood":   ["current_mental_state"],
        }

        for category in categories:
            cat_wants = want_to_know.get(category, [])
            cat_data = self.profile.get(category, {})
            for item in cat_wants:
                existing = cat_data.get(item, {})
                if not existing or existing.get("confidence", 0) < 0.4:
                    unknowns.append(f"{category}.{item}")

        return unknowns[:4]  # Max 4 unknowns at a time

    # ── LLM Deep Extraction ───────────────────────────────────────────────────

    async def _llm_extract_insights(
        self, semantic_english: str
    ) -> dict:
        """
        Uses LLM to extract subtle facts that regex can't catch.
        Returns {fact_path: fact_value} dict.
        """
        prompt_messages = [
            {
                "role": "system",
                "content": (
                    "You extract personal facts from messages. "
                    "Output ONLY valid JSON. Nothing else. No explanation.\n"
                    "Allowed categories: family, work, health, location, "
                    "mood, personality, interests, goals, relationships, style\n"
                    "Format: {\"category.subcategory\": \"fact_value\"}\n"
                    "Example: {\"mood.current\": \"stressed about deadlines\", "
                    "\"interests.music\": \"listens to music when stressed\"}\n"
                    "If no personal facts found: return {}"
                )
            },
            {
                "role": "user",
                "content": f"Extract facts from: \"{semantic_english}\""
            }
        ]

        try:
            timeout = aiohttp.ClientTimeout(total=15)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"{self.ollama_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": prompt_messages,
                        "stream": False,
                        "options": {"temperature": 0.1, "num_predict": 150}
                    }
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        raw = data.get("message", {}).get("content", "{}").strip()

                        # Extract JSON safely
                        json_match = re.search(r'\{[^}]+\}', raw, re.DOTALL)
                        if json_match:
                            extracted = json.loads(json_match.group())
                            # Validate structure
                            valid = {
                                k: v for k, v in extracted.items()
                                if "." in k and isinstance(v, str)
                            }
                            return valid

        except (asyncio.TimeoutError, json.JSONDecodeError, Exception) as e:
            print(f"[MemoryLearner] LLM extraction skipped: {e}", flush=True)

        return {}

    # ── Profile I/O ───────────────────────────────────────────────────────────

    def _load_profile(self) -> dict:
        try:
            with open(self.profile_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(
                "[MemoryLearner] No profile found. "
                "Starting fresh — will learn over time.", flush=True
            )
            return self._empty_profile()
        except Exception as e:
            print(f"[MemoryLearner] Profile load error: {e}", flush=True)
            return self._empty_profile()

    def _save_profile(self):
        Path(self.profile_path).parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.profile_path, "w", encoding="utf-8") as f:
                json.dump(self.profile, f, indent=2, ensure_ascii=False)
            
            # Also sync to Obsidian vault
            self.sync_to_obsidian_vault("arion/vault")
        except Exception as e:
            print(f"[MemoryLearner] Save error: {e}", flush=True)

    def sync_to_obsidian_vault(self, vault_path: str = "arion/vault"):
        """
        Writes the current learned profile as a readable Obsidian markdown file.
        Called after every save.
        """
        try:
            profile_md_path = os.path.join(vault_path, "Memories", "Owner_Profile.md")
            os.makedirs(os.path.dirname(profile_md_path), exist_ok=True)
            
            # Build markdown table from profile
            lines = [
                "---",
                "type: owner_profile",
                "version: organic_learned", 
                f"last_updated: {self.profile['meta'].get('last_updated', 'unknown')}",
                f"total_conversations: {self.profile['meta'].get('total_conversations', 0)}",
                "---\n",
                "# Owner Profile — Learned Organically\n",
                "> Written by ARION through observation. Not filled manually.\n",
            ]
            
            # Write each category
            for category, data in self.profile.items():
                if category == "meta" or not isinstance(data, dict) or not data:
                    continue
                
                lines.append(f"\n## {category.replace('_', ' ').title()}\n")
                lines.append("| Fact | Value | Confidence | Last Seen |")
                lines.append("| --- | --- | --- | --- |")
                
                has_visible_facts = False
                for key, fact in data.items():
                    if not isinstance(fact, dict):
                        continue
                    conf = fact.get("confidence", 0)
                    if conf < 0.2:  # Skip very uncertain facts
                        continue
                    
                    has_visible_facts = True
                    conf_bar = "🟢" if conf >= 0.6 else "🟡" if conf >= 0.4 else "🔴"
                    lines.append(
                        f"| {key} | {fact.get('value', '?')} | "
                        f"{conf_bar} {conf} | {fact.get('last_seen', '?')[:10]} |"
                    )
                if not has_visible_facts:
                    lines.pop(); lines.pop() # Remove header and separator
                    lines.append("*Still learning...*")
            
            with open(profile_md_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            
            print(f"[MemoryLearner] 📝 Vault profile synced -> {profile_md_path}", flush=True)
        except Exception as e:
            print(f"[MemoryLearner] Vault Sync Error: {e}", flush=True)

    def _empty_profile(self) -> dict:
        return {
            "meta": {
                "profile_version": 1,
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "total_conversations": 0,
                "confidence_threshold": self.CONFIDENCE_THRESHOLD_TO_USE
            },
            "identity": {},
            "family": {},
            "work": {},
            "health": {},
            "location": {},
            "mood": {},
            "personality": {},
            "style": {},
            "interests": {},
            "goals": {},
            "relationships": {},
            "routine": {}
        }

    def _count_facts(self) -> int:
        count = 0
        for category, data in self.profile.items():
            if category == "meta":
                continue
            if isinstance(data, dict):
                count += sum(
                    1 for v in data.values()
                    if isinstance(v, dict) and v.get("confidence", 0) >= 0.4
                )
        return count
