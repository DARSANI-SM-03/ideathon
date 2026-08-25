# StudIQ Desktop Agent Installer Script v1.1
# ============================================

$ErrorActionPreference = "Stop"

$InstallDir = "$env:LOCALAPPDATA\StudIQ\Agent"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$SourceDist = Join-Path (Split-Path -Parent $ScriptDir) "dist\StudIQAgent"
$SourceParent = Split-Path -Parent $ScriptDir

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   StudIQ Windows Desktop Agent Installer v1.1" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "Target Installation Directory: $InstallDir" -ForegroundColor Yellow
Write-Host ""

# 1. Create installation directory & stop running agent instances
if (-not (Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
    Write-Host "[Installer] Created installation directory: $InstallDir" -ForegroundColor Green
}

Write-Host "[Installer] Stopping active StudIQAgent processes if any..." -ForegroundColor Yellow
Stop-Process -Name "StudIQAgent" -Force -ErrorAction SilentlyContinue

# 2. Copy binaries / packaged output
if (Test-Path $SourceDist) {
    Write-Host "[Installer] Copying packaged executable files from dist\StudIQAgent..." -ForegroundColor Green
    Copy-Item -Path "$SourceDist\*" -Destination $InstallDir -Recurse -Force
}

# 3. Copy python scripts as fallback/modules
$pyFiles = @("agent.py", "bridge.py", "protocol_handler.py", "collector.py", "classifier.py", "sender.py", "config.py")
foreach ($file in $pyFiles) {
    $srcPath = Join-Path $SourceParent $file
    if (Test-Path $srcPath) {
        Copy-Item -Path $srcPath -Destination $InstallDir -Force
    }
}

# 4. Verify StudIQAgent.exe exists
$ExePath = Join-Path $InstallDir "StudIQAgent.exe"
if (-not (Test-Path $ExePath)) {
    Write-Host "[ERROR] StudIQAgent.exe was not found in $InstallDir!" -ForegroundColor Red
    Write-Host "Please build the executable using 'python backend/desktop_agent/build_agent_exe.py' first." -ForegroundColor Red
    exit 1
}
Write-Host "[Installer] Verified StudIQAgent.exe exists at: $ExePath" -ForegroundColor Green

# 5. Register studiq-agent:// Protocol in Registry (HKCU)
Write-Host "[Installer] Registering custom URI protocol: studiq-agent://" -ForegroundColor Green

$ProtocolKey = "HKCU:\Software\Classes\studiq-agent"
New-Item -Path $ProtocolKey -Force | Out-Null
Set-ItemProperty -Path $ProtocolKey -Name "(default)" -Value "URL:StudIQ Agent Protocol" -Force
Set-ItemProperty -Path $ProtocolKey -Name "URL Protocol" -Value "" -Force

$CmdKey = "$ProtocolKey\shell\open\command"
New-Item -Path $CmdKey -Force | Out-Null
$CommandValue = '"' + $ExePath + '" "%1"'
Set-ItemProperty -Path $CmdKey -Name "(default)" -Value $CommandValue -Force

# 6. Create Start Menu & Desktop Shortcuts using Environment Folder Paths
$WshShell = New-Object -ComObject WScript.Shell

$StartMenuDir = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::Programs)
if ($StartMenuDir -and (Test-Path $StartMenuDir)) {
    $StartMenuShortcut = Join-Path $StartMenuDir "StudIQ Desktop Agent.lnk"
    $s1 = $WshShell.CreateShortcut($StartMenuShortcut)
    $s1.TargetPath = $ExePath
    $s1.Arguments = "studiq-agent://start"
    $s1.Description = "StudIQ Desktop Agent Launcher"
    $s1.WorkingDirectory = $InstallDir
    $s1.Save()
    Write-Host "[Installer] Created Start Menu shortcut: $StartMenuShortcut" -ForegroundColor Green
}

$DesktopDir = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::Desktop)
if ($DesktopDir -and (Test-Path $DesktopDir)) {
    $DesktopShortcut = Join-Path $DesktopDir "StudIQ Desktop Agent.lnk"
    $s2 = $WshShell.CreateShortcut($DesktopShortcut)
    $s2.TargetPath = $ExePath
    $s2.Arguments = "studiq-agent://start"
    $s2.Description = "StudIQ Desktop Agent Launcher"
    $s2.WorkingDirectory = $InstallDir
    $s2.Save()
    Write-Host "[Installer] Created Desktop shortcut: $DesktopShortcut" -ForegroundColor Green
}

# 7. Generate Uninstaller Script
$UninstallBat = Join-Path $InstallDir "uninstall_studiq_agent.bat"
$UninstallContent = @"
@echo off
title StudIQ Agent Uninstaller
echo ==========================================================
echo    StudIQ Windows Desktop Agent Uninstaller
echo ==========================================================
echo Removing StudIQ Agent protocol handler, shortcuts, and files...
echo.

powershell -ExecutionPolicy Bypass -Command "Remove-Item -Path 'HKCU:\Software\Classes\studiq-agent' -Recurse -Force -ErrorAction SilentlyContinue"

powershell -ExecutionPolicy Bypass -Command "`$sm = [System.Environment]::GetFolderPath('Programs'); `$lnk1 = Join-Path `$sm 'StudIQ Desktop Agent.lnk'; if (Test-Path `$lnk1) { Remove-Item `$lnk1 -Force }; `$dt = [System.Environment]::GetFolderPath('Desktop'); `$lnk2 = Join-Path `$dt 'StudIQ Desktop Agent.lnk'; if (Test-Path `$lnk2) { Remove-Item `$lnk2 -Force }"

echo Terminating active StudIQ agent processes...
taskkill /F /IM StudIQAgent.exe 2>nul

echo Removing installation files...
rmdir /S /Q "%LOCALAPPDATA%\StudIQ\Agent"

echo.
echo ==========================================================
echo   SUCCESS: StudIQ Desktop Agent Uninstalled Cleanly.
echo ==========================================================
pause
"@
Set-Content -Path $UninstallBat -Value $UninstallContent -Force
Write-Host "[Installer] Generated uninstaller script: $UninstallBat" -ForegroundColor Green

# 8. Registry Verification Check
Write-Host ""
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   VERIFYING REGISTRY REGISTRATION" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

cmd.exe /c "reg query HKCU\Software\Classes\studiq-agent\shell\open\command"

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host " SUCCESS: StudIQ Desktop Agent Installed Successfully!" -ForegroundColor Green
Write-Host " Protocol Handler Registered : studiq-agent://" -ForegroundColor Green
Write-Host " Installation Path          : $InstallDir" -ForegroundColor Green
Write-Host " Executable Verified        : $ExePath" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host ""
