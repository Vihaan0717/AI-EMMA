"""
KnowledgeInjector — Semantic memory writer for ARION.

Features:
  - Automated YAML frontmatter with tags
  - Knowledge categorization (History, Science, etc.)
  - MOC connectivity (Links to Knowledge/Index and root Index)
  - Date-prefixed filenames to prevent overwrites
"""

import asyncio
import re
import time
from datetime import datetime, timezone
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import wikipedia
from core.base_agent import BaseAgent
from core.message_bus import Channel, Message


# Maps common Wikipedia category keywords to Knowledge subfolders
_WIKI_CATEGORY_MAP = {
    "history":     "History",
    "religion":    "Religion",
    "philosophy":  "Philosophy",
    "science":     "Science",
    "music":       "Music",
    "film":        "Movies",
    "movie":       "Movies",
    "television":  "TVSeries",
    "book":        "Books",
    "novel":       "Books",
}


def _wiki_folder(title: str) -> str:
    tl = title.lower()
    for keyword, folder in _WIKI_CATEGORY_MAP.items():
        if keyword in tl:
            return folder
    return "General"


def _safe_filename(title: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "", title)[:50] or "web_digest"


class KnowledgeInjector(BaseAgent):
    def __init__(self):
        super().__init__("KnowledgeInjector", [Channel.ORCHESTRATOR])

    async def run_loop(self):
        while self.running:
            msg = await self.get_next_message(timeout=1.0)
            if msg:
                await self.handle_message(msg)

    async def handle_message(self, message: Message):
        if message.action != "inject_url":
            return

        url    = message.payload.get("url", "")
        source = message.payload.get("source", "unknown")
        if not url:
            return

        print(f"[KnowledgeInjector] Scraping: {url}")

        content  = None
        metadata = {"url": url, "source": source}

        # ── Source routing ────────────────────────────────────────────────
        if "youtube.com" in url or "youtu.be" in url:
            content             = await self._scrape_youtube(url)
            metadata["type"]    = "youtube"
            metadata["title"]   = "YouTube Video Transcript"
            metadata["folder"]  = "Injected/Summaries"
            metadata["tags"]    = ["injected", "youtube", "semantic"]

        elif "wikipedia.org" in url:
            raw_title           = url.split("/")[-1].replace("_", " ")
            content             = await self._scrape_wikipedia(url)
            metadata["type"]    = "wikipedia"
            metadata["title"]   = raw_title
            metadata["folder"]  = f"Knowledge/{_wiki_folder(raw_title)}"
            metadata["tags"]    = ["injected", "wikipedia", "semantic",
                                    _wiki_folder(raw_title).lower()]

        else:
            content             = await self._scrape_general(url)
            metadata["type"]    = "web"
            metadata["title"]   = _safe_filename(url.split("/")[-1] or "article")
            metadata["folder"]  = "Injected/Summaries"
            metadata["tags"]    = ["injected", "web", "semantic"]

        if not content:
            if message.requires_response:
                await self.respond_to(
                    message, "injection_failed",
                    {"url": url, "reason": "content_not_extractable"}
                )
            return

        # ── Build vault note ──────────────────────────────────────────────
        title    = metadata["title"]
        tags     = metadata["tags"]
        folder   = metadata["folder"]
        src_type = metadata["type"]

        # Date-prefixed filename prevents overwrites on re-inject
        date_prefix = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
        filename    = f"{date_prefix}_{_safe_filename(title)}.md"

        # YAML frontmatter — visible in Obsidian reading view
        tag_str = "\n".join(f"  - {t}" for t in tags)
        frontmatter = (
            f"---\n"
            f"title: \"{title}\"\n"
            f"source: {url}\n"
            f"type: {src_type}\n"
            f"injected: {date_prefix}\n"
            f"tags:\n{tag_str}\n"
            f"---\n\n"
        )

        # MOC backlinks — keeps graph connected
        backlinks = (
            f"**Backlinks:** [[Knowledge/Index]] | [[Index]]\n\n"
            f"---\n\n"
        )

        vault_content = frontmatter + f"# {title}\n\n" + backlinks + content

        asyncio.create_task(
            self.send(
                to_channel=Channel.MEMORY,
                action="write_vault",
                payload={
                    "path":    f"{folder}/{filename}",
                    "content": vault_content
                }
            )
        )

        if message.requires_response:
            await self.respond_to(
                message, "injection_success",
                {
                    "url":     url,
                    "title":   title,
                    "summary": content[:1000] + "..."
                }
            )

    # ── Scrapers (unchanged logic) ───────────────────────

    async def _scrape_youtube(self, url: str) -> str:
        loop = asyncio.get_event_loop()
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
            if not video_id_match:
                return None
            video_id = video_id_match.group(1)

            def _sync_fetch():
                api     = YouTubeTranscriptApi()
                fetched = api.fetch(video_id)
                data    = fetched.to_raw_data()
                return " ".join([t["text"] for t in data])

            return await loop.run_in_executor(None, _sync_fetch)
        except Exception as e:
            print(f"[KnowledgeInjector] YouTube Error: {e}")
            return None

    async def _scrape_wikipedia(self, url: str) -> str:
        loop = asyncio.get_event_loop()
        try:
            title = url.split("/")[-1].replace("_", " ")

            def _sync_wiki():
                return wikipedia.summary(title, sentences=15)

            return await loop.run_in_executor(None, _sync_wiki)
        except Exception as e:
            print(f"[KnowledgeInjector] Wikipedia Error: {e}")
            return None

    async def _scrape_general(self, url: str) -> str:
        loop = asyncio.get_event_loop()
        try:
            def _sync_web():
                headers = {
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36"
                    )
                }
                resp  = requests.get(url, headers=headers, timeout=15)
                soup  = BeautifulSoup(resp.text, "html.parser")
                paras = [
                    p.get_text().strip()
                    for p in soup.find_all("p")
                    if len(p.get_text().strip()) > 30
                ]
                return "\n\n".join(paras[:25])

            return await loop.run_in_executor(None, _sync_web)
        except Exception as e:
            print(f"[KnowledgeInjector] Web Error: {e}")
            return None
