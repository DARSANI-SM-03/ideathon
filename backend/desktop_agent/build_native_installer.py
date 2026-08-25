"""
StudIQ Native Windows Setup Package Builder (v1.3)
===================================================
1. Packages dist/StudIQAgent into StudIQAgent.zip (compressed payload).
2. Base64-encodes StudIQAgent.zip.
3. Generates standalone native Windows setup script StudIQAgentSetup.bat (v1.3).
   - Requires 0 MB of PyInstaller C bootloader DLL temporary extraction on C:
   - Dynamically resolves Windows per-user LOCALAPPDATA directory (%LOCALAPPDATA%\StudIQ\Agent).
   - Unblocks Mark-of-the-Web (MotW) download flags automatically.
   - Dual-logs to %TEMP%\StudIQAgentSetup.log & %LOCALAPPDATA%\StudIQ\Agent\install.log.
   - Captures errors and forces CMD pause so windows never close silently on failure.
   - Registers HKCU URI scheme & Windows startup.
   - Launches background daemon.
"""

import sys
import os
import zipfile
import base64

def create_payload_zip(source_dir: str, output_zip_path: str):
    print(f"[Build Native Setup] Zipping payload directory '{source_dir}' -> '{output_zip_path}'...")
    with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, source_dir)
                zipf.write(abs_path, rel_path)
    zip_size = os.path.getsize(output_zip_path)
    print(f"[Build Native Setup] Payload ZIP created ({zip_size} bytes / {zip_size / (1024*1024):.2f} MB).")

