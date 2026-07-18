"""
NoiseGate — Decides what enters the Neural Core.
Phase 1: Filtered Sync.
Think of this as the thalamus of the brain —
only meaningful signals pass through to cortex.
"""

import re
import logging
from typing  import Dict, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from datetime    import datetime

logger = logging.getLogger("Zero.NoiseGate")


# ── Gate Configuration ────────────────────────────────────────────────────────
@dataclass
class NoiseGateConfig:
    """
    All thresholds in one place.
    Change these to tune what enters the Neural Core.
    """

    # ── Tag filters (Phase 1: Filtered Sync) ──────────────────────
    allowed_tags: List[str] = field(default_factory=lambda: [
        "active-project",
        "learning",
        "architecture",
        "algorithm",
        "research",
        "system",
        "jarvis",
        "zero",
        "knowledge",
        "protocol",
        "engineering",
        "data",
        "ai",
        "ml",
        "book",
        "philosophy",
        "psychology",
        "culture",
    ])

    # ── Quality thresholds ─────────────────────────────────────────
    min_word_count:      int   = 30      # Less than 30 words = fleeting note
    min_link_richness:   float = 0.0     # Minimum [[links]]/word ratio (0 = any)
    max_age_days:        int   = 730     # Ignore notes older than 2 years
    min_heading_depth:   int   = 0       # Require at least N headings (0 = any)

    # ── Filename patterns to ALWAYS skip ──────────────────────────
    skip_patterns: List[str] = field(default_factory=lambda: [
        r"^daily\/",          # Daily notes
        r"^journal\/",        # Journal entries
        r"^scratch\/",        # Scratch pad
        r"^inbox\/",          # Unprocessed inbox
        r"^templates\/",      # Obsidian templates
        r"\.excalidraw$",     # Drawing files
        r"^_",                # Private notes starting with _
    ])

    # ── Frontmatter fields that signal a note is ready ────────────
    ready_signals: List[str] = field(default_factory=lambda: [
        "status: active",
        "status: complete",
        "status: published",
    ])

    # ── Full sync override (Phase 2) ──────────────────────────────
    full_sync_mode: bool = False


