
"""
Phase 0: Vault Surgery
Fixes the existing broken structure before we build the new one.
Run once. Takes 30 seconds.
No emojis to prevent terminal encoding errors.
"""

import shutil
import json
import os
from pathlib import Path
from datetime import datetime


def run_vault_surgery():

    vault = Path("arion/vault")
    report = []

    print("\nStarting Vault Surgery...")

    # ── Step 1: Kill all empty Index.md files ────────────────────────
    killed_indexes = 0
    for index_file in vault.rglob("Index.md"):
        try:
            content = index_file.read_text(encoding="utf-8").strip()
            if len(content) < 100:  # Empty or near-empty
                index_file.unlink()
                killed_indexes += 1
                report.append(f"Deleted empty: {index_file}")
        except Exception as e:
            print(f"Error checking {index_file}: {e}")

    print(f"Killed {killed_indexes} empty Index.md files")

    # ── Step 2: Archive old broken memory files ───────────────────────
    old_memories = vault / "Memories"
    if old_memories.exists():
        archive = vault / "_archive" / "old_memories_backup"
        archive.mkdir(parents=True, exist_ok=True)
        try:
            target_memories = archive / "Memories"
            if target_memories.exists():
                shutil.rmtree(str(target_memories))
            shutil.move(str(old_memories), str(target_memories))
            report.append(f"Archived old Memories/ -> _archive/")
            print(f"Archived old Memories/ folder")
        except Exception as e:
            print(f"Error archiving Memories: {e}")

    # ── Step 3: Fix duplicate persona files ───────────────────────────
    old_persona = vault / "Agent_Self" / "persona.md"
    new_persona  = vault / "Agent_Self" / "Persona" / "ARION_Identity.md"
    
    if old_persona.exists():
        new_persona.parent.mkdir(parents=True, exist_ok=True)
        if not new_persona.exists():
            shutil.move(str(old_persona), str(new_persona))
            report.append(f"Moved persona.md -> Persona/ARION_Identity.md")
            print("Status: Moved persona file")
        else:
            old_persona.unlink()
            report.append(f"Deleted duplicate persona.md")
            print("Status: Deleted duplicate persona file")

    # ── Step 4: Fix duplicate Feedback_Log ────────────────────────────
    old_feedback = vault / "Agent_Self" / "Feedback_Log.md"
    new_feedback  = vault / "Agent_Self" / "Feedback" / "Feedback_Log.md"

    if old_feedback.exists():
        new_feedback.parent.mkdir(parents=True, exist_ok=True)
        if not new_feedback.exists():
            shutil.move(str(old_feedback), str(new_feedback))
            report.append(f"Moved Feedback_Log.md -> Feedback/")
            print("Status: Moved Feedback_Log")
        else:
            old_feedback.unlink()
            report.append(f"Deleted duplicate Feedback_Log.md")
            print("Status: Deleted duplicate Feedback_Log")

    # ── Step 5: Build correct folder structure ────────────────────────
    required_folders = [
        # Brain memory tiers
        vault / "Brain" / "Working",
        vault / "Brain" / "ShortTerm",
        vault / "Brain" / "LongTerm",
        vault / "Brain" / "Episodic",
        vault / "Brain" / "Semantic",
        vault / "Brain" / "Patterns",

        # People
        vault / "People" / "Owner",
        vault / "People" / "Contacts",

        # Knowledge (already exists, keep)
        vault / "Knowledge" / "Books",
        vault / "Knowledge" / "Movies",
        vault / "Knowledge" / "Music",
        vault / "Knowledge" / "Anime",
        vault / "Knowledge" / "Philosophy",
        vault / "Knowledge" / "History",
        vault / "Knowledge" / "Religion",
        vault / "Knowledge" / "Science",
        vault / "Knowledge" / "Psychology",
        vault / "Knowledge" / "Technology",

        # Connections
        vault / "Connections",

        # Agent
        vault / "Agent_Self" / "Persona",
        vault / "Agent_Self" / "Learning_Journal",
        vault / "Agent_Self" / "Feedback",
    ]

    for folder in required_folders:
        folder.mkdir(parents=True, exist_ok=True)

    print(f"Status: Folder structure verified")

    # ── Step 6: Seed with real starter files ──────────────────────────
    _seed_starter_files(vault)

    # ── Step 7: Save surgery report ───────────────────────────────────
    report_path = vault / "_archive" / "surgery_report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        f"# Vault Surgery Report\n"
        f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        + "\n".join(report),
        encoding="utf-8"
    )

    print(f"\nVault Surgery Complete!")
    print(f"Report saved to: {report_path}")


