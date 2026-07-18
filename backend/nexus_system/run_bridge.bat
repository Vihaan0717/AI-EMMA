@echo off
echo [NEXUS-X] Starting Zero Bridge on 0.0.0.0:8000...
uvicorn bridge_server:app --host 0.0.0.0 --port 8000
pause
