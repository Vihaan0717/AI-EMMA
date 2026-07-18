"""
ObsidianParser — Reads Obsidian markdown vaults.
Extracts:
  - Frontmatter (YAML)
  - [[Backlinks]] → graph edges
  - #tags         → neuron labels
  - ## Headings   → structural nodes
  - Body text     → knowledge content
  - Embedded ![[files]] → asset refs
  - Dataview queries → structured data
"""

import re
import yaml
import logging
from typing      import Dict, List, Optional, Any, Iterator
from pathlib     import Path
from dataclasses import dataclass, field
from datetime    import datetime

logger = logging.getLogger("Zero.ObsidianParser")


@dataclass
class ParsedNote:
    """A fully parsed Obsidian note — ready for Neural Core ingestion."""
    path:          Path
    title:         str
    frontmatter:   Dict[str, Any]   = field(default_factory=dict)
    tags:          List[str]        = field(default_factory=list)
    backlinks:     List[str]        = field(default_factory=list)  # [[link targets]]
    headings:      List[Dict]       = field(default_factory=list)  # {level, text, anchor}
    sections:      List[Dict]       = field(default_factory=list)  # {heading, content}
    body:          str              = ""
    word_count:    int              = 0
    embeds:        List[str]        = field(default_factory=list)  # ![[embedded files]]
    aliases:       List[str]        = field(default_factory=list)  # frontmatter aliases
    created_at:    Optional[str]    = None
    updated_at:    Optional[str]    = None

    def to_dict(self) -> Dict:
        return {
            "path":        str(self.path),
            "title":       self.title,
            "frontmatter": self.frontmatter,
            "tags":        self.tags,
            "backlinks":   self.backlinks,
            "headings":    self.headings,
            "sections":    self.sections,
            "body":        self.body,
            "word_count":  self.word_count,
            "embeds":      self.embeds,
            "aliases":     self.aliases,
            "created_at":  self.created_at,
            "updated_at":  self.updated_at,
        }


