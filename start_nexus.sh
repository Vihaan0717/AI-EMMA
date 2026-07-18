#!/bin/bash
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
