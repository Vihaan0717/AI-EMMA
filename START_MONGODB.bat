@echo off
title NEXUS-X : MONGODB SERVER
color 0A
echo Starting MongoDB for Arion Bridge...
echo Log file will be created at logs\mongodb.log
"mongodb\mongodb-win32-x86_64-windows-7.0.8\bin\mongod.exe" --dbpath "data\mongodb" --port 27017 --logpath "logs\mongodb.log" --logappend
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] MongoDB failed to start with error code %ERRORLEVEL%
    pause
)
pause
