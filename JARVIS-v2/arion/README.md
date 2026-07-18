# ARION - Local AI Digital Twin

ARION is a 100% offline, local AI Digital Twin built using a centralized pub/sub message bus architecture via Python `asyncio`. It uses Ollama for local LLM inference, 4-tier memory persistence, and various API-free local integrations.

## Features
- **Local Persistence**: SQLite, ChromaDB, Obsidian Markdown Vault.
- **Micro-Agent Architecture**: 17 independent agents running asynchronously.
- **Multilingual**: Detects and uses English, Telugu, and Hindi.
- **Integrations**: Local Telegram Bot polling and WhatsApp bridge via Node.js.

## Setup
Run the setup script to install dependencies.
```powershell
.\setup.ps1
```

## Running
After installing Ollama and downloading `llama3:8b`:
```bash
python main.py
```
To connect WhatsApp, in a separate terminal:
```bash
cd whatsapp
npm start
```
