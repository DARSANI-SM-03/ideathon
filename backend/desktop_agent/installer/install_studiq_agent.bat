@echo off
title StudIQ Desktop Agent Setup v1.3
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install_agent.ps1"
if errorlevel 1 (
    echo.
    echo [ERROR] Installation failed.
    pause
    exit /b 1
)
pause