class NoiseGate:
    """
    Filters Obsidian notes before they enter the Neural Core.
    
    Scoring model (0.0 → 1.0):
      +0.30  Has an allowed tag
      +0.20  Meets minimum word count
      +0.15  Has [[backlinks]] (connected to other nodes)
      +0.15  Has structured headings
      +0.10  Has frontmatter (organized note)
      +0.10  Has a ready_signal in frontmatter
      ─────
      1.00   Perfect score → directly into Neural Core
      
    Threshold: 0.45 (Phase 1 Filtered), 0.20 (Phase 2 Full)
    """

    PHASE1_THRESHOLD = 0.45
    PHASE2_THRESHOLD = 0.20

    def __init__(self, config: Optional[NoiseGateConfig] = None):
        self.config    = config or NoiseGateConfig()
        self.threshold = (
            self.PHASE2_THRESHOLD
            if self.config.full_sync_mode
            else self.PHASE1_THRESHOLD
        )
        self._stats = {
            "evaluated": 0,
            "passed":    0,
            "blocked":   0,
            "reasons":   {}
        }
        logger.info(
            f"✅ NoiseGate ready | mode={'full' if self.config.full_sync_mode else 'filtered'} "
            f"| threshold={self.threshold}"
        )

    # ═══════════════════════════════════════════════════════════════
    #  PUBLIC
    # ═══════════════════════════════════════════════════════════════

    def evaluate(
        self,
        note: Dict,
        vault_root: Optional[Path] = None
    ) -> Tuple[bool, float, str]:
        """
        Evaluate a parsed note.
        
        Args:
            note: Parsed note dict from ObsidianParser
            vault_root: Vault root for relative path checks
            
        Returns:
            (passes: bool, score: float, reason: str)
        """
        self._stats["evaluated"] += 1
        path = note.get("path", "")

        # ── Hard blocks (skip_patterns) ───────────────────────────
        for pattern in self.config.skip_patterns:
            rel_path = str(path)
            if vault_root:
                try:
                    rel_path = str(Path(path).relative_to(vault_root))
                except ValueError:
                    pass
            if re.search(pattern, rel_path, re.IGNORECASE):
                reason = f"skip_pattern:{pattern}"
                self._record_block(reason)
                return False, 0.0, reason

        # ── Age check ─────────────────────────────────────────────
        if not self.config.full_sync_mode:
            age_fail, age_reason = self._check_age(note)
            if age_fail:
                self._record_block(age_reason)
                return False, 0.0, age_reason

        # ── Score the note ────────────────────────────────────────
        score, breakdown = self._score(note)

        passes = score >= self.threshold
        reason = (
            f"score={score:.2f} breakdown={breakdown}"
        )

        if passes:
            self._stats["passed"] += 1
            logger.debug(f"✅ PASS  [{score:.2f}] {Path(path).name}")
        else:
            self._record_block(f"low_score:{score:.2f}")
            logger.debug(f"🚫 BLOCK [{score:.2f}] {Path(path).name}")

        return passes, score, reason

    def stats(self) -> Dict:
        total = self._stats["evaluated"]
        return {
            **self._stats,
            "pass_rate":  round(self._stats["passed"] / max(total, 1), 3),
            "block_rate": round(self._stats["blocked"] / max(total, 1), 3),
        }

    def upgrade_to_full_sync(self):
        """Phase 2 upgrade — lower the gate."""
        self.config.full_sync_mode = True
        self.threshold = self.PHASE2_THRESHOLD
        logger.info("⬆️ NoiseGate upgraded to FULL SYNC mode")

    # ═══════════════════════════════════════════════════════════════
    #  SCORING
    # ───────────────────────────────────────────────────────────────

    def _score(self, note: Dict) -> Tuple[float, Dict]:
        """
        Score a note on a 0.0–1.0 scale.
        Returns (total_score, breakdown_dict).
        """
        breakdown = {}
        score     = 0.0

        tags         = [t.lower() for t in note.get("tags", [])]
        word_count   = note.get("word_count", 0)
        backlinks    = note.get("backlinks", [])
        headings     = note.get("headings", [])
        frontmatter  = note.get("frontmatter", {})

        # ── +0.30 Tag match ───────────────────────────────────────
        allowed = [t.lower() for t in self.config.allowed_tags]
        tag_match = any(
            tag in allowed or
            any(tag.startswith(a) for a in allowed)
            for tag in tags
        )
        if tag_match:
            score += 0.30
            breakdown["tag_match"] = 0.30

        # ── +0.20 Word count ──────────────────────────────────────
        if word_count >= self.config.min_word_count:
            # Scale: 30 words = 0.10, 200+ words = 0.20
            wc_score = min(0.20, (word_count / 200) * 0.20)
            score   += wc_score
            breakdown["word_count"] = round(wc_score, 3)

        # ── +0.15 Has backlinks (connected node) ──────────────────
        if backlinks:
            link_score = min(0.15, len(backlinks) * 0.025)
            score     += link_score
            breakdown["backlinks"] = round(link_score, 3)

        # ── +0.15 Has structure (headings) ────────────────────────
        if len(headings) >= max(self.config.min_heading_depth, 1):
            heading_score = min(0.15, len(headings) * 0.03)
            score        += heading_score
            breakdown["headings"] = round(heading_score, 3)

        # ── +0.10 Has frontmatter ─────────────────────────────────
        if frontmatter:
            score += 0.10
            breakdown["frontmatter"] = 0.10

        # ── +0.10 Ready signal ────────────────────────────────────
        fm_str = " ".join(f"{k}: {v}" for k, v in frontmatter.items()).lower()
        if any(sig.lower() in fm_str for sig in self.config.ready_signals):
            score += 0.10
            breakdown["ready_signal"] = 0.10

        return round(min(score, 1.0), 3), breakdown

    # ═══════════════════════════════════════════════════════════════
    #  HELPERS
    # ───────────────────────────────────────────────────────────────

    def _check_age(self, note: Dict) -> Tuple[bool, str]:
        """Returns (is_too_old: bool, reason: str)."""
        fm = note.get("frontmatter", {})
        date_str = fm.get("date") or fm.get("created") or fm.get("updated")
        if not date_str:
            return False, ""   # No date = no age restriction

        try:
            formats = ["%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d", "%B %d, %Y"]
            note_date = None
            for fmt in formats:
                try:
                    # Clean the date string for some common formats
                    clean_date = str(date_str).strip()
                    note_date = datetime.strptime(clean_date[:10], fmt)
                    break
                except ValueError:
                    continue

            if note_date:
                age_days = (datetime.utcnow() - note_date).days
                if age_days > self.config.max_age_days:
                    return True, f"too_old:{age_days}days"
        except Exception:
            pass

        return False, ""

    def _record_block(self, reason: str):
        self._stats["blocked"] += 1
        key = reason.split(":")[0]
        self._stats["reasons"][key] = self._stats["reasons"].get(key, 0) + 1