PS_SETUP_SCRIPT_TEMPLATE = r'''# StudIQ Desktop Agent Setup PowerShell Core Engine v1.3
$ErrorActionPreference = 'Stop'

Add-Type -AssemblyName System.Windows.Forms -ErrorAction SilentlyContinue

$Global:LogFile = Join-Path $env:TEMP 'StudIQAgentSetup.log'

function Write-Log([string]$msg, [string]$color = 'White') {
    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $logLine = "[$timestamp] $msg"
    Write-Host $msg -ForegroundColor $color
    try {
        Add-Content -Path $Global:LogFile -Value $logLine -ErrorAction SilentlyContinue
    } catch {}
}

function Show-MsgBox([string]$msg, [string]$title, [int]$icon = 64) {
    try {
        [System.Windows.Forms.MessageBox]::Show($msg, $title, [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]$icon) | Out-Null
    } catch {
        Write-Log "[$title] $msg" 'Yellow'
    }
}

try {
    Write-Log '==========================================================' 'Cyan'
    Write-Log '   StudIQ Desktop Agent Setup v1.3' 'Cyan'
    Write-Log '==========================================================' 'Cyan'
    Write-Log '[Setup] Resolving Windows per-user installation path...' 'Yellow'

    $localAppData = $env:LOCALAPPDATA
    if (-not $localAppData) {
        $localAppData = [System.Environment]::GetFolderPath('LocalApplicationData')
    }
    if (-not $localAppData) {
        $localAppData = Join-Path $env:USERPROFILE 'AppData\Local'
    }

    $reqBytes = 150 * 1024 * 1024
    $drives = [System.IO.DriveInfo]::GetDrives() | Where-Object { $_.DriveType -eq 'Fixed' -and $_.IsReady }

    $appDataDrive = 'C:\'
    if ($localAppData -and $localAppData.Length -ge 3 -and $localAppData[1] -eq ':') {
        $appDataDrive = $localAppData.Substring(0, 3).ToUpper()
    }

    $installDir = $null
    $targetDrive = $null

    $appDataDriveInfo = $drives | Where-Object { $_.Name.ToUpper().StartsWith($appDataDrive) -and $_.AvailableFreeSpace -ge $reqBytes }
    if ($appDataDriveInfo) {
        $installDir = Join-Path $localAppData 'StudIQ\Agent'
        $targetDrive = $appDataDriveInfo.Name
    } else {
        $altDrive = $drives | Where-Object { $_.AvailableFreeSpace -ge $reqBytes }
        if ($altDrive) {
            $targetDrive = $altDrive[0].Name
            $installDir = Join-Path $targetDrive 'StudIQ\Agent'
        }
    }

    if (-not $installDir) {
        Write-Log '[ERROR] Insufficient disk space on all local drives.' 'Red'
        Show-MsgBox 'StudIQ Desktop Agent setup failed: Insufficient free disk space on all local drives.' 'StudIQ Setup Error' 16
        exit 1
    }

    Write-Log "[Setup] Selected target directory: $installDir (Drive $targetDrive)" 'Green'

    if (-not (Test-Path $installDir)) {
        New-Item -ItemType Directory -Path $installDir -Force | Out-Null
    }

    # Set up dual logging to target directory as well
    $localInstallLog = Join-Path $installDir 'install.log'

    Write-Log '[Setup] Checking for active StudIQAgent processes...' 'Yellow'
    try {
        $req = [System.Net.WebRequest]::Create('http://127.0.0.1:8765/stop')
        $req.Method = 'POST'
        $req.Timeout = 2000
        $resp = $req.GetResponse()
        $resp.Close()
    } catch {}

    Start-Sleep -Milliseconds 500
    Stop-Process -Name 'StudIQAgent' -Force -ErrorAction SilentlyContinue

    $exePath = Join-Path $installDir 'StudIQAgent.exe'
    if (Test-Path $exePath) {
        for ($i = 0; $i -lt 10; $i++) {
            try {
                $fs = [System.IO.File]::Open($exePath, [System.IO.FileMode]::Open, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
                $fs.Close()
                break
            } catch {
                Start-Sleep -Milliseconds 500
            }
        }
    }

    Write-Log '[Setup] Extracting binary payload directly to installation directory...' 'Green'
    $setupScriptPath = $args[0]
    if (-not $setupScriptPath -or -not (Test-Path $setupScriptPath)) {
        $setupScriptPath = Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Definition) 'StudIQAgentSetup.bat'
    }

    if (-not (Test-Path $setupScriptPath)) {
        throw "Setup payload file missing at '$setupScriptPath'."
    }

    $lines = Get-Content -Path $setupScriptPath
    $startIndex = -1
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -match '^-----BEGIN PAYLOAD-----') {
            $startIndex = $i + 1
            break
        }
    }

    if ($startIndex -eq -1) {
        throw 'Payload marker missing in setup script.'
    }

    $zipFile = Join-Path $installDir 'payload.zip'
    $b64Content = $lines[$startIndex..($lines.Count - 1)] -join ''
    $bytes = [System.Convert]::FromBase64String($b64Content)
    [System.IO.File]::WriteAllBytes($zipFile, $bytes)

    Expand-Archive -Path $zipFile -DestinationPath $installDir -Force
    Remove-Item -Path $zipFile -Force -ErrorAction SilentlyContinue

    if (-not (Test-Path $exePath)) {
        throw "StudIQAgent.exe missing at $exePath after extraction."
    }

    Write-Log '[Setup] Configuring Windows Registry protocol and startup keys...' 'Green'
    $protKey = 'HKCU:\Software\Classes\studiq-agent'
    New-Item -Path $protKey -Force | Out-Null
    Set-ItemProperty -Path $protKey -Name '(default)' -Value 'URL:StudIQ Agent Protocol' -Force
    Set-ItemProperty -Path $protKey -Name 'URL Protocol' -Value '' -Force

    $cmdKey = Join-Path $protKey 'shell\open\command'
    New-Item -Path $cmdKey -Force | Out-Null
    Set-ItemProperty -Path $cmdKey -Name '(default)' -Value "`"$exePath`" `"%1`"" -Force

    $runKey = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run'
    Set-ItemProperty -Path $runKey -Name 'StudIQAgent' -Value "`"$exePath`" `"studiq-agent://start`"" -Force

    $WshShell = New-Object -ComObject WScript.Shell
    $sm = [System.Environment]::GetFolderPath('Programs')
    if ($sm -and (Test-Path $sm)) {
        $s1 = $WshShell.CreateShortcut((Join-Path $sm 'StudIQ Desktop Agent.lnk'))
        $s1.TargetPath = $exePath
        $s1.Arguments = 'studiq-agent://start'
        $s1.WorkingDirectory = $installDir
        $s1.Save()
    }

    $dt = [System.Environment]::GetFolderPath('Desktop')
    if ($dt -and (Test-Path $dt)) {
        $s2 = $WshShell.CreateShortcut((Join-Path $dt 'StudIQ Desktop Agent.lnk'))
        $s2.TargetPath = $exePath
        $s2.Arguments = 'studiq-agent://start'
        $s2.WorkingDirectory = $installDir
        $s2.Save()
    }

    $unBat = Join-Path $installDir 'uninstall_studiq_agent.bat'
    $unCode = @"
@echo off
title StudIQ Agent Uninstaller
echo Removing StudIQ Agent protocol, shortcuts, and files...
powershell -ExecutionPolicy Bypass -Command "Remove-Item -Path 'HKCU:\Software\Classes\studiq-agent' -Recurse -Force -ErrorAction SilentlyContinue"
powershell -ExecutionPolicy Bypass -Command "`$sm = [System.Environment]::GetFolderPath('Programs'); `$lnk1 = Join-Path `$sm 'StudIQ Desktop Agent.lnk'; if (Test-Path `$lnk1) { Remove-Item `$lnk1 -Force }; `$dt = [System.Environment]::GetFolderPath('Desktop'); `$lnk2 = Join-Path `$dt 'StudIQ Desktop Agent.lnk'; if (Test-Path `$lnk2) { Remove-Item `$lnk2 -Force }"
powershell -ExecutionPolicy Bypass -Command "Remove-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' -Name 'StudIQAgent' -ErrorAction SilentlyContinue"
taskkill /F /IM StudIQAgent.exe 2>nul
rmdir /S /Q "$installDir"
echo StudIQ Desktop Agent uninstalled.
pause
"@
    Set-Content -Path $unBat -Value $unCode -Force

    Write-Log '[Setup] Launching background StudIQ Agent daemon...' 'Green'
    Start-Process -FilePath $exePath -ArgumentList 'studiq-agent://start' -WindowStyle Hidden

    Write-Log '==========================================================' 'Green'
    Write-Log ' SUCCESS: StudIQ Desktop Agent Installed Successfully!' 'Green'
    Write-Log " Installation Directory : $installDir" 'Green'
    Write-Log ' Protocol Handler Registered : studiq-agent://' 'Green'
    Write-Log ' Windows Startup Configured  : HKCU Run Key' 'Green'
    Write-Log '==========================================================' 'Green'

    try {
        Copy-Item -Path $Global:LogFile -Destination $localInstallLog -Force -ErrorAction SilentlyContinue
    } catch {}

    Show-MsgBox "StudIQ Desktop Agent was installed successfully!`n`nLocation: $installDir`n`nBackground monitoring is active." "StudIQ Setup Complete" 64
} catch {
    $err = $_.Exception.Message
    Write-Log "[Setup Error] $err" 'Red'
    Show-MsgBox "StudIQ Desktop Agent setup failed:`n$err`n`nDetailed log file: $Global:LogFile" "StudIQ Setup Error" 16
    exit 1
}
'''

