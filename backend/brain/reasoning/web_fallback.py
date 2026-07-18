"""
WebFallback — Searches the web when local resources fail.
Uses DuckDuckGo (NO API KEY, completely free).
Performs deep extraction + summarization without AI.
Saves results so the same search is never repeated.
"""

import asyncio
import re
import json
import logging
import hashlib
import sqlite3
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus, urljoin

logger = logging.getLogger("JARVIS.WebFallback")

DB_PATH = Path(__file__).parent.parent / "data" / "web_cache.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


class WebFallback:
    """
    Web search fallback system.
    Chain: DuckDuckGo Instant → DuckDuckGo HTML → Deep page scrape
    Caches results locally so we never search the same thing twice.
    """

    DDG_API_URL  = "https://api.duckduckgo.com/"
    DDG_HTML_URL = "https://html.duckduckgo.com/html/"
    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    MAX_RESULTS      = 5
    MAX_CONTENT_LEN  = 8000   # chars per page
    CACHE_TTL_HOURS  = 24

    def __init__(self):
        self.conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        self._init_db()
        logger.info("✅ WebFallback ready — DuckDuckGo mode (no API key)")

    def _init_db(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS search_cache (
                query_hash   TEXT PRIMARY KEY,
                query_text   TEXT NOT NULL,
                results      TEXT NOT NULL,
                combined_text TEXT NOT NULL,
                best_answer  TEXT NOT NULL,
                confidence   REAL DEFAULT 0.7,
                source_urls  TEXT DEFAULT '[]',
                cached_at    TEXT NOT NULL
            )
        """)
        self.conn.commit()

    # ═══════════════════════════════════════════════════════════════
    #  PUBLIC
    # ═══════════════════════════════════════════════════════════════

    async def search(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Main search function.
        Returns dict with: best_answer, combined_text, sources, confidence
        """
        # Check cache first
        cached = self._get_cached(query)
        if cached:
            logger.info(f"💾 Web cache hit for: {query[:50]}")
            return cached

        logger.info(f"🌐 Web searching: {query[:80]}")

        # Try DuckDuckGo Instant Answer API
        instant = await self._ddg_instant(query)

        # Scrape HTML results for more content
        pages = await self._ddg_html_search(query)

        # Combine and extract best answer
        result = self._build_result(query, instant, pages)

        if result:
            self._cache_result(query, result)
            logger.info(
                f"✅ Web search complete: {len(result.get('sources', []))} sources, "
                f"confidence={result.get('confidence', 0):.0%}"
            )

        return result

    # ═══════════════════════════════════════════════════════════════
    #  SEARCH METHODS
    # ═══════════════════════════════════════════════════════════════

    async def _ddg_instant(self, query: str) -> Optional[Dict]:
        """DuckDuckGo Instant Answer API — structured data, no scraping."""
        try:
            import httpx
            params = {
                "q": query,
                "format": "json",
                "no_html": "1",
                "skip_disambig": "1"
            }
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(self.DDG_API_URL, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    answer = (
                        data.get("AbstractText")
                        or data.get("Answer")
                        or data.get("Definition")
                        or ""
                    )
                    if answer:
                        return {
                            "answer": answer,
                            "source": data.get("AbstractURL", ""),
                            "type": data.get("Type", ""),
                            "related": [
                                r.get("Text", "")
                                for r in data.get("RelatedTopics", [])[:3]
                                if isinstance(r, dict)
                            ]
                        }
        except Exception as e:
            logger.debug(f"DDG instant failed: {e}")
        return None

    async def _ddg_html_search(self, query: str) -> List[Dict]:
        """
        Scrape DuckDuckGo HTML results.
        Returns list of {title, url, snippet}.
        """
        results = []
        try:
            import httpx
            from html.parser import HTMLParser

            data = {"q": query, "b": "", "kl": "us-en"}
            async with httpx.AsyncClient(
                timeout=15, headers=self.HEADERS, follow_redirects=True
            ) as client:
                resp = await client.post(self.DDG_HTML_URL, data=data)
                if resp.status_code != 200:
                    return []

                # Parse results
                results = self._parse_ddg_html(resp.text)

                # Scrape top pages for full content
                full_results = []
                for r in results[:self.MAX_RESULTS]:
                    content = await self._scrape_page(client, r["url"])
                    r["content"] = content
                    full_results.append(r)

                return full_results

        except Exception as e:
            logger.warning(f"DDG HTML search failed: {e}")
        return results

    async def _scrape_page(self, client, url: str) -> str:
        """Scrape a page and extract clean text content."""
        if not url or not url.startswith("http"):
            return ""
        try:
            resp = await client.get(url, timeout=8, headers=self.HEADERS)
            if resp.status_code == 200:
                return self._extract_text(resp.text)
        except Exception as e:
            logger.debug(f"Page scrape failed {url}: {e}")
        return ""

    # ═══════════════════════════════════════════════════════════════
    #  PARSING
    # ═══════════════════════════════════════════════════════════════

    def _parse_ddg_html(self, html: str) -> List[Dict]:
        """Parse DuckDuckGo HTML results page."""
        results = []

        # Extract result blocks
        # DDG result structure: <div class="result">
        result_blocks = re.findall(
            r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>([^<]+)</a>.*?'
            r'<a[^>]+class="result__snippet"[^>]*>(.*?)</a>',
            html, re.DOTALL
        )

        for url, title, snippet in result_blocks[:self.MAX_RESULTS]:
            # DDG wraps URLs — extract the actual URL
            actual_url = self._extract_ddg_url(url)
            clean_title   = re.sub(r'<[^>]+>', '', title).strip()
            clean_snippet = re.sub(r'<[^>]+>', '', snippet).strip()
            if actual_url and clean_title:
                results.append({
                    "url":     actual_url,
                    "title":   clean_title,
                    "snippet": clean_snippet,
                    "content": ""
                })

        # Fallback: simpler regex if above fails
        if not results:
            urls = re.findall(r'href="(/l/\?[^"]+)"', html)
            titles = re.findall(r'class="result__a"[^>]*>([^<]+)<', html)
            snippets = re.findall(r'class="result__snippet"[^>]*>([^<]+)<', html)

            for i, (url, title) in enumerate(zip(urls, titles)):
                actual_url = self._extract_ddg_url(url)
                results.append({
                    "url":     actual_url or url,
                    "title":   title.strip(),
                    "snippet": snippets[i].strip() if i < len(snippets) else "",
                    "content": ""
                })

        return results

    @staticmethod
    def _extract_ddg_url(raw: str) -> str:
        """Extract actual URL from DuckDuckGo redirect URL."""
        match = re.search(r'uddg=([^&]+)', raw)
        if match:
            from urllib.parse import unquote
            return unquote(match.group(1))
        if raw.startswith("http"):
            return raw
        return ""

    @staticmethod
    def _extract_text(html: str) -> str:
        """
        Extract clean readable text from HTML.
        Removes scripts, styles, nav, footer etc.
        """
        # Remove non-content sections
        for tag in ["script", "style", "nav", "footer",
                    "header", "aside", "form", "iframe"]:
            html = re.sub(
                rf'<{tag}[\s\S]*?</{tag}>', ' ', html, flags=re.IGNORECASE
            )

        # Remove all remaining HTML tags
        text = re.sub(r'<[^>]+>', ' ', html)

        # Clean whitespace
        text = re.sub(r'&[a-z]+;', ' ', text)   # HTML entities
        text = re.sub(r'\s{2,}', ' ', text)       # Multiple spaces
        text = re.sub(r'\n{3,}', '\n\n', text)    # Multiple newlines

        return text.strip()[:8000]

    # ═══════════════════════════════════════════════════════════════
    #  RESULT BUILDING
    # ═══════════════════════════════════════════════════════════════

    def _build_result(
        self,
        query: str,
        instant: Optional[Dict],
        pages: List[Dict]
    ) -> Optional[Dict[str, Any]]:
        """Combine all sources into a structured result."""
        sources = []
        text_pieces = []
        confidence = 0.0

        # Add instant answer (highest quality)
        if instant and instant.get("answer"):
            text_pieces.append(f"[Instant Answer] {instant['answer']}")
            sources.append(instant.get("source", ""))
            confidence = max(confidence, 0.85)

        # Add page snippets and content
        for page in pages:
            if page.get("snippet"):
                text_pieces.append(f"[{page['title']}] {page['snippet']}")
            if page.get("content"):
                # Extract most relevant sentences
                relevant = self._extract_relevant(query, page["content"])
                if relevant:
                    text_pieces.append(relevant)
            sources.append(page.get("url", ""))
            confidence = max(confidence, 0.70)

        if not text_pieces:
            return None

        combined_text = "\n\n".join(text_pieces)

        # Build best answer from most informative piece
        best_answer = self._extract_best_answer(query, text_pieces)

        return {
            "best_answer":   best_answer,
            "combined_text": combined_text[:6000],
            "sources":       [s for s in sources if s],
            "confidence":    confidence,
            "result_count":  len(pages)
        }

    def _extract_relevant(self, query: str, text: str, max_chars: int = 1500) -> str:
        """
        Extractive relevance: pick sentences most related to the query.
        No AI — uses keyword overlap scoring.
        """
        query_words = set(re.findall(r'\b\w{3,}\b', query.lower()))
        sentences   = re.split(r'(?<=[.!?])\s+', text)

        scored = []
        for sent in sentences:
            if len(sent) < 20:
                continue
            words  = set(re.findall(r'\b\w{3,}\b', sent.lower()))
            overlap = len(query_words & words)
            if overlap > 0:
                scored.append((overlap, sent))

        scored.sort(reverse=True)
        result = " ".join(s for _, s in scored[:5])
        return result[:max_chars]

    def _extract_best_answer(self, query: str, pieces: List[str]) -> str:
        """Pick the single most informative piece as the answer."""
        if not pieces:
            return ""

        # Prefer instant answers
        for piece in pieces:
            if piece.startswith("[Instant Answer]"):
                return piece.replace("[Instant Answer] ", "")

        # Otherwise, pick longest relevant piece
        query_words = set(re.findall(r'\b\w{3,}\b', query.lower()))
        best = max(
            pieces,
            key=lambda p: len(set(re.findall(r'\b\w{3,}\b', p.lower())) & query_words)
        )
        # Strip source tag
        best = re.sub(r'^\[[^\]]+\]\s*', '', best)
        return best[:2000]

    # ═══════════════════════════════════════════════════════════════
    #  CACHE
    # ═══════════════════════════════════════════════════════════════

    def _get_cached(self, query: str) -> Optional[Dict]:
        qhash = self._hash(query)
        row = self.conn.execute(
            "SELECT * FROM search_cache WHERE query_hash = ?", (qhash,)
        ).fetchone()
        if not row:
            return None

        # Check TTL
        cached_at = datetime.fromisoformat(row["cached_at"])
        age_hours = (datetime.utcnow() - cached_at).total_seconds() / 3600
        if age_hours > self.CACHE_TTL_HOURS:
            self.conn.execute(
                "DELETE FROM search_cache WHERE query_hash = ?", (qhash,)
            )
            self.conn.commit()
            return None

        return {
            "best_answer":   row["best_answer"],
            "combined_text": row["combined_text"],
            "sources":       json.loads(row["source_urls"]),
            "confidence":    row["confidence"],
            "from_cache":    True
        }

    def _cache_result(self, query: str, result: Dict):
        qhash = self._hash(query)
        self.conn.execute("""
            INSERT OR REPLACE INTO search_cache
                (query_hash, query_text, results, combined_text,
                 best_answer, confidence, source_urls, cached_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            qhash,
            query,
            json.dumps(result),
            result.get("combined_text", ""),
            result.get("best_answer", ""),
            result.get("confidence", 0.7),
            json.dumps(result.get("sources", [])),
            datetime.utcnow().isoformat()
        ))
        self.conn.commit()

    @staticmethod
    def _hash(text: str) -> str:
        return hashlib.sha256(text.strip().lower().encode()).hexdigest()[:16]
