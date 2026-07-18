@echo off
color 0B
cls
echo.
echo  ================================================
echo        ARION SENTIENT MIRROR V3 (FREE STACK)
echo  ================================================
echo.

echo  [Step 1] Checking Ollama Status...
curl -s http://localhost:11434/api/tags >nul
if %ERRORLEVEL% NEQ 0 (
    echo  [ERROR] Ollama is not running!
    echo  Please start Ollama Desktop or run 'ollama serve'
    echo  Download from: https://ollama.ai
    pause
    exit
)
echo  [OK] Ollama is Alive

echo  [Step 2] Cleaning old processes...
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM node.exe /T >nul 2>&1
timeout /t 2 >nul
echo  [OK] Cleaned

echo  [Step 3] Checking vault path...
python -c "import os, sys; from pathlib import Path; from dotenv import load_dotenv; load_dotenv(); vault = os.getenv('VAULT_PATH', ''); (print('[ERROR] VAULT_PATH not set in .env') or sys.exit(1)) if not vault else None; p = Path(vault); (p.mkdir(parents=True, exist_ok=True) or print(f'Created vault: {vault}')) if not p.exists() else print(f'[OK] Vault found: {len(list(p.rglob(\"*.md\")))} .md files')"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Vault check failed.
    pause
    exit
)
echo.

echo  [Step 4] Launching ARION Core (Full Multi-Agent)...
start "ARION_CORE" cmd /k "cd /d %~dp0\arion && python main.py"
timeout /t 10 >nul

echo  [Step 5] Launching WhatsApp Bridge...
if exist arion\whatsapp (
    cd arion\whatsapp
    start "ARION_WA" cmd /k "npm start"
    cd /d %~dp0
) else (
    echo [WARNING] WhatsApp folder not found. Skipping.
)

echo.
echo  ================================================
echo     ARION FREE STACK IS RUNNING!
echo  ================================================
echo.
echo   Brain Engine : Ollama (Local)
echo   Vision Eye   : Active
echo   WhatsApp     : Initializing
echo  ================================================
echo.
pause
