@echo off
color 0A
title NEXUS-X: WAKE UP SEQUENCE

echo ===================================================
echo             NEXUS-X SYSTEM INITIALIZATION
echo ===================================================
echo.

echo [1/4] Checking System Dependencies...
powershell -Command "Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('Checking System Dependencies.')"
pip install mcp pyautogui pillow python-dotenv requests numpy sounddevice soundfile edge-tts kokoro-onnx PyPDF2 playwright nest_asyncio langchain-ollama crawl4ai langgraph browser-use -q

echo [2/4] Booting Local Ollama Engine...
powershell -Command "Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('Booting Local Ollama Engine.')"
start /b "" ollama serve >nul 2>&1
timeout /t 3 >nul

echo [3/4] Spinning up MCP Swarm Servers...
powershell -Command "Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('Spinning up Swarm Servers.')"
:: Start the OS Controller (Port 8005)
start "OS Controller MCP" /min cmd /c "python agents\os_controller_mcp.py"

:: Start the Vision MCP (Port 8006)
start "Vision MCP" /min cmd /c "python agents\vision_mcp.py"

:: Start the Hank MCP (Port 8002)
start "Hank Cybersecurity MCP" /min cmd /c "python agents\hank_mcp.py"

:: Start the Atlas MCP (Port 8003)
start "Atlas Research MCP" /min cmd /c "python agents\atlas_mcp.py"

:: Start the Psyche MCP (Port 8004)
start "Psyche Memory MCP" /min cmd /c "python agents\psyche_mcp.py"

:: Wait for servers to stabilize
timeout /t 3 >nul

echo [4/4] Initializing NEXUS Master Brain...
powershell -Command "Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('Initializing NEXUS Master Brain.')"
echo.
echo ===================================================
echo             ALL SYSTEMS ONLINE. 
echo ===================================================
echo.

:: Launch the main interactive loop
python nexus_master.py

pause