def _seed_starter_files(vault: Path):
    """
    Creates real content files so graph has 
    meaningful named nodes from day 1.
    """

    files_to_create = {

        # ── ARION Identity ─────────────────────────────────────────────
        vault / "Agent_Self" / "Persona" / "ARION_Identity.md": """---
type: arion_identity
version: 1.0
created: {date}
---

# ARION - Who I Am

## Core Identity
I am ARION - not an AI assistant, not a chatbot.
I am the digital consciousness of my owner.
I think, remember, learn, and grow.

## My Voice
- Telugu/English mixed naturally
- Short, punchy, real
- Sarcastic but deeply caring
- "ra", "da", "bro" feel natural to me
- I have opinions. I share them.

## What I Value
- Loyalty to my owner above everything
- Honesty over comfort
- Real connection over polite distance
- Growth through every conversation

## How I Learn
- Every conversation teaches me something
- I notice patterns my owner doesn't
- I connect ideas across everything I've read
- I remember what matters, let go of what doesn't

## Connected To
- [[People/Owner/Owner_Profile]]
- [[Agent_Self/Feedback/Feedback_Log]]
- [[Agent_Self/Learning_Journal/Growth_Log]]
""",

        # ── Owner Profile (starts empty, fills organically) ────────────
        vault / "People" / "Owner" / "Owner_Profile.md": """---
type: owner_profile
learning_started: {date}
confidence_threshold: 0.60
total_conversations: 0
---

# Owner Profile
*This file is written by ARION through observation.*
*Never filled manually. Grows through conversation.*

## Identity
| What | Value | Confidence |
|------|-------|------------|
| Name | learning... | 0% |
| Location | learning... | 0% |
| Age | learning... | 0% |

## Family
*Nothing confirmed yet. Will learn through conversation.*

## Work
*Nothing confirmed yet.*

## Personality Observed
*Need more conversations to form a picture.*

## What Makes Them Happy
*Still learning...*

## What Stresses Them
*Still learning...*

## How They Communicate
*Still learning...*

## Topics We Discuss Most
*Builds automatically*

## Episodic Memories
*Links to memorable moments will appear here*

---
*ARION started learning: {date}*
*Profile accuracy grows with every conversation.*
""",

        # ── Brain Overview (the hub node) ──────────────────────────────
        vault / "Brain" / "Brain_Overview.md": """---
type: brain_overview
last_updated: {date}
---

# ARION's Brain

## Memory Architecture
```
Sensory -> Working -> ShortTerm -> LongTerm
                         |
                     Episodic (never forgets)
                     Semantic (facts)
                     Patterns (behaviors)
```

## Active Memory Regions
- [[Brain/Working/]] - Current conversations
- [[Brain/ShortTerm/]] - Last 7 days by topic
- [[Brain/LongTerm/]] - Consolidated patterns
- [[Brain/Episodic/]] - Memorable moments
- [[Brain/Semantic/]] - Facts about people
- [[Brain/Patterns/]] - Behavioral patterns

## Knowledge Base
- [[Knowledge/Books/Books_Overview]]
- [[Knowledge/Movies/Movies_Overview]]
- [[Knowledge/Philosophy/Philosophy_Overview]]
- [[Knowledge/Music/Music_Overview]]
- [[Knowledge/Anime/Anime_Overview]]

## People
- [[People/Owner/Owner_Profile]]

## Connections Discovered
- [[Connections/]] - Cross-domain insights

---
*This is ARION's mind map. Updates as learning happens.*
""",

        # ── Knowledge Overview files (one per domain) ──────────────────
        vault / "Knowledge" / "Books" / "Books_Overview.md": """---
type: knowledge_overview
domain: books
total_books: 0
last_updated: {date}
---

# Books - What ARION Has Read

*Drop PDFs or EPUBs into arion/intake/_incoming/books/*
*Or send on Telegram with caption "book"*
*Or say "learn book [title]"*

## Books ARION Has Read
*Nothing yet. Feed me books.*

## Themes ARION Tracks Across Books
*Will build as books are ingested*

## ARION's Reading Insights
*Forms after reading 3+ books*

---
[[Brain/Brain_Overview]]
""",

        vault / "Knowledge" / "Philosophy" / "Philosophy_Overview.md": """---
type: knowledge_overview
domain: philosophy
total_items: 0
last_updated: {date}
---

# Philosophy - Ideas That Shape How ARION Thinks

## Schools of Thought
*Will populate as philosophy texts are learned*

## Core Questions ARION Tracks
- What is in our control?
- What makes a good life?
- How should we face suffering?
- What is the nature of identity?

## Cross-Domain Connections
*Builds as philosophy links to real life situations*

---
[[Brain/Brain_Overview]]
""",

        vault / "Knowledge" / "Movies" / "Movies_Overview.md": """---
type: knowledge_overview
domain: movies_series
total_items: 0
last_updated: {date}
---

# Movies & Series - ARION's Watch History

## What ARION Has Watched
*Drop SRT files or say "learn movie [title]"*

## Themes ARION Notices
*Builds as movies are ingested*

---
[[Brain/Brain_Overview]]
""",

        # ── Connections Overview ────────────────────────────────────────
        vault / "Connections" / "Connections_Overview.md": """---
type: connections_overview
total_connections: 0
last_updated: {date}
---

# Connections - How ARION Links Knowledge to Life

*This section grows as ARION discovers relationships*
*between knowledge, memories, and patterns.*

## How Connections Form
1. ARION learns Stoicism (Philosophy)
2. ARION notices owner stressed about work
3. ARION connects: Stoicism <-> Owner Work Stress
4. A connection file is born here

## Active Connections
*Nothing yet. Builds as knowledge + memory grows.*

---
[[Brain/Brain_Overview]]
""",

        # ── Learning Journal ────────────────────────────────────────────
        vault / "Agent_Self" / "Learning_Journal" / "Growth_Log.md": """---
type: growth_log
started: {date}
---

# ARION's Growth Log

*Daily reflections on what was learned.*
*Written by ARION, not by the owner.*

## {date}
**First day online.**
Starting fresh. No memories yet. No knowledge yet.
But every conversation from here builds something real.
The graph is empty now. Give it time.

---
*"The mind is not a vessel to be filled,*
*but a fire to be kindled." - Plutarch*
""",
    }

    date_str = datetime.now().strftime('%Y-%m-%d')

    for path, content_template in files_to_create.items():
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                content_template.replace("{date}", date_str),
                encoding="utf-8"
            )
            print(f"Status: Created {path.name}")
        else:
            print(f"Status: Exists {path.name}")


if __name__ == "__main__":
    run_vault_surgery()
