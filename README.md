# 🌌 NEXUS-X ULTIMATE: The Autonomous Cognitive OS
**Distributed Fleet • Tiered Memory Architecture • Zero-Latency Intelligence • Automated Social Presence**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![NEXUS-X](https://img.shields.io/badge/Architecture-Nexus--X-orange.svg)](https://github.com/Vihaan0717/Jarvis_project)
[![Memory](https://img.shields.io/badge/Memory-Glymphatic--GC-green.svg)](https://github.com/Vihaan0717/Jarvis_project)
[![Fleet](https://img.shields.io/badge/Fleet-Autonomous-red.svg)](https://github.com/Vihaan0717/Jarvis_project)

NEXUS-X (formerly JARVIS Project) is a privacy-first, self-hosted AI ecosystem that functions as a personal operating system. It moves beyond simple chat interfaces to a **Biologically-Inspired Cognitive Architecture** that manages long-term memory, performs autonomous research, seamlessly bypasses social media security checkpoints, and orchestrates a fleet of specialized agents.

---

## 🚀 Core Features & Capabilities

### 🧠 Cognitive Architecture: The Nexus Brain
The system operates on the **A1-A16 Intelligence Pipeline**, ensuring every input is understood, validated, and executed with precision.

| Stage | Module | Function |
| :--- | :--- | :--- |
| **A1** | **Normalization** | Language detection (English/Telugu/Tenglish) and input cleaning. |
| **A2** | **Memory Recall** | Multi-tier retrieval from Redis, Qdrant (Hippocampus/Cortex), and Supabase. |
| **A2.5** | **Predictive Gate** | Validates requests against world models to prevent hallucinations. |
| **A3** | **Comprehension** | Semantic analysis and intent extraction using fast local LLMs (e.g., Llama 3.2). |
| **A4** | **Classification** | Categorizes tasks via the **Hybrid Model Router** (Execution, Research, Synthesis, Chat). |
| **A5** | **Planning** | Generates step-by-step execution strategies for the agent fleet. |
| **A6** | **Orchestration** | Delegates sub-tasks to specialized agents (Hank, Atlas, Cleo, etc.). |
| **A7** | **QA & Safety** | Filters AI-isms and ensures the output meets the "Boss's" standards. |
| **A8** | **Stylization** | Applies the active persona (Arion/Jarvis) and social/emotional filters. |
| **A13** | **Passive Awareness** | Logs background linguistic candidates with location/emotion metadata. |
| **A16** | **Psyche Analysis** | Tracks cognitive load, emotional state, and psychological archetype shifts. |

### 🧬 Memory Management: The Glymphatic System
Inspired by the human brain's waste clearance and consolidation process, NEXUS-X features a sophisticated tiered memory management system.
1. **Tier 1: Volatile Buffer (Redis)**: Immediate context and short-term "working memory."
2. **Tier 2: Hippocampus (Qdrant Hot)**: Active knowledge and recent interactions.
3. **Tier 3: Cortex (Qdrant Cold)**: Long-term consolidated knowledge and verified facts.

* **Glymphatic Garbage Collector (`glymphatic.py`)**: Runs nightly at 3:00 AM to move high-value memories, decay weak memories, deduplicate vectors, and clean orphans.
* **The Sleep Cycle (`sleep_cycle.py`)**: Analyzes the day's logs and distills **3 Core Lessons** for each agent to update their internal system prompts dynamically.

### 🤖 The Autonomous Fleet
Specialized agents collaborate in a **Peer-Review Loop** to solve complex problems:
* **Atlas**: Deep web research and data synthesis via SearXNG & WebBrain.
* **Hank**: Code generation, logic structuring, and python execution.
* **Cleo**: Content strategy, marketing copy, and social media storytelling.
* **Sentinel**: Network auditing (Nmap/Netstat) and security sweeping.
* **Psyche**: Psychological monitoring, CBT principles, and emotional regulation.
* **Arion/Jarvis**: The social layer providing dual-persona emotional support and natural interaction.

---

## ⚡ New & Advanced Infrastructure

### 🌐 Hybrid Intelligence Router (Zero-Latency)
NEXUS-X uses a custom **Hybrid Model Router** to guarantee uptime.
- **Cloud Primary (Gemini/Groq)**: Used for instantaneous, high-level reasoning and complex logic.
- **Local Fallback (Ollama)**: Automatically takes over if the internet drops or cloud APIs fail.
- **Ollama Heavy Task Queue (2-Minute Cooldown)**: A built-in asynchronous locking mechanism throttles heavy background tasks (like memory consolidation or autonomous web scraping) with a 2-minute delay to prevent local AMD GPU timeouts, ensuring zero crashes.

### 🛡️ Telegram Security Guardian
Your Telegram app acts as the Master Key.
- **Biometric / Manual Handshake**: Before executing sensitive operations (like accessing bank files or changing OS configurations), JARVIS pauses and sends a "Yes/No" approval prompt to your secure Telegram chat.
- **Live Diagnostics**: Receive instant alerts for network drops, unauthorized login attempts, and system health checks directly to Telegram.

### 📸 Seamless Instagram Automation
The `InstagramMonitor` controls your social media presence without ever triggering bot alarms.
- **IMAP Challenge Bypassing**: When Instagram detects automated activity and throws a security checkpoint, JARVIS doesn't crash. He pauses, securely logs into your synced Gmail account via IMAP SSL, uses Regex to extract the 6-digit verification code, and automatically submits it to Instagram—**zero human verification required**.
- **Trend Analysis**: Silently polls Reels, Feeds, and Direct Messages to synthesize social insights and trend data.

### 👁️ Multimodal Vision & Tenglish Logic
- **VisionRouter**: Uses `moondream` or `gemini` to analyze images sent from WhatsApp or Telegram, detecting context, objects, and text natively.
- **Telugu / Tenglish Processing**: Full pipeline dedicated to mapping localized Hyderabadi/Deccani slang to emotional logic. JARVIS understands "Nuvvu ela unnav?" and replies contextually in Telugu script without generic "dictionary" robotic text.

---

## 🛠 Technical Architecture Flow

1. **Input Layer**: You send a message via WhatsApp, Telegram, or Voice.
2. **Gateway**: `main.py` catches the input. `PrivacyGuard` checks authorization.
3. **Brain Routing**: The Master Brain calls `brain.py`, utilizing `qwen`/`llama3.2` to output a strict JSON intent (e.g., routing to `SENTINEL` for a network check or `CLEO` for a social media post).
4. **Execution**: The mapped agent takes over, queries Vector Memory for context, runs its tools, and generates a response.
5. **Output**: Delivered back to your app seamlessly.
6. **Background Metabolism**: Any data processed is ingested into the Knowledge Graph for future recall.

---

## 📥 Installation & Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Vihaan0717/Jarvis_project.git
   cd JARVIS_Project
   ```
2. **Environment Configuration**:
   Rename `.env.example` to `.env`.
   Crucially, provide your API keys, and **ensure you use a 16-character Google App Password** for the `IG_EMAIL_PASSWORD` to enable automatic Instagram verifications.
3. **Start Local Services**:
   Ensure MongoDB, Redis, and Ollama (with `llama3.2:1b` and `nomic-embed-text`) are running.
4. **Launch the Master System**:
   ```bash
   LAUNCH_SYSTEM.bat
   ```

---
© 2026 NEXUS-X / Project Zero. All Rights Reserved.
