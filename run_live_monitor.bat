@echo off
set "SCRIPT_DIR=%~dp0"
title STUDIQ LIVE TELEMETRY MONITOR LAUNCHER
echo ============================================================
echo   LAUNCHING STUDIQ REAL-TIME LIVE MONITOR IN DEDICATED WINDOW
echo ============================================================
start "STUDIQ LIVE TELEMETRY MONITOR" cmd /k "cd /d "%SCRIPT_DIR%" && python "%SCRIPT_DIR%backend\desktop_agent\run_live_monitor.py""
