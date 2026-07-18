from pathlib import Path
from datetime import datetime
import os

MOC_TEMPLATES = {
    "Books": """---
type: map_of_content
domain: books
auto_generated: true
---

# 📚 Books — Map of Content

> ARION's reading list. Every book here was digested, 
> not just stored. Opinions formed. Connections made.

## Books ARION Has Read
{book_links}

## Themes Across Books
{theme_connections}

## ARION's Top Picks
*Updates as more books are read*

---
*This index updates automatically when new books are learned.*
""",

    "Movies": """---
type: map_of_content  
domain: movies_series
---

# 🎬 Movies & Series — Map of Content

## What ARION Has Watched
{movie_links}

## Recurring Themes
{theme_connections}

---
*Auto-updated when new content is ingested.*
""",

    "Philosophy": """---
type: map_of_content
domain: philosophy
---

# 🧠 Philosophy — Map of Content

> Ideas that shaped how ARION thinks.

## Thinkers & Schools
{philosophy_links}

## Core Themes ARION Tracks
- Control vs Chaos -> [[Stoicism]] [[Bhagavad_Gita]]
- Human Nature -> [[Nietzsche]] [[Psychology/]]
- Meaning -> [[Existentialism]]

---
""",
}

def rebuild_indexes():
    base_dir = Path("c:/Users/anger/Desktop/JARVIS-v2")
    knowledge = base_dir / "arion" / "vault" / "Knowledge"
    
    if not knowledge.exists():
        print(f"[INFO] Knowledge folder not found at {knowledge}")
        return

    for domain_folder in knowledge.iterdir():
        if not domain_folder.is_dir():
            continue
        
        # Delete old empty Index.md
        old_index = domain_folder / "Index.md"
        if old_index.exists():
            content = old_index.read_text(encoding="utf-8")
            if len(content.strip()) < 100:  # Empty or near-empty
                old_index.unlink()
                print(f"[CLEANUP] Deleted empty: {old_index}")
        
        # Build new MOC
        domain_name = domain_folder.name
        template = MOC_TEMPLATES.get(domain_name, """---
type: map_of_content
domain: {domain}
---

# {domain} — Map of Content

## Contents
{links}

---
*Auto-updated as ARION learns.*
""")
        
        # Find existing content files
        content_files = [
            f for f in domain_folder.glob("*.md")
            if f.name != "MOC_" + domain_name + ".md" and f.name != "Index.md"
        ]
        
        links = "\n".join([
            f"- [[Knowledge/{domain_name}/{f.stem}]]"
            for f in content_files
        ]) or "*Nothing learned yet. Drop files or use /learn command.*"
        
        moc_content = template.format(
            domain=domain_name,
            book_links=links,
            movie_links=links,
            philosophy_links=links,
            theme_connections="*Builds automatically as connections are found.*",
            links=links
        )
        
        moc_path = domain_folder / f"MOC_{domain_name}.md"
        moc_path.write_text(moc_content, encoding="utf-8")
        print(f"[SUCCESS] Created MOC: {moc_path}")

if __name__ == "__main__":
    rebuild_indexes()
