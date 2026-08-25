@echo off
title StudIQ Desktop Agent Installer v1.1
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install_agent.ps1"
if errorlevel 1 (
    echo.
    echo [ERROR] Installation failed.
    pause
    exit /b 1
)
pause


