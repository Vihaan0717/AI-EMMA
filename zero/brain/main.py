"""
PROJECT ZERO — Cloud Brain
FastAPI server running on Oracle Cloud
Handles all requests from JARVIS + ARION
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import Dict, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel, Field
import redis.asyncio as aioredis

from brain.groq_engine import GroqEngine
from brain.hf_engine import HFEngine
from brain.router import PersonalityRouter
from supabase.client import SupabaseMemory

# ─── Logging ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s"
)
logger = logging.getLogger("ZeroBrain")

# ─── Global Instances ─────────────────────────────────────
groq: Optional[GroqEngine] = None
hf: Optional[HFEngine] = None
memory: Optional[SupabaseMemory] = None
router: Optional[PersonalityRouter] = None
redis_client: Optional[aioredis.Redis] = None


# ─── Lifespan ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown"""
    global groq, hf, memory, router, redis_client

    logger.info("🚀 Zero Brain starting...")

    # Initialize services
    try:
        groq = GroqEngine()
        await groq.initialize()
        logger.info("✅ Groq AI ready")
    except Exception as e:
        logger.warning(f"Groq init failed: {e}")

    try:
        hf = HFEngine()
        await hf.initialize()
        logger.info("✅ HuggingFace ready")
    except Exception as e:
        logger.warning(f"HF init failed: {e}")

    try:
        memory = SupabaseMemory()
        await memory.initialize()
        logger.info("✅ Supabase memory ready")
    except Exception as e:
        logger.warning(f"Supabase init failed: {e}")

    try:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        redis_client = aioredis.from_url(
            redis_url, decode_responses=True
        )
        await redis_client.ping()
        logger.info("✅ Redis ready")
    except Exception as e:
        logger.warning(f"Redis init failed: {e}")

    router = PersonalityRouter(
        groq=groq, hf=hf,
        memory=memory, redis=redis_client
    )

    logger.info("✅ Zero Brain ONLINE")
    yield

    # Shutdown
    logger.info("🛑 Zero Brain shutting down...")
    if redis_client:
        await redis_client.aclose()


# ─── App ──────────────────────────────────────────────────
app = FastAPI(
    title="Project Zero — Cloud Brain",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)
app.add_middleware(GZipMiddleware, minimum_size=1000)


# ─── Models ───────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    sender: str = Field(default="user", max_length=100)
    source: str = Field(default="api")
    personality: str = Field(default="auto")
    session_id: Optional[str] = None
    language: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    personality: str
    emotion: str
    intent: str
    language: str
    confidence: float
    processing_ms: float
    session_id: str
    timestamp: str

class DumpRequest(BaseModel):
    content: str = Field(..., min_length=1)
    category: str = Field(default="general")
    tags: list = Field(default_factory=list)
    sender: str = Field(default="user")

class HealthResponse(BaseModel):
    status: str
    services: Dict
    uptime_seconds: float
    timestamp: str


# ─── Startup time ─────────────────────────────────────────
_start_time = datetime.now()


# ─── Routes ───────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """System health check — called by watchdog"""
    services = {
        "groq": groq is not None and groq.is_ready,
        "huggingface": hf is not None and hf.is_ready,
        "supabase": memory is not None and memory.is_ready,
        "redis": False
    }

    if redis_client:
        try:
            await redis_client.ping()
            services["redis"] = True
        except:
            pass

    all_ok = services["groq"] or services["huggingface"]
    uptime = (datetime.now() - _start_time).total_seconds()

    return HealthResponse(
        status="healthy" if all_ok else "degraded",
        services=services,
        uptime_seconds=uptime,
        timestamp=datetime.now().isoformat()
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """
    Main chat endpoint.
    Called by JARVIS UI, ARION WhatsApp, Telegram bot.
    """
    if not router:
        raise HTTPException(503, "Brain not ready")

    try:
        result = await router.process(
            message=req.message,
            sender=req.sender,
            source=req.source,
            personality=req.personality,
            session_id=req.session_id
        )
        return ChatResponse(**result)
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(500, f"Processing error: {str(e)}")


@app.post("/dump")
async def dump_memory(req: DumpRequest):
    """
    The Vault Drop Zone.
    Drop any info here - Zero remembers it semantically.
    """
    if not memory:
        raise HTTPException(503, "Memory not ready")

    try:
        result = await memory.store_dump(
            content=req.content,
            category=req.category,
            tags=req.tags,
            sender=req.sender
        )
        return {
            "status": "stored",
            "id": result,
            "message": "Memory stored successfully"
        }
    except Exception as e:
        logger.error(f"Dump error: {e}")
        raise HTTPException(500, str(e))


@app.get("/search")
async def search_memory(q: str, limit: int = 5):
    """Semantic search across all memories"""
    if not memory:
        raise HTTPException(503, "Memory not ready")

    try:
        results = await memory.semantic_search(q, limit=limit)
        return {"results": results, "query": q}
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(500, str(e))


@app.get("/stats")
async def get_stats():
    """System statistics"""
    stats = {
        "uptime_seconds": (
            datetime.now() - _start_time
        ).total_seconds(),
        "timestamp": datetime.now().isoformat()
    }

    if memory:
        stats["memory"] = await memory.get_stats()

    if redis_client:
        try:
            info = await redis_client.info("server")
            stats["redis_uptime"] = info.get(
                "uptime_in_seconds", 0
            )
        except:
            pass

    return stats


@app.post("/webhook/telegram")
async def telegram_webhook(data: dict):
    """Telegram webhook from n8n"""
    if not router:
        return {"ok": False}

    try:
        msg = data.get("message", {})
        text = msg.get("text", "")
        chat_id = msg.get("chat", {}).get("id")
        username = msg.get("from", {}).get("username", "user")

        if not text or not chat_id:
            return {"ok": True}

        result = await router.process(
            message=text,
            sender=username,
            source="telegram",
            personality="arion"
        )

        # Send back via Telegram API
        import aiohttp
        async with aiohttp.ClientSession() as session:
            token = os.getenv("TELEGRAM_TOKEN")
            await session.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": result["response"],
                    "parse_mode": "Markdown"
                }
            )

        return {"ok": True}
    except Exception as e:
        logger.error(f"Telegram webhook error: {e}")
        return {"ok": False, "error": str(e)}
