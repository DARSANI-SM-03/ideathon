@echo off
title StudIQ Desktop Agent Bridge Launcher
echo ==========================================================
echo    StudIQ Windows Desktop Agent Bridge Launcher
echo ==========================================================
echo Starting local bridge daemon on http://127.0.0.1:8765...
echo.
cd /d "%~dp0"
python bridge.py
pause