def generate_native_installer_bat(zip_path: str, output_bat_path: str):
    print(f"[Build Native Setup] Encoding base64 payload from '{zip_path}'...")
    with open(zip_path, 'rb') as f:
        b64_payload = base64.b64encode(f.read()).decode('ascii')

    print(f"[Build Native Setup] Base64 payload length: {len(b64_payload)} characters.")

    b64_ps_code = base64.b64encode(PS_SETUP_SCRIPT_TEMPLATE.encode('utf-8')).decode('ascii')

    output_ps1_path = os.path.join(os.path.dirname(output_bat_path), "StudIQAgentSetup.ps1")
    with open(output_ps1_path, 'w', encoding='utf-8') as f:
        f.write(PS_SETUP_SCRIPT_TEMPLATE)
    print(f"[Build Native Setup] Generated standalone StudIQAgentSetup.ps1 ({os.path.getsize(output_ps1_path)} bytes).")

    bat_template = f"""@echo off
title StudIQ Desktop Agent Setup v1.3
setlocal enabledelayedexpansion

echo ==========================================================
echo    StudIQ Desktop Agent Setup v1.3
echo ==========================================================
echo Initializing native Windows installation setup...
echo.

set "BAT_PATH=%~f0"
set "TEMP_PS1=%TEMP%\\studiq_setup_%RANDOM%.ps1"
set "TEMP_LOG=%TEMP%\\StudIQAgentSetup.log"
set "PS_B64={b64_ps_code}"

echo [Installer Launcher v1.3] [%DATE% %TIME%] Launching StudIQ Desktop Agent Setup >> "%TEMP_LOG%"

rem Unblock Mark-of-the-Web download security flag if present
powershell -NoProfile -ExecutionPolicy Bypass -Command "Unblock-File -Path '%BAT_PATH%' -ErrorAction SilentlyContinue" >nul 2>&1

rem Decode embedded PowerShell engine
powershell -NoProfile -ExecutionPolicy Bypass -Command "[System.IO.File]::WriteAllText($env:TEMP_PS1, [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($env:PS_B64)))"
if not exist "%TEMP_PS1%" (
    echo.
    echo ==========================================================
    echo  [ERROR] Failed to extract temporary setup engine.
    echo ==========================================================
    echo.
    echo [ERROR] Failed to extract temporary setup engine script to %TEMP_PS1% >> "%TEMP_LOG%"
    pause
    exit /b 1
)

rem Unblock temporary extracted setup engine script
powershell -NoProfile -ExecutionPolicy Bypass -Command "Unblock-File -Path '%TEMP_PS1%' -ErrorAction SilentlyContinue" >nul 2>&1

rem Execute PowerShell setup engine
powershell -NoProfile -ExecutionPolicy Bypass -File "%TEMP_PS1%" "%BAT_PATH%"
set "EXIT_CODE=%ERRORLEVEL%"

if exist "%TEMP_PS1%" del /f /q "%TEMP_PS1%" >nul 2>&1

if %EXIT_CODE% neq 0 (
    echo.
    echo ==========================================================
    echo  [ERROR] StudIQ Desktop Agent Setup failed with exit code %EXIT_CODE%.
    echo  Detailed log file available at: %TEMP_LOG%
    echo ==========================================================
    echo.
    pause
    exit /b %EXIT_CODE%
)

echo.
echo ==========================================================
echo  StudIQ Desktop Agent Setup v1.3 Finished Successfully.
echo ==========================================================
echo.
pause
exit /b 0

-----BEGIN PAYLOAD-----
"""

    with open(output_bat_path, 'w', encoding='utf-8') as f:
        f.write(bat_template)
        f.write(b64_payload)

    out_size = os.path.getsize(output_bat_path)
    print(f"[Build Native Setup] Generated StudIQAgentSetup.bat ({out_size} bytes / {out_size / (1024*1024):.2f} MB).")

def build():
    agent_dir = os.path.dirname(os.path.abspath(__file__))
    agent_dist_dir = os.path.join(agent_dir, "dist", "StudIQAgent")
    installer_dir = os.path.join(agent_dir, "installer")
    payload_zip = os.path.join(installer_dir, "StudIQAgent.zip")
    output_bat = os.path.join(installer_dir, "StudIQAgentSetup.bat")

    if not os.path.exists(os.path.join(agent_dist_dir, "StudIQAgent.exe")):
        print("[Build Native Setup] Building StudIQAgent executable first...")
        import build_agent_exe
        build_agent_exe.build()

    create_payload_zip(agent_dist_dir, payload_zip)
    generate_native_installer_bat(payload_zip, output_bat)

if __name__ == "__main__":
    build()
