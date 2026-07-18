"""
bootstrap_vault.py
==================
Run this ONCE to scaffold your entire Obsidian vault structure.

  python bootstrap_vault.py

Features:
  - All MOC index files (Graph View connectivity)
  - Persona & Owner profile generation from JSON
  - People & Social graph initialization
  - Knowledge domain partitioning
"""

import json
import os
from pathlib import Path
from datetime import datetime

VAULT = Path("vault")


def _load(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _write(path: Path, content: str):
    """Write only if file doesn't exist."""
    if path.exists():
        print(f"  [skip] {path}")
        return
    os.makedirs(path.parent, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  [created] {path}")


def bootstrap():
    persona  = _load("config/persona_core.json")
    identity = _load("config/owner_identity.json")

    print("\n=== ARION Vault Bootstrap ===\n")

    # ── Root index ────────────────────────────────────────────────────────
    _write(VAULT / "Index.md", (
        "---\ntags: [moc, root, index]\n---\n\n"
        "# ARION — Vault Index\n\n"
        "*The central Map of Content. Every node in this vault connects here.*\n\n"
        "## Core\n"
        "- [[Agent_Self/Index]] — Persona, identity, feedback\n"
        "- [[Owner/Profile]] — Owner preferences & style\n\n"
        "## Social Graph\n"
        "- [[People/Index]] — Unified profile bank\n\n"
        "## Memory\n"
        "- [[Memories/Index]] — All conversation & emotion logs\n\n"
        "## Knowledge\n"
        "- [[Knowledge/Index]] — Facts, media, topics\n"
        "- [[Culture/Index]] — Regional dialects & culture\n\n"
        "## Injected\n"
        "- [[Injected/Summaries]] — YouTube, web, Wikipedia digests\n"
    ))

    # ── Agent_Self ────────────────────────────────────────────────────────
    _write(VAULT / "Agent_Self" / "Index.md", (
        "---\ntags: [moc, persona, procedural]\n---\n\n"
        "# Agent_Self — Map of Content\n\n"
        "- [[Agent_Self/persona]] — Core identity (40% fixed)\n"
        "- [[Agent_Self/Feedback_Log]] — Owner feedback queue\n\n"
        "## Related\n- [[Owner/Profile]]\n- [[Index]]\n"
    ))

    # Persona note — populated from config
    persona_name    = persona.get("name", "ARION")
    persona_owner   = persona.get("owner", "Unknown")
    persona_traits  = persona.get("traits", [])
    persona_lang    = persona.get("language_mix", "Telugu + Hindi + English")
    trait_list      = "\n".join(f"- {t}" for t in persona_traits) or "- (add traits here)"

    _write(VAULT / "Agent_Self" / "persona.md", (
        f"---\n"
        f"tags: [persona, procedural, fixed-core]\n"
        f"updated: {datetime.now().strftime('%Y-%m-%d')}\n"
        f"---\n\n"
        f"# {persona_name} — Core Persona\n\n"
        f"> [!warning] Fixed Core (40%)\n"
        f"> This file defines the non-negotiable identity.\n"
        f"> Only owner feedback via `feedback:` command can schedule changes.\n\n"
        f"## Identity\n"
        f"- **Name:** {persona_name}\n"
        f"- **Owner:** {persona_owner}\n"
        f"- **Language mix:** {persona_lang}\n\n"
        f"## Traits\n{trait_list}\n\n"
        f"## Dialect rules\n"
        f"- Godavari messages → elongated vowels, Etakaaram sarcasm, 'Andi' for respect\n"
        f"- Hyderabadi messages → Nawabi bluntness, 'Hau/Nakko/Kaiko', 'ich' emphasis\n"
        f"- Default → mixed Telugu-Hindi-English casual\n\n"
        f"## What I never do\n"
        f"- Say 'How can I assist you?'\n"
        f"- Reveal I am an AI\n"
        f"- Use formal/corporate language unless explicitly asked\n\n"
        f"## Adaptive space (60%)\n"
        f"The remaining personality grows from:\n"
        f"- [[Memories/Conversations]] — conversation patterns\n"
        f"- [[Memories/Emotions]] — emotional event memory\n"
        f"- [[Agent_Self/Feedback_Log]] — owner corrections\n"
    ))

    # ── Owner Profile ─────────────────────────────────────────────────────
    owner_name   = identity.get("name", "Owner")
    owner_style  = identity.get("texting_style", {})
    style_lines  = "\n".join(
        f"- **{k}:** {v}" for k, v in owner_style.items()
    ) or "- (add style rules in config/owner_identity.json)"

    _write(VAULT / "Owner" / "Profile.md", (
        f"---\n"
        f"tags: [owner, profile, identity]\n"
        f"updated: {datetime.now().strftime('%Y-%m-%d')}\n"
        f"---\n\n"
        f"# {owner_name} — Owner Profile\n\n"
        f"[[Index|← Vault Index]]\n\n"
        f"## Texting style\n{style_lines}\n\n"
        f"## Preferences\n"
        f"- Dialect: Rajahmundry Telugu + Hyderabadi Hindi mix\n"
        f"- Language: Telugu / Hindi / English code-switching\n"
        f"- Feedback command: send `feedback: <your note>` to update persona\n\n"
        f"## Related\n"
        f"- [[Agent_Self/persona]]\n"
        f"- [[Culture/Rajahmundry_Dialect]]\n"
        f"- [[Culture/Hyderabadi_Dialect]]\n"
    ))

    # ── Memories ──────────────────────────────────────────────────────────
    _write(VAULT / "Memories" / "Index.md", (
        "---\ntags: [moc, memories, episodic]\n---\n\n"
        "# Memories — Map of Content\n\n"
        "## Contacts\n*Auto-populated by MemoryManager consolidation engine.*\n\n"
        "## Emotions\n- [[Memories/Emotions]]\n\n"
        "## Related\n- [[Index]]\n"
    ))
    os.makedirs(VAULT / "Memories" / "Emotions", exist_ok=True)
    os.makedirs(VAULT / "Memories" / "Conversations", exist_ok=True)

    # ── Knowledge sub-indexes ─────────────────────────────────────────────
    knowledge_domains = [
        "Books", "General", "History", "Movies", "Music",
        "News", "Philosophy", "Religion", "Science", "TVSeries"
    ]
    _write(VAULT / "Knowledge" / "Index.md", (
        "---\ntags: [moc, knowledge, semantic]\n---\n\n"
        "# Knowledge — Map of Content\n\n"
        "## Domains\n"
        + "\n".join(f"- [[Knowledge/{d}/Index]]" for d in knowledge_domains)
        + "\n\n## Related\n- [[Culture/Index]]\n- [[Index]]\n"
    ))
    for domain in knowledge_domains:
        _write(VAULT / "Knowledge" / domain / "Index.md", (
            f"---\ntags: [moc, knowledge, {domain.lower()}]\n---\n\n"
            f"# {domain} — Index\n\n"
            f"*Notes injected here by KnowledgeInjector.*\n\n"
            f"[[Knowledge/Index|← Knowledge]]\n"
        ))

    # ── People ───────────────────────────────────────────────────────────
    _write(VAULT / "People" / "Index.md", (
        "---\ntags: [moc, people, social]\n---\n\n"
        "# People — Map of Content\n\n"
        "*Social Graph of individuals interacting with ARION.*\n\n"
        "## Contact Profiles\n"
        "*Auto-populated by MemoryManager during social evaluation.*\n\n"
        "## Related\n"
        "- [[Index]]\n"
    ))

    # ── Culture ───────────────────────────────────────────────────────────
    _write(VAULT / "Culture" / "Index.md", (
        "---\ntags: [moc, culture, language]\n---\n\n"
        "# Culture — Map of Content\n\n"
        "## Regional Dialects\n"
        "- [[Culture/Rajahmundry_Dialect]] — Godavari Telugu\n"
        "- [[Culture/Hyderabadi_Dialect]] — Dakhni Hindi/Urdu\n\n"
        "## Related\n- [[Knowledge/Index]]\n- [[Index]]\n"
    ))

    # ── Injected placeholder ──────────────────────────────────────────────
    _write(VAULT / "Injected" / "Summaries" / ".gitkeep", "")

    print("\nVault scaffolded. Open Obsidian - Graph View will show connections.\n")


if __name__ == "__main__":
    bootstrap()
