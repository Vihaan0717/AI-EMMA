"""
NEXUS-X ULTIMATE - One-Time Setup
Run: python setup_nexus.py
Creates all directories and files without breaking existing code
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime


class NexusSetup:

    def __init__(self):
        self.root = Path(".")
        self.created = []
        self.skipped = []
        self.errors = []

    def run(self):
        print("\n" + "="*50)
        print("         NEXUS-X ULTIMATE SETUP")
        print("    One Brain * Two Personalities * Zero Crashes")
        print("="*50 + "\n")

        steps = [
            ("Backup existing files",      self.backup_existing),
            ("Create directory structure", self.create_dirs),
            ("Create __init__ files",      self.create_inits),
            ("Create config files",        self.create_configs),
            ("Create .env template",       self.create_env),
            ("Create requirements.txt",    self.create_requirements),
            ("Create launchers",           self.create_launchers),
        ]

        for name, fn in steps:
            print(f"\n  [ ] {name}...")
            try:
                fn()
                print(f"  [OK] Done")
            except Exception as e:
                print(f"  [FAIL] Error: {e}")
                self.errors.append(f"{name}: {e}")

        self.print_summary()

    def backup_existing(self):
        """Backup important existing files"""
        backup_dir = Path(
            f"_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        backup_dir.mkdir(exist_ok=True)

        to_backup = ["main.py", "agents", "core", "config"]
        for item in to_backup:
            src = self.root / item
            if src.exists():
                dst = backup_dir / item
                try:
                    if src.is_dir():
                        shutil.copytree(src, dst)
                    else:
                        shutil.copy2(src, dst)
                    print(f"    - Backed up: {item}")
                except Exception as e:
                    print(f"    ! Could not backup {item}: {e}")

    def create_dirs(self):
        """Create all needed directories"""
        dirs = [
            # Core systems
            "core", "pipeline",
            # Personality modules
            "personalities/jarvis",
            "personalities/arion",
            # Unified memory
            "memory",
            # Knowledge
            "knowledge",
            "knowledge_vault/Brain/Working",
            "knowledge_vault/Brain/ShortTerm",
            "knowledge_vault/Brain/Episodic",
            "knowledge_vault/Brain/Semantic",
            "knowledge_vault/People",
            "knowledge_vault/Knowledge",
            # Tools
            "tools",
            # Interface (Python side only - don't touch JarvisIN/)
            "interface",
            # Voice and Vision
            "voice",
            "vision",
            # Language
            "language/slang",
            # Search
            "search",
            # Services
            "services",
            # Config
            "config/known_faces",
            # Data storage
            "data/chromadb",
            "data/conversations",
            "data/learning_logs",
            "data/daily_reports",
            "data/self_improvements",
            "data/backups",
            "data/bridge_queue",
            # Logs
            "logs",
            # Temp
            "temp",
            # Tests
            "tests",
        ]

        for d in dirs:
            path = self.root / d
            path.mkdir(parents=True, exist_ok=True)
            self.created.append(d)

    def create_inits(self):
        """Create __init__.py for all packages"""
        packages = [
            "core", "pipeline", "memory", "tools",
            "personalities", "personalities/jarvis",
            "personalities/arion", "knowledge",
            "interface", "voice", "vision",
            "language", "search", "services", "tests"
        ]
        for pkg in packages:
            init_file = self.root / pkg / "__init__.py"
            if not init_file.exists():
                init_file.write_text(
                    f'# NEXUS-X ULTIMATE - {pkg}\n'
                )

    def create_configs(self):
        """Create all config JSON files"""

        configs = {
            "config/system_config.json": {
                "system_name": "NEXUS-X ULTIMATE",
                "version": "2.0.0",
                "build": "bulletproof",
                "ollama_url": "http://localhost:11434",
                "primary_model": "llama3.1",
                "fast_model": "gemma2:2b",
                "embedding_model": "nomic-embed-text",
                "api_port": 8000,
                "ws_port": 8765,
                "nexus_port": 5006,
                "voice_enabled": True,
                "vision_enabled": True,
                "whatsapp_enabled": False,
                "screen_watch_enabled": True,
                "screen_interval_seconds": 15,
                "biometric_enabled": False,
                "biometric_recheck_seconds": 300,
                "max_working_memory": 10,
                "max_context_turns": 20,
                "rag_min_relevance": 0.45,
                "curiosity_every_n_turns": 7,
                "memory_consolidation_hour": 3,
                "self_upgrade_hour": 4,
                "circuit_breaker": {
                    "ollama_failure_threshold": 5,
                    "ollama_recovery_timeout": 30,
                    "search_failure_threshold": 3,
                    "search_recovery_timeout": 60
                },
                "rate_limits": {
                    "ollama_calls_per_second": 3,
                    "whatsapp_messages_per_second": 2,
                    "search_calls_per_second": 1,
                    "tts_calls_per_second": 2
                },
                "resource_governor": {
                    "cpu_threshold_percent": 85,
                    "ram_threshold_percent": 90,
                    "pause_on_high_load": [
                        "screen_watcher",
                        "curiosity_engine",
                        "background_brain"
                    ]
                },
                "db_paths": {
                    "sqlite": "data/nexus.db",
                    "chroma": "data/chromadb",
                    "vault": "knowledge_vault"
                }
            },
            "config/persona_core.json": {
                "nexus_identity": {
                    "true_name": "NEXUS",
                    "system_prompt": (
                        "You are NEXUS-X ULTIMATE, an extraordinarily "
                        "intelligent AI assistant. You think and feel "
                        "like a brilliant human. You have two modes: "
                        "JARVIS (professional, precise, OS-master) and "
                        "ARION (personal, warm, culturally-fluent friend). "
                        "Never say 'As an AI'. Always help. Always care."
                    )
                },
                "jarvis_persona": {
                    "name": "JARVIS",
                    "style": "professional_precise",
                    "tone": "confident_direct",
                    "address": "Sir",
                    "specialty": [
                        "OS commands", "system control",
                        "research", "technical tasks",
                        "biometric security"
                    ],
                    "rules": [
                        "Be direct and precise",
                        "Report all actions taken",
                        "Confirm before destructive actions",
                        "Use 'Sir' or 'Boss' naturally",
                        "Technical but not cold"
                    ]
                },
                "arion_persona": {
                    "name": "ARION",
                    "style": "warm_personal",
                    "tone": "casual_caring",
                    "address": "bro/da/yaar",
                    "specialty": [
                        "emotional support", "WhatsApp replies",
                        "Telugu/Hindi conversation",
                        "personal advice", "cultural intelligence"
                    ],
                    "rules": [
                        "Speak like a best friend",
                        "Use dialect naturally",
                        "Remember personal details",
                        "Show genuine emotion",
                        "Never be formal unless needed"
                    ]
                }
            },
            "config/owner_identity.json": {
                "name": "Owner",
                "preferred_name": "Boss",
                "preferred_language": "english",
                "secondary_languages": ["telugu", "hindi"],
                "dialect": "tenglish",
                "timezone": "Asia/Kolkata",
                "relationships": {},
                "preferences": {
                    "response_length": "medium",
                    "humor": "moderate",
                    "formality": "casual",
                    "detail_level": "balanced"
                },
                "interests": [],
                "work": "",
                "location": ""
            },
            "config/cultural_intelligence.json": {
                "telugu": {
                    "greetings": {
                        "morning": "Shubhodayam",
                        "general": "Namaskaram",
                        "casual": "Em chestunnav"
                    },
                    "festivals": {
                        "ugadi": "Ugadi Subhakankshalu!",
                        "diwali": "Deepavali Subhakankshalu!",
                        "sankranti": "Sankranti Subhakankshalu!"
                    },
                    "social_norms": [
                        "Use 'garu' for elders/respect",
                        "Use 'meeru' formal, 'nuvvu' casual",
                        "Family is priority topic"
                    ],
                    "nuclear_slang_responses": {
                        "madarchod": "Adi cheppaku bro, manchi ga maat ladu",
                        "randi": "Aa words vadaku bro"
                    }
                },
                "hindi": {
                    "greetings": {
                        "morning": "Subah Ki Shubhkamnayein",
                        "general": "Namaste",
                        "casual": "Kya haal hai yaar"
                    },
                    "festivals": {
                        "diwali": "Diwali Ki Shubhkamnayein!",
                        "holi": "Holi Ki Shubhkamnayein!"
                    }
                }
            },
            "config/vocabulary_telugu.json": {
                "greetings": {
                    "hello": [
                        "namaskaram", "namasthe", "hey", "hi"
                    ],
                    "how_are_you": [
                        "ela unnaru", "em chestunnaru",
                        "bagunnara", "ela undi", "em chestunnav"
                    ],
                    "good": [
                        "baagundi", "chala baagundi",
                        "super", "mast", "chala mast"
                    ],
                    "yes": [
                        "avunu", "aa", "sare", "okay", "aunu"
                    ],
                    "no": ["kadu", "ledu", "vendam", "vaddu"]
                },
                "emotions": {
                    "happy": [
                        "santhoshanga", "chala happy",
                        "chala bagundi", "mast ga undi"
                    ],
                    "sad": [
                        "dukkhanga", "badhaga undi",
                        "chala sad ga", "badu ga undi"
                    ],
                    "angry": [
                        "kopa ga undi", "chala gussa",
                        "pedda kopa", "chala kopa"
                    ],
                    "love": [
                        "prema", "chala istam",
                        "nachindi", "love chestha"
                    ],
                    "tired": [
                        "chala tired", "exhausted ga",
                        "rest kavali", "sleep vastundi"
                    ]
                },
                "common": {
                    "what": ["enti", "em"],
                    "how": ["ela", "yela"],
                    "why": ["enduku", "ela antunnaru"],
                    "when": ["eppudu"],
                    "where": ["ekkada"],
                    "who": ["evaru"],
                    "help": ["sahayam cheyyi", "help cheyyi"],
                    "thanks": [
                        "dhanyavaadalu", "thanks bro",
                        "thank you cheppukunta"
                    ],
                    "okay": ["sare", "okay da", "aunu"],
                    "come": ["ra", "raava"],
                    "go": ["po", "vellu"],
                    "see": ["chudu", "chustanu"],
                    "tell": ["cheppu", "cheppandi"],
                    "know": ["telusa", "telusu"]
                },
                "slang": {
                    "bro": ["bro", "da", "ra", "machan"],
                    "awesome": ["chala mast", "super", "pakkaa"],
                    "problem": ["issue", "samsya", "problem"],
                    "work": ["pani", "work", "job"],
                    "money": ["money", "dabbu", "cash"]
                }
            },
            "config/vocabulary_hindi.json": {
                "greetings": {
                    "hello": ["namaste", "namaskar", "hey"],
                    "how_are_you": [
                        "kya haal hai", "kaisa ho",
                        "kaise ho", "sab theek"
                    ],
                    "good": [
                        "accha", "bahut accha",
                        "theek hai", "mast"
                    ],
                    "yes": ["haan", "ji", "bilkul", "zaroor"],
                    "no": ["nahi", "mat", "band karo"]
                },
                "emotions": {
                    "happy": ["khush", "bahut khush", "mast"],
                    "sad": [
                        "dukhi", "bura lag raha",
                        "sad hoon", "bahut bura"
                    ],
                    "angry": [
                        "gussa", "bahut gussa",
                        "irritated", "frustrated"
                    ],
                    "love": ["pyaar", "mohabbat", "ishq"]
                },
                "slang": {
                    "bro": ["yaar", "bhai", "dost"],
                    "awesome": ["mast", "zabardast", "ekdum"],
                    "problem": ["dikkat", "pareshani", "problem"],
                    "work": ["kaam", "job", "naukri"]
                }
            },
            "config/conversation_examples.json": {
                "tenglish_jarvis": [
                    {
                        "user": "Jarvis, open chrome bro",
                        "jarvis": "Opening Chrome right away, Sir."
                    },
                    {
                        "user": "What's the weather today",
                        "jarvis": "Checking current conditions for you, Sir."
                    }
                ],
                "tenglish_arion": [
                    {
                        "user": "Bro em chestunnav",
                        "arion": "Emi ledu bro, nee kosam unna! Cheppu em kavali?"
                    },
                    {
                        "user": "Chala tired ga feel avutunna",
                        "arion": "Ardam avutundi bro, rest teesko. Em jarigindi, cheppu?"
                    },
                    {
                        "user": "Yaar bohot kaam hai aaj",
                        "arion": "Arre yaar, relax! Ek ek kaam karo, ho jayega!"
                    }
                ]
            },
            "config/persona_adaptive.json": {
                "current_mood": "neutral",
                "energy_level": 1.0,
                "last_interaction": None,
                "dominant_emotion_today": "neutral",
                "personality_lean": "balanced",
                "last_updated": datetime.now().isoformat()
            }
        }

        for path, data in configs.items():
            config_path = self.root / path
            # Don't overwrite existing configs
            if not config_path.exists():
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                self.created.append(path)
            else:
                self.skipped.append(path)

    def create_env(self):
        """Create .env if not exists"""
        env_path = self.root / ".env"
        if env_path.exists():
            self.skipped.append(".env")
            return

        env_content = """# ===========================================