class ObsidianParser:
    """
    Obsidian Vault Parser.
    Performs a Synaptic Scan — builds a full picture
    of every note's content AND its relationships.
    """

    # ── Regex patterns ────────────────────────────────────────────
    FRONTMATTER_RE  = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)
    BACKLINK_RE     = re.compile(r'\[\[([^\]|#]+)(?:\|[^\]]*)?\]\]')
    EMBED_RE        = re.compile(r'!\[\[([^\]]+)\]\]')
    TAG_INLINE_RE   = re.compile(r'(?<!\S)#([a-zA-Z][a-zA-Z0-9_\-/]*)')
    HEADING_RE      = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
    CODE_BLOCK_RE   = re.compile(r'```[\s\S]*?```', re.MULTILINE)
    INLINE_CODE_RE  = re.compile(r'`[^`]+`')
    HTML_TAG_RE     = re.compile(r'<[^>]+>')
    CALLOUT_RE      = re.compile(r'>\s*\[!(\w+)\][^\n]*\n((?:>.*\n?)*)')
    DATAVIEW_RE     = re.compile(r'```dataview[\s\S]*?```', re.MULTILINE)

    def __init__(self, vault_path: str | Path):
        self.vault_path = Path(vault_path)
        if not self.vault_path.exists():
            raise FileNotFoundError(f"Vault not found: {vault_path}")
        logger.info(f"✅ ObsidianParser ready | vault={self.vault_path}")

    # ═══════════════════════════════════════════════════════════════
    #  PUBLIC
    # ═══════════════════════════════════════════════════════════════

    def scan_vault(self) -> Iterator[ParsedNote]:
        """
        Generator — yields ParsedNote for every .md file in vault.
        Memory-efficient: processes one file at a time.
        """
        md_files = list(self.vault_path.rglob("*.md"))
        total    = len(md_files)
        logger.info(f"🔍 Synaptic Scan started: {total} notes found")

        for i, filepath in enumerate(md_files, 1):
            try:
                note = self.parse_file(filepath)
                if note:
                    if i % 100 == 0:
                        logger.info(f"   → Scanned {i}/{total} notes...")
                    yield note
            except Exception as e:
                logger.warning(f"⚠️ Parse failed: {filepath.name} — {e}")
                continue

        logger.info(f"✅ Synaptic Scan complete: {total} notes processed")

    def parse_file(self, filepath: Path) -> Optional[ParsedNote]:
        """Parse a single Obsidian markdown file."""
        try:
            raw = filepath.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            logger.error(f"Read failed: {filepath} — {e}")
            return None

        return self.parse_raw(raw, filepath)

    def parse_raw(self, raw: str, filepath: Path) -> ParsedNote:
        """Parse raw markdown text into a ParsedNote."""
        note = ParsedNote(
            path=filepath,
            title=self._extract_title(raw, filepath)
        )

        # ── Step 1: Extract and strip frontmatter ─────────────────
        frontmatter, body = self._split_frontmatter(raw)
        note.frontmatter  = frontmatter

        # ── Step 2: Extract tags (frontmatter + inline) ───────────
        note.tags    = self._extract_tags(frontmatter, body)
        note.aliases = self._extract_aliases(frontmatter)

        # ── Step 3: Extract timestamps ────────────────────────────
        note.created_at = self._get_date(frontmatter, filepath, "created")
        note.updated_at = self._get_date(frontmatter, filepath, "updated")

        # ── Step 4: Clean body (remove code blocks etc.) ──────────
        clean_body    = self._clean_body(body)
        note.body     = clean_body

        # ── Step 5: Extract [[backlinks]] (graph edges) ───────────
        note.backlinks = self._extract_backlinks(body)   # Use raw body for links
        note.embeds    = self._extract_embeds(body)

        # ── Step 6: Extract headings (structural nodes) ───────────
        note.headings = self._extract_headings(body)

        # ── Step 7: Build sections (heading → content map) ────────
        note.sections = self._build_sections(body)

        # ── Step 8: Word count ────────────────────────────────────
        note.word_count = len(clean_body.split())

        return note

    # ═══════════════════════════════════════════════════════════════
    #  EXTRACTION METHODS
    # ───────────────────────────────────────────────────────────────

    def _split_frontmatter(self, raw: str) -> tuple[Dict, str]:
        """Split YAML frontmatter from body."""
        match = self.FRONTMATTER_RE.match(raw)
        if not match:
            return {}, raw

        yaml_str = match.group(1)
        body     = raw[match.end():]

        try:
            fm = yaml.safe_load(yaml_str) or {}
            if not isinstance(fm, dict):
                fm = {}
        except yaml.YAMLError as e:
            logger.debug(f"YAML parse error (non-critical): {e}")
            fm = {}

        return fm, body

    def _extract_title(self, raw: str, filepath: Path) -> str:
        """
        Extract note title in priority order:
        1. First H1 heading
        2. frontmatter title field
        3. Filename (without extension)
        """
        # Try H1
        h1 = re.search(r'^#\s+(.+)$', raw, re.MULTILINE)
        if h1:
            return h1.group(1).strip()

        # Try frontmatter title
        fm_match = self.FRONTMATTER_RE.match(raw)
        if fm_match:
            try:
                fm = yaml.safe_load(fm_match.group(1)) or {}
                if isinstance(fm, dict) and fm.get("title"):
                    return str(fm["title"]).strip()
            except Exception:
                pass

        # Fallback: filename
        return filepath.stem.replace("-", " ").replace("_", " ").title()

    def _extract_tags(self, frontmatter: Dict, body: str) -> List[str]:
        """
        Extract tags from:
        1. frontmatter 'tags' field (list or space-separated string)
        2. Inline #tags in body
        """
        tags = set()

        # Frontmatter tags
        fm_tags = frontmatter.get("tags", [])
        if isinstance(fm_tags, list):
            tags.update(str(t).lower().strip() for t in fm_tags if t)
        elif isinstance(fm_tags, str):
            tags.update(t.lower().strip() for t in fm_tags.split() if t)

        # Inline tags (skip code blocks)
        clean = self.CODE_BLOCK_RE.sub("", body)
        clean = self.INLINE_CODE_RE.sub("", clean)
        inline_tags = self.TAG_INLINE_RE.findall(clean)
        tags.update(t.lower() for t in inline_tags)

        # Normalize: "project/zero" → ["project/zero", "project", "zero"]
        expanded = set()
        for tag in tags:
            expanded.add(tag)
            parts = tag.split("/")
            if len(parts) > 1:
                expanded.update(parts)

        return sorted(expanded)

    def _extract_aliases(self, frontmatter: Dict) -> List[str]:
        aliases = frontmatter.get("aliases", [])
        if isinstance(aliases, list):
            return [str(a).strip() for a in aliases if a]
        elif isinstance(aliases, str):
            return [aliases.strip()]
        return []

    def _extract_backlinks(self, body: str) -> List[str]:
        """
        Extract [[wikilinks]] as graph edges.
        Handles:
          [[Note Name]]
          [[Note Name|Display Text]]
          [[Note Name#Heading]]
        """
        # Remove embeds first (![[...]])
        body_no_embeds = self.EMBED_RE.sub("", body)

        links = self.BACKLINK_RE.findall(body_no_embeds)
        # Normalize: lowercase, strip path prefix
        normalized = []
        for link in links:
            clean = link.strip()
            # Remove folder prefix if any (folder/Note → Note)
            if "/" in clean:
                clean = clean.split("/")[-1]
            # Remove heading anchor (#anchor)
            clean = clean.split("#")[0].strip()
            if clean:
                normalized.append(clean)

        return list(dict.fromkeys(normalized))  # Deduplicate, preserve order

    def _extract_embeds(self, body: str) -> List[str]:
        """Extract ![[embedded files]]."""
        return [e.strip() for e in self.EMBED_RE.findall(body)]

    def _extract_headings(self, body: str) -> List[Dict]:
        """
        Extract all headings as structural nodes.
        Returns: [{level, text, anchor}]
        """
        # Remove code blocks to avoid false positives
        clean = self.CODE_BLOCK_RE.sub("", body)

        headings = []
        for match in self.HEADING_RE.finditer(clean):
            level = len(match.group(1))
            text  = match.group(2).strip()
            # Remove inline formatting from heading text
            text_clean = re.sub(r'[\*\_\`\[\]]', '', text)
            anchor     = re.sub(r'[^\w\s-]', '', text_clean).lower()
            anchor     = re.sub(r'\s+', '-', anchor).strip('-')
            headings.append({
                "level":  level,
                "text":   text_clean,
                "anchor": anchor
            })

        return headings

    def _build_sections(self, body: str) -> List[Dict]:
        """
        Split body into sections by heading.
        Returns: [{heading, level, content}]
        """
        clean = self.CODE_BLOCK_RE.sub("[CODE_BLOCK]", body)
        parts = re.split(r'^(#{1,6}\s+.+)$', clean, flags=re.MULTILINE)

        sections = []
        current_heading = {"text": "__intro__", "level": 0}
        buffer = []

        for part in parts:
            hm = re.match(r'^(#{1,6})\s+(.+)$', part.strip())
            if hm:
                # Save previous section
                content = " ".join(buffer).strip()
                if content:
                    sections.append({
                        "heading": current_heading["text"],
                        "level":   current_heading["level"],
                        "content": content[:3000]
                    })
                buffer = []
                current_heading = {
                    "text":  re.sub(r'[\*\_\`]', '', hm.group(2)).strip(),
                    "level": len(hm.group(1))
                }
            else:
                buffer.append(part.strip())

        # Last section
        content = " ".join(buffer).strip()
        if content:
            sections.append({
                "heading": current_heading["text"],
                "level":   current_heading["level"],
                "content": content[:3000]
            })

        return [s for s in sections if s["content"]]

    def _clean_body(self, body: str) -> str:
        """Remove markdown syntax, return plain readable text."""
        text = body

        # Remove code blocks (keep as placeholder)
        text = self.CODE_BLOCK_RE.sub(" [code block] ", text)
        text = self.INLINE_CODE_RE.sub(" [code] ", text)

        # Remove dataview queries
        text = self.DATAVIEW_RE.sub("", text)

        # Remove callouts but keep content
        text = re.sub(r'>\s*\[!\w+\][^\n]*', '', text)
        text = re.sub(r'^>\s*', '', text, flags=re.MULTILINE)

        # Remove HTML
        text = self.HTML_TAG_RE.sub(' ', text)

        # Remove markdown formatting
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)   # **bold**
        text = re.sub(r'\*(.+?)\*',     r'\1', text)   # *italic*
        text = re.sub(r'__(.+?)__',     r'\1', text)   # __bold__
        text = re.sub(r'_(.+?)_',       r'\1', text)   # _italic_
        text = re.sub(r'~~(.+?)~~',     r'\1', text)   # ~~strikethrough~~
        text = re.sub(r'==(.+?)==',     r'\1', text)   # ==highlight==

        # Remove links but keep text
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # [text](url)
        text = re.sub(r'!\[\[([^\]]+)\]\]', '', text)           # ![[embed]]
        text = re.sub(r'\[\[([^\]|]+)(?:\|([^\]]+))?\]\]',
                      lambda m: m.group(2) or m.group(1), text)  # [[link|text]]

        # Remove headings markers (keep text)
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)

        # Remove horizontal rules
        text = re.sub(r'^[-*_]{3,}$', '', text, flags=re.MULTILINE)

        # Remove bullet/numbered list markers
        text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)

        # Clean whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'[ \t]{2,}', ' ',  text)

        return text.strip()

    @staticmethod
    def _get_date(
        frontmatter: Dict,
        filepath: Path,
        kind: str = "created"
    ) -> Optional[str]:
        """Extract date from frontmatter or file metadata."""
        keys = (
            ["date", "created", "creation date", "date created"]
            if kind == "created"
            else ["updated", "modified", "last modified", "date updated"]
        )
        for key in keys:
            val = frontmatter.get(key)
            if val:
                return str(val)

        # Fall back to file system timestamps
        try:
            stat = filepath.stat()
            ts   = stat.st_ctime if kind == "created" else stat.st_mtime
            return datetime.fromtimestamp(ts).isoformat()
        except Exception:
            return None
