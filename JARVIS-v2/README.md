# 🧠 ARION — Sentient Mirror V3 (Free Stack)

> A 100% locally-run digital twin that texts like you, thinks like you, and remembers like you.  
> Built on **Ollama + WhatsApp + Telegram** with zero paid APIs.

---

## 📖 Table of Contents

1. [What Is ARION?](#what-is-arion)
2. [Architecture Overview](#architecture-overview)
3. [Project Structure](#project-structure)
4. [Core Systems](#core-systems)
5. [Agent Pipeline](#agent-pipeline)
6. [Memory Architecture](#memory-architecture)
7. [WhatsApp Bridge](#whatsapp-bridge)
8. [Telegram Integration](#telegram-integration)
9. [Language & Cultural Intelligence](#language--cultural-intelligence)
10. [Privacy & Security](#privacy--security)
11. [Configuration](#configuration)
12. [Setup & Running](#setup--running)
13. [Admin Commands](#admin-commands)
14. [Known State & Tech Debt](#known-state--tech-debt)

---

## What Is ARION?

ARION is a **sentient digital twin** — an AI that runs on your local machine and acts as *you* in WhatsApp/Telegram conversations. It is not a generic chatbot. It is trained on:

- Your **personality** (persona config JSONs)
- Your **texting style** (Tenglish / Telugu / Hindi dialect awareness)
- Your **relationships** (who each person is to you, how to talk to them)
- Your **knowledge** (Obsidian-style vault of everything you/it learns)
- Your **memory** (live working memory, short-term, episodic, and semantic long-term)

Everything runs **locally** — no OpenAI, no cloud APIs.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                   START_ARION.bat                   │
│   (1) Checks Ollama ─ (2) Boots Python Core         │
│   (3) Boots WhatsApp Bridge (Node.js)               │
└──────────────┬──────────────────────────────────────┘
               │
    ┌──────────▼──────────┐     ┌─────────────────────┐
    │   arion/core/        │     │  arion/whatsapp/     │
    │   arion_core.py      │◄────│  whatsapp_listener.js│
    │   (Free Stack Brain) │     │  (WhatsApp Web.js)   │
    └──────────┬──────────┘     └─────────────────────┘
               │
    ┌──────────▼──────────────────────────────────────┐
    │                  MessageBus                      │
    │   (Async pub/sub backbone — message_bus.py)      │
    └──────┬──────────────────────────────────────────┘
           │
    ┌──────▼──────────────────────────────────────────────────────────┐
    │                 AGENT PIPELINE (Orchestrator)                    │
    │                                                                  │
    │  A1: LanguageEngine  →  Normalize script, detect dialect        │
    │  A2: MemoryManager   →  Decode slang from vocab                 │
    │  A3: ComprehensionEngine → Build semantic bridge (Ollama)       │
    │  A4: IntentEngine    →  Tier-based intent + emotion detection   │
    │  A4.5: RAGEngine     →  Retrieve relevant memories (ChromaDB)   │
    │  A5: Ollama LLM      →  Generate response                       │
    │  A6: LanguageEngine  →  Stylize to dialect                      │
    └───────────────────┬─────────────────────────────────────────────┘
                        │
           ┌────────────▼───────────────────┐
           │  WhatsApp / Telegram Channel    │
           └────────────────────────────────┘
```

---

## Project Structure

```
JARVIS-v2/
├── START_ARION.bat              # One-click launcher (Windows)
├── .env                         # Environment config (secrets & paths)
├── package.json                 # Root Node.js package
│
└── arion/                       # Main Python package
    ├── main.py                  # Async agent boot loop (multi-agent mode)
    ├── requirements.txt         # Python dependencies
    ├── setup.ps1                # PowerShell setup helper
    ├── bootstrap_vault.py       # One-time Obsidian vault scaffolding
    │
    ├── core/                    # Core infrastructure
    │   ├── arion_core.py        # Free Stack Brain (socket server)
    │   ├── message_bus.py       # Async pub/sub backbone
    │   ├── base_agent.py        # BaseAgent class (all agents extend this)
    │   ├── free_ai_engine.py    # Ollama API wrapper
    │   ├── intent_engine.py     # Deep intent classifier (joke/distress/roleplay)
    │   ├── smart_responses.py   # Pre-written smart reply bank
    │   ├── response_quality.py  # Output quality validator & fallback
    │   ├── memory_consolidator.py # 24-hour memory reflection loop
    │   └── persona.py           # Persona loader
    │
    ├── agents/                  # All live agents (run in async loop)
    │   ├── orchestrator.py      # 🧠 Central brain — full 6-agent pipeline
    │   ├── language_engine.py   # Script normalization + dialect stylization
    │   ├── intent_engine.py     # Tiered intent classification (A4)
    │   ├── comprehension_engine.py # Semantic bridge via Ollama (A3)
    │   ├── memory_manager.py    # 3-tier memory store (SQLite + ChromaDB + Vault)
    │   ├── memory_learner.py    # Passive profile builder from conversation
    │   ├── knowledge_ingestion_engine.py # "learn X" → Vault pipeline
    │   ├── knowledge_injector.py # Knowledge → Ollama context injection
    │   ├── knowledge_retrieval.py # Vault search interface
    │   ├── telegram_center.py   # Telegram bot integration
    │   ├── whatsapp_bridge.py   # Bridge queue reader (connects JS↔Python)
    │   ├── voice_engine.py      # Whisper STT + edge-tts TTS
    │   ├── privacy_shield.py    # 4-tier privacy firewall
    │   ├── curiosity_engine.py  # Asks gap-filling questions naturally
    │   ├── connection_insight_engine.py # Pattern-based relationship insights
    │   ├── emotion_engine.py    # Emotion state tracker
    │   ├── persona_engine.py    # Adaptive persona loader
    │   ├── prediction_engine.py # Predictive response prep
    │   ├── resource_governor.py # Load shedding (CPU governor)
    │   ├── system_monitor.py    # CPU/RAM/GPU watchdog
    │   ├── agent_monitor.py     # Heartbeat + zombie detection
    │   ├── coding_agent.py      # Code generation capability
    │   ├── digital_twin.py      # Digital twin sync layer
    │   ├── intake_watcher.py    # File intake watcher (for bulk ingestion)
    │   ├── learning_scheduler.py # Scheduled background learning
    │   └── life_manager.py      # Daily life context manager
    │
    ├── brain/                   # Long-term brain modules
    │   ├── rag_engine.py        # ChromaDB RAG retrieval (Hippocampus)
    │   ├── reinforcement_engine.py # Preference learning from feedback
    │   └── vault_brain.py       # Obsidian vault writer (all 4 memory tiers)
    │
    ├── config/                  # Personality & system config JSONs
    │   ├── system_config.json   # Core settings (Ollama URL, model, DB paths)
    │   ├── persona_core.json    # Core personality definition
    │   ├── persona_adaptive.json # Real-time adaptive persona state
    │   ├── owner_identity.json  # Owner name, texting style, relationships
    │   ├── cultural_intelligence.json # Cultural context rules
    │   ├── conversation_examples.json # Example Tenglish conversations
    │   ├── vocabulary_telugu.json # ~1000+ Telugu/Tenglish vocabulary
    │   └── vocabulary_hindi.json  # ~1000+ Hindi vocabulary
    │
    ├── knowledge/               # Vault loader & semantic search
    │   ├── vault_loader.py      # Loads + searches Obsidian vault (FAISS)
    │   ├── vault_index.json     # FAISS index metadata
    │   └── vault_embeddings.index # FAISS vector index
    │
    ├── knowledge_vault/         # Obsidian VAULT (live, user-editable)
    │   └── (Brain/Working, Brain/ShortTerm, Brain/Episodic,
    │         Brain/Semantic, Knowledge/*, People/*)
    │
    ├── language/                # Language processing
    │   ├── free_translator.py   # Argos offline translator
    │   └── slang/
    │       ├── telugu.json      # Regional Telugu slang DB
    │       └── hindi.json       # Regional Hindi slang DB
    │
    ├── screen/                  # Screen awareness
    │   ├── screen_watcher.py    # Periodic screenshot capture
    │   ├── screen_learner.py    # OCR → knowledge extraction
    │   └── screen_indicator.py  # Visual activity indicator
    │
    ├── search/
    │   └── free_search.py       # DuckDuckGo search (no API key)
    │
    ├── voice/
    │   └── free_voice.py        # Whisper STT + edge-tts/pyttsx3 TTS
    │
    ├── memory/                  # (Empty — memory lives in MemoryManager agent)
    │
    └── whatsapp/                # Node.js WhatsApp bridge
        ├── whatsapp_listener.js # Main WhatsApp Web.js listener
        ├── whitelist.json       # Approved contact list
        ├── blocked.json         # Auto/manual blocked numbers
        ├── package.json
        ├── .env                 # WhatsApp-specific env (MongoDB, admin number)
        ├── config/
        │   └── database.js      # MongoDB connection
        ├── handlers/
        │   ├── languageHandler.js  # JS-side dialect + intent detection
        │   └── aiHandler.js        # Routes messages to Python core (TCP)
        ├── models/
        │   ├── Contact.js          # MongoDB contact schema
        │   └── Conversation.js     # MongoDB conversation schema
        └── utils/
```

---

## Core Systems

### 1. `arion_core.py` — Free Stack Brain
The original standalone brain (runs as a TCP socket server on port `5006`). This is the entry point launched by `START_ARION.bat`. It boots:
- **FreeAIEngine** — Ollama API wrapper (model selection per topic)
- **VaultLoader** — FAISS semantic search over Obsidian vault
- **FreeSearchEngine** — DuckDuckGo live web search
- **ScreenWatcher** + **ScreenLearner** — Screen OCR → vault learning
- **MemoryConsolidator** — 24-hour reflection loop
- **IntentEngine** — Deep joke/distress/roleplay classifier
- **SmartResponses** — Pre-written reply bank for predictable scenarios
- **ResponseQualityController** — Output validator with auto-retry

### 2. `main.py` — Multi-Agent Async Mode
Alternative entry point that boots every agent as an async coroutine connected via `MessageBus`. This is the full production pipeline. Both modes can run — `arion_core.py` handles HTTP from WhatsApp, `main.py` handles the full agent pipeline over message channels.

### 3. `MessageBus` — Async Backbone
Pub/sub system with:
- **Channels**: ORCHESTRATOR, LANGUAGE, MEMORY, INTENT, COMPREHENSION, WHATSAPP, TELEGRAM, VOICE
- **Request/response** pattern via correlation IDs
- **Priority queuing**

---

## Agent Pipeline

When a WhatsApp message arrives from the owner:

| Step | Agent | Action |
|------|-------|--------|
| A1 | `LanguageEngine` | Normalize script, detect dialect (Telugu/Hindi/General), tokenize |
| A2 | `MemoryManager` | Decode slang tokens using vocabulary DBs |
| A3 | `ComprehensionEngine` | Build semantic English bridge via Ollama |
| A4 | `IntentEngine` | 4-tier intent classification: topic, emotion, dialect, response style |
| A4.5 | `RAGEngine` | Retrieve relevant memories from ChromaDB if memory question detected |
| A5 | Ollama LLM | Generate response with full context prompt |
| A6 | `LanguageEngine` | Stylize response to detected dialect |

For **proxy messages** (someone texting the owner's WhatsApp number):
- Same A1→A6 pipeline
- `PrivacyShield` is applied before A5
- Response is sent to the person **and** a notification forwarded to the owner

---

## Memory Architecture

ARION has a **4-tier memory system**, all written as Obsidian markdown `.md` files in `knowledge_vault/`:

| Tier | File Location | Lifespan | Purpose |
|------|---------------|----------|---------|
| **Working** | `Brain/Working/` | Per-conversation | Real-time conversation buffer (last 10 turns) |
| **Short-Term** | `Brain/ShortTerm/` | 7 days | Topic-based mention tracking |
| **Episodic** | `Brain/Episodic/` | Forever | High-emotion or significant moments |
| **Semantic** | `Brain/Semantic/` | Forever | Confidence-scored facts about people/world |

**Additional stores:**
- **SQLite** (`arion/data/memory.db`) — structured conversation log
- **ChromaDB** (`arion/data/chromadb/`) — vector embeddings for semantic RAG
- **Obsidian Vault** (`arion/vault/` or `knowledge_vault/`) — navigable wikilink graph

**Memory writes are managed by:**
- `VaultBrain` — the single writer interface
- `MemoryManager` agent — routes `store_conversation`, `store_emotion`, `decode_slang`, `learn_slang` commands from the bus

---

## WhatsApp Bridge

The WhatsApp layer is a Node.js app (`arion/whatsapp/`) using [whatsapp-web.js](https://wwebjs.dev/).

**Architecture:**
1. `whatsapp_listener.js` receives messages via WhatsApp Web puppeteer
2. JS-side language/dialect/intent is detected (`languageHandler.js`)
3. Message is forwarded to Python core via **TCP socket** (`aiHandler.js`)
4. Python core generates response and returns it
5. Response is sent back to the WhatsApp contact

**Security:**
- **Whitelist**: only approved contacts get replies (`whitelist.json`)
- **Blocklist**: auto-blocked spammers + manual blocks (`blocked.json`)
- **Spam detection**: pattern-matched rules
- Admin is notified of every unknown contact attempting to message

**Key file:** `whatsapp_listener.js`

---

## Telegram Integration

`TelegramCenter` agent handles Telegram bot messages. It:
- Listens for messages to the owner's Telegram bot
- Routes them through the **same Orchestrator pipeline** as WhatsApp
- Supports voice messages (via Whisper STT)
- Used for the primary owner interface during development

Config: `system_config.json` → `telegram_token`, `telegram_owner_chat_id`

---

## Language & Cultural Intelligence

ARION has deep Tenglish (Telugu + English) and Hindi fluency:

| Component | File | Description |
|-----------|------|-------------|
| Telugu Vocabulary | `config/vocabulary_telugu.json` | 1000+ words across greetings, slang, sarcasm, emotions, daily phrases |
| Hindi Vocabulary | `config/vocabulary_hindi.json` | 1000+ Hindi words |
| Telugu Slang DB | `language/slang/telugu.json` | Regional slang dictionary |
| Hindi Slang DB | `language/slang/hindi.json` | Regional Hindi slang |
| Conversation Examples | `config/conversation_examples.json` | Real Tenglish example Q&A pairs injected into LLM prompt |
| Cultural Intelligence | `config/cultural_intelligence.json` | Cultural rules (festival greetings, social norms, etc.) |

**Dialect detection flow:**
1. A1 `LanguageEngine` tokenizes and confidence-scores (Telugu vs Hindi vs General)
2. A4 `IntentEngine` also detects `dialect_to_reply_in`
3. A1 wins if confidence ≥ 0.30
4. A6 `LanguageEngine` stylizes the final output to the winning dialect

**Nuclear Slang Shield:**
Hard-coded keyword→response map for regional profanity (bypasses all AI filters, replies instantly).

---

## Privacy & Security

`PrivacyShield` (4-tier) protects against:

| Tier | What It Blocks |
|------|----------------|
| T1 | Identity — who owns this number, is this AI, who built this |
| T2 | Personal info — location, work, family, health |
| T3 | Sensitive — money, schedule, relationships |
| T4 | Technical — Ollama, API, Python, model names, localhost |

**For proxy contacts** (people texting the owner's number):
- Blocked questions trigger a culturally-appropriate deflection
- Owner receives an alert with what was asked

**Owner permission system:**
- Owner can grant specific contacts access to specific topics:
  `grant [contact] access to [topic]` (parsed by `parse_owner_permission_command`)

**Output filter:** All AI responses are scanned for forbidden technical terms before delivery.

---

## Configuration

### `.env` (root)
```env
OLLAMA_MODEL=llama3.1
OLLAMA_FAST_MODEL=gemma3:1b
OLLAMA_URL=http://localhost:11434
VOICE_ENABLED=false
WHISPER_MODEL=base
VAULT_PATH=C:\...\knowledge_vault
SCREEN_WATCH=true
SCREEN_INTERVAL=15
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
ARION_PORT=5006
ADMIN_NUMBER=919154716156
```

### `arion/config/system_config.json`
```json
{
  "ollama_url": "http://localhost:11434",
  "model_name": "llama3.1",
  "heartbeat_interval_seconds": 10,
  "zombie_multiplier": 3,
  "dead_multiplier": 6,
  "max_memory_history": 20,
  "db_paths": {
    "sqlite": "arion/data/memory.db",
    "chroma": "arion/data/chromadb",
    "obsidian_vault": "arion/vault"
  },
  "bridge_queue": "arion/data/bridge_queue",
  "telegram_token": "...",
  "telegram_owner_chat_id": "..."
}
```

### `arion/whatsapp/whitelist.json`
Controls who the WhatsApp bridge replies to. Key fields:
- `enabled` — toggle whitelist on/off
- `numbers` — approved phone numbers
- `names` — approved contact names (partial match)
- `settings.reply_to_saved_contacts_only` — only reply to saved contacts
- `settings.reply_to_groups` — enable/disable group replies

---

## Setup & Running

### Prerequisites
- **Ollama** running locally with `llama3.1` model pulled
- **Python 3.11+** with venv
- **Node.js 18+**
- **Tesseract OCR** (for screen watching)
- **MongoDB** (optional, for WhatsApp conversation history)

### First Time Setup
```powershell
# 1. Install Python deps
cd arion
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. Install Node deps
cd whatsapp
npm install

# 3. Bootstrap the vault structure
cd ..
python bootstrap_vault.py

# 4. Edit .env with your paths and Telegram token
```

### Running
```
Double-click: START_ARION.bat
```
This will:
1. Check Ollama is running
2. Kill any old Python/Node processes
3. Verify vault path
4. Start `arion_core.py` (main brain, socket server)
5. Start WhatsApp bridge (`npm start` in `arion/whatsapp/`)

### Running Multi-Agent Mode (Experimental)
```powershell
cd arion
python main.py
```

---

## Admin Commands

These are sent **to the owner's own WhatsApp number** (admin self-commands):

| Command | Effect |
|---------|--------|
| `APPROVE [number]` | Add a number to the whitelist |
| `BLOCK [number]` | Block a number |
| `STATUS` | View whitelist/blocklist stats |
| `feedback: [text]` | Teach ARION to adjust its tone |
| `learn slang word [word] means [meaning]` | Add slang to ARION's vocabulary |
| `learn [Topic]` | Trigger knowledge ingestion (Wikipedia/YouTube) |

---

## Known State & Tech Debt

| Area | Status | Notes |
|------|--------|-------|
| **Dual boot modes** | ⚠️ Active | `arion_core.py` and `main.py` are two partially overlapping entry points. The `START_ARION.bat` boots `arion_core.py`. The full multi-agent pipeline is in `main.py`. These should eventually be unified. |
| **Resource Governor** | ✅ Active | CPU load shedding pauses Prediction, Intake, and ComprehensionEngine at >85% CPU |
| **Voice** | ⚠️ Disabled | `VOICE_ENABLED=false`. Whisper + edge-tts are installed but off by default due to resource cost |
| **Screen Watcher** | ✅ Active | Takes screenshots every 15s, extracts text via OCR, learns from it |
| **MongoDB** | Optional | WhatsApp bridge can use MongoDB for conversation history. Falls back to in-memory if not running |
| **Temp WAV files** | 🗑️ Cleanup needed | `temp_voice_*.wav` files accumulate in the project root |
| **RAGEngine min_relevance** | Note | Set to 0.45 — tune if memory recall feels too sparse |
| **Curiosity Engine throttle** | Note | Only asks questions every N turns and not during high-emotion states |

---

*Built with ❤️ by Anger Kabir — ARION is his digital soul.*