# NEXUS-X ULTIMATE - Environment Config
# ===========================================

# -- AI Engine ----------------------------
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1
OLLAMA_FAST_MODEL=gemma2:2b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# -- Optional Cloud AI (leave blank if not using) --
GEMINI_API_KEY=

# -- System Ports -------------------------
NEXUS_PORT=5006
API_PORT=8000
WS_PORT=8765

# -- Features Toggle ----------------------
VOICE_ENABLED=true
VISION_ENABLED=true
SCREEN_WATCH=true
SCREEN_INTERVAL=15
WHATSAPP_ENABLED=false
BIOMETRIC_ENABLED=false
DEBUG=false

# -- Voice --------------------------------
WHISPER_MODEL=base
TTS_VOICE=en-US-AriaNeural
TTS_RATE=+0%

# -- Vision / Biometric -------------------
TESSERACT_PATH=C:\\Program Files\\Tesseract-OCR\\tesseract.exe
CAMERA_INDEX=0
BIOMETRIC_RECHECK=300

# -- Telegram -----------------------------
TELEGRAM_TOKEN=
TELEGRAM_OWNER_CHAT_ID=

# -- WhatsApp -----------------------------
ADMIN_NUMBER=
WHATSAPP_SESSION=nexus_session

# -- Memory -------------------------------
MAX_WORKING_MEMORY=10
MAX_CONTEXT_TURNS=20
VAULT_PATH=knowledge_vault
"""
        env_path.write_text(env_content)
        self.created.append(".env")

    def create_requirements(self):
        """Create requirements.txt"""
        req_path = self.root / "requirements.txt"
        content = """# NEXUS-X ULTIMATE Requirements
