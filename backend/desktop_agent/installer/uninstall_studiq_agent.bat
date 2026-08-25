@echo off
title StudIQ Agent Uninstaller
echo ==========================================================
echo    StudIQ Windows Desktop Agent Uninstaller
echo ==========================================================
echo Removing StudIQ Agent and registry protocol handler...
echo.

powershell -Command "Remove-Item -Path 'HKCU:\Software\Classes\studiq-agent' -Recurse -Force -ErrorAction SilentlyContinue"
powershell -Command "Remove-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' -Name 'StudIQAgent' -ErrorAction SilentlyContinue"

if exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\StudIQ Desktop Agent.lnk" (
    del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\StudIQ Desktop Agent.lnk"
)
if exist "%USERPROFILE%\Desktop\StudIQ Desktop Agent.lnk" (
    del "%USERPROFILE%\Desktop\StudIQ Desktop Agent.lnk"
)

echo Terminating active StudIQ agent processes...
taskkill /F /IM StudIQAgent.exe 2>nul

echo Removing installation files...
rmdir /S /Q "%LOCALAPPDATA%\StudIQ\Agent"

echo.
echo ==========================================================
echo   SUCCESS: StudIQ Desktop Agent Uninstalled Cleanly.
echo ==========================================================
pause
