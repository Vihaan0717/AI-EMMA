
"""
VaultBrain — Single interface for all vault writes.
Every write produces a named, linked, content-filled file.
No more Index.md. No more empty nodes.
"""

import re
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional


class VaultBrain:

    def __init__(self, vault_path: str = "arion/vault"):
        self.VAULT = Path(vault_path)
        self._ensure_structure()

    # ── WORKING MEMORY — Updates every single message ────────────────

    def update_working_memory(
        self,
        contact: str,
        role: str,
        content: str,
        emotion: str = "",
        topic: str = "general"
    ):
        """
        Real-time conversation buffer.
        Named: "Talking_With_Kannaya_Now.md"
        or: "Owner_Active_Conversation.md"
        """
        is_owner = self._is_owner(contact)
        name = (
            "Owner_Active_Conversation"
            if is_owner
            else f"Talking_With_{self._safe(contact)}_Now"
        )
        path = self.VAULT / "Brain" / "Working" / f"{name}.md"

        # Load existing turns
        turns = []
        if path.exists():
            try:
                raw = path.read_text(encoding="utf-8")
                if "## Live Feed" in raw:
                    turns_raw = raw.split("## Live Feed")[1].strip()
                    turns = [
                        t.strip()
                        for t in turns_raw.split("\n---\n")
                        if t.strip()
                    ]
            except Exception:
                pass

        # Add new turn
        now = datetime.now()
        turn = (
            f"**{role.upper()}** {now.strftime('%H:%M')}"
            f"{' | ' + emotion if emotion else ''}\n"
            f"{content}"
        )
        turns.append(turn)
        turns = turns[-10:]  # Last 10 turns

        person_link = (
            "[[People/Owner/Owner_Profile]]"
            if is_owner
            else f"[[People/Contacts/{self._safe(contact)}/{self._safe(contact)}_Profile]]"
        )

        template = (
            f"---\n"
            f"type: working_memory\n"
            f"contact: {contact}\n"
            f"topic: {topic}\n"
            f"emotion: {emotion}\n"
            f"updated: {now.isoformat()}\n"
            f"---\n\n"
            f"# {'Owner' if is_owner else contact} - Active Conversation\n\n"
            f"**Current Topic:** {topic.replace('_', ' ').title()}\n"
            f"**Mood:** {emotion or 'neutral'}\n"
            f"**Person:** {person_link}\n\n"
            f"## Live Feed\n\n"
            + "\n\n---\n\n".join(turns) +
            f"\n\n---\n"
            f"*Updates every message in real-time*\n"
            f"*Clears when conversation ends*\n"
        )
        
        path.write_text(template, encoding="utf-8")

    # ── SHORT TERM — Organized by topic, not date ─────────────────────

    def write_short_term(
        self,
        contact: str,
        topic: str,
        content: str,
        emotion: str = "neutral",
        summary: str = ""
    ):
        """
        Topic-based short term memory.
        Named: "Owner_Talking_About_Work.md"
        or: "Kannaya_Family_Mentions.md"
        """
        is_owner = self._is_owner(contact)
        display_name = "Owner" if is_owner else self._safe(contact)
        topic_clean = topic.replace("-", "_").replace(" ", "_").title()

        name = f"{display_name}_Talking_About_{topic_clean}"
        path = (
            self.VAULT / "Brain" / "ShortTerm" / f"{name}.md"
        )

        now = datetime.now()
        expiry = (
            now + timedelta(days=7)
        ).strftime('%Y-%m-%d')

        # Load existing
        entries = []
        entry_count = 0
        if path.exists():
            try:
                raw = path.read_text(encoding="utf-8")
                if "## Mentions" in raw:
                    entries_raw = raw.split("## Mentions")[1].strip()
                    entries = [
                        e.strip()
                        for e in entries_raw.split("\n---\n")
                        if e.strip()
                    ]
                count_match = re.search(r"entry_count: (\d+)", raw)
                entry_count = int(count_match.group(1)) if count_match else 0
            except Exception:
                pass

        entry_count += 1
        new_entry = (
            f"**{now.strftime('%b %d, %H:%M')}**"
            f"{' | ' + emotion if emotion else ''}\n"
            f"{content[:200]}"
        )
        entries.append(new_entry)
        entries = entries[-15:]  # Keep last 15

        person_link = (
            "[[People/Owner/Owner_Profile]]"
            if is_owner
            else f"[[People/Contacts/{self._safe(contact)}/{self._safe(contact)}_Profile]]"
        )

        template = (
            f"---\n"
            f"type: short_term_memory\n"
            f"contact: {contact}\n"
            f"topic: {topic}\n"
            f"entry_count: {entry_count}\n"
            f"expires: {expiry}\n"
            f"last_updated: {now.isoformat()}\n"
            f"---\n\n"
            f"# {display_name} - {topic.replace('_', ' ').title()}\n\n"
            f"**Person:** {person_link}\n"
            f"**Expires:** {expiry} -> promotes to long-term if pattern found\n"
            f"**Entries:** {entry_count}\n\n"
            f"## Summary\n"
            f"{summary or 'Accumulating data...'}\n\n"
            f"## Mentions\n\n"
            + "\n\n---\n\n".join(entries) +
            f"\n\n---\n"
            f"*Short-term memory. Consolidates in 7 days.*\n"
        )

        path.write_text(template, encoding="utf-8")

    # ── EPISODIC MEMORY — Named after the actual event ────────────────

    def write_episodic(
        self,
        contact: str,
        event_description: str,
        full_content: str,
        emotion: str = "neutral",
        related_links: list = None
    ) -> str:
        """
        Named after what ACTUALLY happened.
        """
        is_owner = self._is_owner(contact)
        display = "Owner" if is_owner else self._safe(contact)
        event_slug = self._content_to_slug(event_description)

        now = datetime.now()
        name = f"{display}_{event_slug}"
        path = (
            self.VAULT / "Brain" / "Episodic" / f"{name}.md"
        )

        links_md = ""
        if related_links:
            links_md = "\n".join([
                f"- [[{link}]]" for link in related_links
            ])

        person_link = (
            "[[People/Owner/Owner_Profile]]"
            if is_owner
            else f"[[People/Contacts/{self._safe(contact)}/{self._safe(contact)}_Profile]]"
        )

        template = (
            f"---\n"
            f"type: episodic_memory\n"
            f"contact: {contact}\n"
            f"event: {event_description}\n"
            f"emotion: {emotion}\n"
            f"date: {now.strftime('%Y-%m-%d')}\n"
            f"never_expires: true\n"
            f"---\n\n"
            f"# {event_description.title()}\n\n"
            f"**When:** {now.strftime('%B %d, %Y at %H:%M')}\n"
            f"**Who:** {person_link}\n"
            f"**Emotion:** {emotion}\n\n"
            f"## What Happened\n"
            f"{full_content}\n\n"
            f"## Why ARION Remembers This\n"
            f"*High emotional weight or significant moment*\n\n"
            f"## Connected To\n"
            f"{links_md or '[[Brain/Brain_Overview]]'}\n\n"
            f"---\n"
            f"*Episodic memories never expire.*\n"
            f"*They form ARION's lived experience.*\n"
        )

        path.write_text(template, encoding="utf-8")
        return name

    # ── SEMANTIC FACT — Named after the actual fact ───────────────────

    def write_semantic_fact(
        self,
        subject: str,
        fact: str,
        confidence: float,
        source_memory: str = ""
    ) -> str:
        """
        Named after the fact itself.
        """
        slug = self._content_to_slug(f"{subject} {fact}")
        path = self.VAULT / "Brain" / "Semantic" / f"{slug}.md"

        now = datetime.now()

        # If exists, update confidence
        if path.exists():
            try:
                raw = path.read_text(encoding="utf-8")
                updated = re.sub(
                    r"confidence: [\d.]+",
                    f"confidence: {confidence:.2f}",
                    raw
                )
                updated = re.sub(
                    r"last_updated: .+",
                    f"last_updated: {now.strftime('%Y-%m-%d')}",
                    updated
                )
                # Add evidence line
                evidence_line = (
                    f"\n- {now.strftime('%b %d')} | "
                    f"confidence now {confidence:.0%}"
                )
                if "## Evidence" in updated:
                    updated = updated.replace(
                        "## Evidence",
                        f"## Evidence{evidence_line}"
                    )
                path.write_text(updated, encoding="utf-8")
                return slug
            except Exception:
                pass

        template = (
            f"---\n"
            f"type: semantic_fact\n"
            f"subject: {subject}\n"
            f"fact: {fact}\n"
            f"confidence: {confidence:.2f}\n"
            f"first_recorded: {now.strftime('%Y-%m-%d')}\n"
            f"last_updated: {now.strftime('%Y-%m-%d')}\n"
            f"---\n\n"
            f"# {subject.title()}: {fact.title()}\n\n"
            f"## The Fact\n"
            f"**{fact}**\n\n"
            f"**Confidence:** {confidence:.0%}\n"
            f"**First noticed:** {now.strftime('%B %d, %Y')}\n\n"
            f"## Evidence\n"
            f"- {now.strftime('%b %d')} | First observation | conf {confidence:.0%}\n\n"
            f"## Source\n"
            f"{f'[[Brain/ShortTerm/{source_memory}]]' if source_memory else 'Observed in conversation'}\n\n"
            f"## Updates\n"
            f"*Confidence grows each time this is confirmed*\n\n"
            f"---\n"
            f"*Semantic facts build ARION's model of people and the world.*\n"
        )

        path.write_text(template, encoding="utf-8")
        return slug

    # ── KNOWLEDGE NODE ─────────────────

    def write_knowledge_node(
        self,
        title: str,
        domain: str,
        essence: str,
        themes: list,
        arion_opinion: str = "",
        arion_rating: int = 5,
        key_facts: list = None,
        connections: list = None,
        triggers: list = None
    ) -> str:
        """
        Named after what was learned.
        """
        domain_folder_map = {
            "books":                 "Books",
            "movies_series":         "Movies",
            "anime":                 "Anime",
            "music":                 "Music",
            "philosophy":            "Philosophy",
            "history":               "History",
            "religion_beliefs":      "Religion",
            "science_biology_math":  "Science",
            "psychology_human_nature": "Psychology",
            "computer_science_tech": "Technology",
        }

        folder = domain_folder_map.get(domain, "General")
        safe_title = re.sub(r'[<>:"/\\|?*]', '', title)
        safe_title = re.sub(r'\s+', '_', safe_title.strip())[:50]

        path = (
            self.VAULT / "Knowledge" / folder /
            f"{safe_title}.md"
        )

        now = datetime.now()
        facts_md = "\n".join([f"- {f}" for f in (key_facts[:5] if key_facts else [])])
        themes_md = " | ".join([f"`{t}`" for t in (themes[:5] if themes else [])])
        
        template = (
            f"---\n"
            f"type: knowledge_node\n"
            f"title: {title}\n"
            f"domain: {domain}\n"
            f"folder: {folder}\n"
            f"ingested: {now.strftime('%Y-%m-%d')}\n"
            f"arion_rating: {arion_rating}/10\n"
            f"---\n\n"
            f"# {title}\n\n"
            f"## What It Is\n"
            f"{essence}\n\n"
            f"## Themes\n"
            f"{themes_md}\n\n"
            f"## Key Facts\n"
            f"{facts_md}\n\n"
            f"## ARION's Take\n"
            f"> {arion_opinion}\n\n"
            f"**Rating:** {'⭐' * min(arion_rating, 10)} {arion_rating}/10\n\n"
            f"## Connected To\n"
            f"[[Knowledge/{folder}/{folder}_Overview]]\n\n"
            f"---\n"
            f"*Learned: {now.strftime('%B %d, %Y')}*\n"
            f"[[Knowledge/{folder}/{folder}_Overview]]\n"
        )

        path.write_text(template, encoding="utf-8")

        # Update domain overview
        self._append_to_domain_overview(folder, safe_title, themes or [])
        return safe_title

    # ── HELPERS ───────────────────────────────────────────────────────

    def _content_to_slug(self, text: str) -> str:
        clean = re.sub(r"[^\w\s]", " ", text)
        words = clean.split()
        stop_words = {"the", "a", "an", "is", "was", "to", "for", "of", "and", "in"}
        filtered = [w.title() for w in words if w.lower() not in stop_words]
        return "_".join(filtered[:6])

    def _safe(self, name: str) -> str:
        name = str(name).split("@")[0]
        name = re.sub(r'[<>:"/\\|?*.\s]+', '_', name)
        return name.strip("_")[:40] or "Unknown"

    def _is_owner(self, contact: str) -> bool:
        c = str(contact).lower()
        return any(x in c for x in ["owner", "919154716156", "5500095565", "telegram"])

    def _append_to_domain_overview(self, folder: str, title: str, themes: list):
        path = self.VAULT / "Knowledge" / folder / f"{folder}_Overview.md"
        if not path.exists(): return
        try:
            content = path.read_text(encoding="utf-8")
            new_entry = f"\n- [[Knowledge/{folder}/{title}]] - {', '.join(themes[:2])}"
            if "## Books" in content or "## Movies" in content or "## Contents" in content:
                 content += new_entry
            else:
                 content += f"\n\n## Contents\n{new_entry}"
            path.write_text(content, encoding="utf-8")
        except: pass

    def write_person_profile(self, contact: str, data: dict):
        """Updates the persistent Profile.md for a person."""
        is_owner = self._is_owner(contact)
        folder = self.VAULT / "People" / ("Owner" if is_owner else f"Contacts/{self._safe(contact)}")
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / "Profile.md"
        
        now = datetime.now()
        topics = data.get("topics_discussed", {})
        top_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)[:5]
        topic_rows = "\n".join([f"| {t} | {c} |" for t, c in top_topics])
        
        emotions = data.get("emotions_observed", {})
        emotion_summary = ", ".join([f"{e} ({c})" for e, c in sorted(emotions.items(), key=lambda x: x[1], reverse=True)[:3]])

        recent = data.get("recent_topics", [])[-5:]
        recent_md = "\n".join([f"- {r['timestamp']} | **{r['topic']}** | {r['snippet']}" for r in reversed(recent)])

        template = (
            f"---\n"
            f"type: person_profile\n"
            f"contact: {contact}\n"
            f"interactions: {data.get('total_interactions', 0)}\n"
            f"last_seen: {data.get('last_seen', '')}\n"
            f"---\n\n"
            f"# {'Owner Profile' if is_owner else f'Profile: {contact}'}\n\n"
            f"## Stats\n"
            f"| Metric | Value |\n"
            f"|---|---|\n"
            f"| Total Chats | {data.get('total_interactions', 0)} |\n"
            f"| Last Active | {now.strftime('%Y-%m-%d %H:%M')} |\n\n"
            f"## Top Topics\n"
            f"| Topic | Hits |\n"
            f"|---|---|\n"
            f"{topic_rows}\n\n"
            f"## Emotions Observed\n"
            f"{emotion_summary or 'Neutral'}\n\n"
            f"## Recent Context\n"
            f"{recent_md or 'No data yet.'}\n\n"
            f"---\n"
            f"*Auto-updated by ARION Brain*\n"
        )
        path.write_text(template, encoding="utf-8")

    def _ensure_structure(self):
        folders = [
            "Brain/Working", "Brain/ShortTerm", "Brain/LongTerm",
            "Brain/Episodic", "Brain/Semantic", "Brain/Patterns",
            "People/Owner", "People/Contacts",
            "Knowledge/Books", "Knowledge/Movies"
        ]
        for f in folders:
            (self.VAULT / f).mkdir(parents=True, exist_ok=True)