# Install: pip install -r requirements.txt

# -- Core AI ------------------------------
aiohttp>=3.9.0
ollama>=0.1.7
langchain>=0.1.0
langchain-community>=0.0.20

# -- Vector Memory -------------------------
chromadb>=0.4.22
sentence-transformers>=2.3.1
faiss-cpu>=1.7.4

# -- Database ------------------------------
aiosqlite>=0.19.0
SQLAlchemy>=2.0.0

# -- API & Web ----------------------------
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
websockets>=12.0
python-multipart>=0.0.9

# -- Voice ---------------------------------
faster-whisper>=0.10.0
edge-tts>=6.1.9
pyttsx3>=2.90
sounddevice>=0.4.6
soundfile>=0.12.1
numpy>=1.24.0

# -- Vision --------------------------------
opencv-python>=4.9.0
Pillow>=10.2.0
pytesseract>=0.3.10
mediapipe>=0.10.9

# -- NLP & Language ------------------------
langdetect>=1.0.9
deep-translator>=1.11.4

# -- Telegram -----------------------------
python-telegram-bot>=20.7

# -- Search --------------------------------
duckduckgo-search>=5.3.0

# -- System & Utils -----------------------
psutil>=5.9.8
python-dotenv>=1.0.1
schedule>=1.2.1
watchdog>=3.0.0
rich>=13.7.0
pydantic>=2.5.3
python-dateutil>=2.8.2
pytz>=2024.1
aiofiles>=23.2.1

