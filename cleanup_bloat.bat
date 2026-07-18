@echo off
title 🧹 ZERO CLEANUP — Safe Bloat Remover
color 0E
cls

echo.
echo  ████████████████████████████████████████████████████
echo  █          🧹  ZERO PROTOCOL CLEANUP              █
echo  █      Safely removes build cache ^& old logs      █
echo  ████████████████████████████████████████████████████
echo.
echo  This script ONLY deletes:
echo   - Flutter build cache (nexus_bridge_app\build\)
echo   - Python __pycache__ folders
echo   - Log files older than 7 days (logs\*.log)
echo   - Temp files (tmp\* and temp\*)
echo.
echo  It does NOT delete your code or memory/knowledge files.
echo.
set /p CONFIRM=  Type YES to continue: 

if /i NOT "%CONFIRM%"=="YES" (
    echo  [!] Cancelled. No files were deleted.
    pause
    exit /b
)

echo.
echo  [1/4] Cleaning Flutter build cache...
cd /d "C:\Users\anger\Desktop\nexus_bridge_app"
if exist "build" (
    call flutter clean
    echo  [+] Flutter build cache removed.
) else (
    echo  [+] No build folder found, already clean.
)

echo.
echo  [2/4] Removing Python __pycache__ folders...
cd /d "C:\Users\anger\Desktop\JARVIS_Project"
for /r . %%d in (__pycache__) do (
    if exist "%%d" (
        rd /s /q "%%d" 2>nul
    )
)
echo  [+] __pycache__ folders removed.

echo.
echo  [3/4] Deleting log files older than 7 days...
if exist "logs" (
    forfiles /p "logs" /m "*.log" /d -7 /c "cmd /c del @path" 2>nul
    echo  [+] Old logs cleaned.
) else (
    echo  [+] No logs folder found.
)

echo.
echo  [4/4] Clearing temp files...
if exist "tmp" (
    del /q /s "tmp\*" 2>nul
    echo  [+] tmp\ cleared.
)
if exist "temp" (
    del /q /s "temp\*" 2>nul
    echo  [+] temp\ cleared.
)

echo.
echo  ════════════════════════════════════════════════════
echo   ✅  Cleanup complete! Your system is leaner.
echo   TIP: Run this monthly to keep your laptop fast.
echo  ════════════════════════════════════════════════════
echo.
pause
