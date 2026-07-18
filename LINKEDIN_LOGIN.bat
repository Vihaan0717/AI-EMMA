@echo off
title LinkedIn Login - JARVIS CELO-APPLY
echo ===================================================
echo    JARVIS: LinkedIn One-Time Login
echo ===================================================
echo.
echo A Chromium browser will open. Log into LinkedIn.
echo Then come back here and press ENTER to save session.
echo.
cd /d "%~dp0"
python linkedin_login.py
pause