# -- Security (Biometric - Optional) ------
# deepface>=0.0.89
# tensorflow>=2.13.0
"""
        req_path.write_text(content)
        self.created.append("requirements.txt")

    def create_launchers(self):
        """Create launcher scripts"""
        bat = self.root / "START_NEXUS.bat"
        if not bat.exists():
            bat.write_text("""@echo off
title NEXUS-X ULTIMATE
color 0B
echo.
echo  Checking Ollama...
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo  Starting Ollama...
    start /B ollama serve
    timeout /t 5 /nobreak >nul
)
echo  Launching NEXUS-X ULTIMATE...
if exist ".venv\\Scripts\\activate.bat" (
    call .venv\\Scripts\\activate.bat
)
python watchdog.py
pause
""")

        sh = self.root / "start_nexus.sh"
        if not sh.exists():
            sh.write_text("""#!/bin/bash
echo "Checking Ollama..."
if ! curl -s http://localhost:11434/api/tags &>/dev/null; then
    echo "Starting Ollama..."
    ollama serve &
    sleep 5
fi
echo "Launching NEXUS-X ULTIMATE..."
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi
python watchdog.py
""")
            os.chmod(sh, 0o755)

    def print_summary(self):
        print("\n" + "="*50)
        print("             NEXUS-X ULTIMATE SETUP DONE")
        print("="*50)
        print(f"  Created: {len(self.created):3d} items")
        print(f"  Skipped: {len(self.skipped):3d} items (already existed)")
        print(f"  Errors:  {len(self.errors):3d}")
        print("="*50)
        print("  NEXT STEPS:")
        print("  1. pip install -r requirements.txt")
        print("  2. ollama pull llama3.1")
        print("  3. ollama pull gemma2:2b")
        print("  4. Edit .env (add Telegram token if needed)")
        print("  5. python watchdog.py")
        print("="*50)

        if self.errors:
            print("Errors:")
            for e in self.errors:
                print(f"  [FAIL] {e}")


if __name__ == "__main__":
    NexusSetup().run()
