"""
StudIQ Native Windows Setup Package Builder
============================================
1. Packages dist/StudIQAgent into StudIQAgent.zip (compressed payload).
2. Base64-encodes StudIQAgent.zip.
3. Generates standalone native Windows setup script StudIQAgentSetup.bat.
   - Requires 0 MB of PyInstaller C bootloader DLL temporary extraction on C:
   - Dynamically selects E:\\ drive as top preference if available, falling back safely to D: or C:
   - Resolves WinError 32 file handle locks cleanly.
   - Registers HKCU URI scheme & Windows startup.
   - Launches daemon and displays setup completion alert.
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

def generate_native_installer_bat(zip_path: str, output_bat_path: str):
    print(f"[Build Native Setup] Encoding base64 payload from '{zip_path}'...")
    with open(zip_path, 'rb') as f:
        b64_payload = base64.b64encode(f.read()).decode('ascii')

    print(f"[Build Native Setup] Base64 payload length: {len(b64_payload)} characters.")

    # Create batch + powershell polyglot setup script
    bat_template = """@echo off
title StudIQ Agent 1-Click Windows Setup
setlocal enabledelayedexpansion

echo ==========================================================
echo    StudIQ Windows Desktop Agent 1-Click Setup v1.2
echo ==========================================================
echo Initializing native Windows installation setup...
echo.

set "SCRIPT_PATH=%~f0"

powershell -NoProfile -ExecutionPolicy Bypass -Command "^
$ErrorActionPreference = 'Stop'; ^
function Show-MsgBox($msg, $title, $icon=64) { ^
    [System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms') | Out-Null; ^
    [System.Windows.Forms]::MessageBox::Show($msg, $title, 0, $icon); ^
}; ^
try { ^
    Write-Host '[Setup] Discovering available local fixed drives...' -ForegroundColor Yellow; ^
    $drives = [System.IO.DriveInfo]::GetDrives() | Where-Object { $_.DriveType -eq 'Fixed' -and $_.IsReady }; ^
    $reqBytes = 150 * 1024 * 1024; ^
    $targetDrive = $null; ^
    $localAppData = $env:LOCALAPPDATA; ^
    $appDataDrive = $null; ^
    if ($localAppData -and $localAppData.Length -ge 3) { $appDataDrive = $localAppData.Substring(0, 3).ToUpper(); }; ^
    $eDrive = $drives | Where-Object { $_.Name.ToUpper().StartsWith('E:') -and $_.AvailableFreeSpace -ge $reqBytes }; ^
    if ($eDrive) { ^
        $targetDrive = 'E:\\'; ^
    } else { ^
        $sysDrive = $env:SystemDrive.ToUpper() + '\\'; ^
        $nonSys = $drives | Where-Object { $_.Name.ToUpper() -ne $sysDrive -and $_.AvailableFreeSpace -ge $reqBytes }; ^
        if ($nonSys) { $targetDrive = $nonSys[0].Name; } ^
        elseif ($appDataDrive -and ($drives | Where-Object { $_.Name.ToUpper().StartsWith($appDataDrive) -and $_.AvailableFreeSpace -ge $reqBytes })) { $targetDrive = $appDataDrive; } ^
        else { ^
            $sys = $drives | Where-Object { $_.AvailableFreeSpace -ge $reqBytes }; ^
            if ($sys) { $targetDrive = $sys[0].Name; }; ^
        }; ^
    }; ^
    if (-not $targetDrive) { ^
        Write-Host '[ERROR] Insufficient disk space on all drives.' -ForegroundColor Red; ^
        Show-MsgBox 'StudIQ Agent setup failed: Insufficient free disk space on all local drives.' 'StudIQ Setup Error' 16; ^
        exit 1; ^
    }; ^
    $installDir = Join-Path $targetDrive 'StudIQ\\Agent'; ^
    Write-Host \"[Setup] Selected target directory: $installDir (Drive $targetDrive)\" -ForegroundColor Green; ^
    if (-not (Test-Path $installDir)) { New-Item -ItemType Directory -Path $installDir -Force | Out-Null; }; ^
    Write-Host '[Setup] Checking for active StudIQAgent processes...' -ForegroundColor Yellow; ^
    try { ^
        $req = [System.Net.WebRequest]::Create('http://127.0.0.1:8765/stop'); ^
        $req.Method = 'POST'; ^
        $req.Timeout = 2000; ^
        $resp = $req.GetResponse(); ^
        $resp.Close(); ^
    } catch {}; ^
    Start-Sleep -Milliseconds 500; ^
    Stop-Process -Name 'StudIQAgent' -Force -ErrorAction SilentlyContinue; ^
    $exePath = Join-Path $installDir 'StudIQAgent.exe'; ^
    if (Test-Path $exePath) { ^
        $unlocked = $false; ^
        for ($i=0; $i -lt 10; $i++) { ^
            try { ^
                $fs = [System.IO.File]::Open($exePath, [System.IO.FileMode]::Open, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None); ^
                $fs.Close(); ^
                $unlocked = $true; ^
                break; ^
            } catch { Start-Sleep -Milliseconds 500; }; ^
        }; ^
    }; ^
    Write-Host '[Setup] Extracting binary payload directly to installation drive...' -ForegroundColor Green; ^
    $b64File = Join-Path $installDir 'payload.b64'; ^
    $zipFile = Join-Path $installDir 'payload.zip'; ^
    $lines = Get-Content -Path '%SCRIPT_PATH%'; ^
    $startIndex = -1; ^
    for ($i=0; $i -lt $lines.Count; $i++) { ^
        if ($lines[$i] -match '^-----BEGIN PAYLOAD-----') { $startIndex = $i + 1; break; }; ^
    }; ^
    if ($startIndex -eq -1) { throw 'Payload marker missing in setup script.'; }; ^
    $b64Content = $lines[$startIndex..($lines.Count - 1)] -join ''; ^
    $bytes = [System.Convert]::FromBase64String($b64Content); ^
    [System.IO.File]::WriteAllBytes($zipFile, $bytes); ^
    Expand-Archive -Path $zipFile -DestinationPath $installDir -Force; ^
    Remove-Item -Path $zipFile -Force -ErrorAction SilentlyContinue; ^
    Write-Host '[Setup] Configuring Windows Registry protocol and startup keys...' -ForegroundColor Green; ^
    $protKey = 'HKCU:\\Software\\Classes\\studiq-agent'; ^
    New-Item -Path $protKey -Force | Out-Null; ^
    Set-ItemProperty -Path $protKey -Name '(default)' -Value 'URL:StudIQ Agent Protocol' -Force; ^
    Set-ItemProperty -Path $protKey -Name 'URL Protocol' -Value '' -Force; ^
    $cmdKey = \"$protKey\\shell\\open\\command\"; ^
    New-Item -Path $cmdKey -Force | Out-Null; ^
    Set-ItemProperty -Path $cmdKey -Name '(default)' -Value ('\"' + $exePath + '\" \"%1\"') -Force; ^
    $runKey = 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run'; ^
    Set-ItemProperty -Path $runKey -Name 'StudIQAgent' -Value ('\"' + $exePath + '\" \"studiq-agent://start\"') -Force; ^
    $WshShell = New-Object -ComObject WScript.Shell; ^
    $sm = [System.Environment]::GetFolderPath('Programs'); ^
    if ($sm) { ^
        $s1 = $WshShell.CreateShortcut((Join-Path $sm 'StudIQ Desktop Agent.lnk')); ^
        $s1.TargetPath = $exePath; ^
        $s1.Arguments = 'studiq-agent://start'; ^
        $s1.WorkingDirectory = $installDir; ^
        $s1.Save(); ^
    }; ^
    $dt = [System.Environment]::GetFolderPath('Desktop'); ^
    if ($dt) { ^
        $s2 = $WshShell.CreateShortcut((Join-Path $dt 'StudIQ Desktop Agent.lnk')); ^
        $s2.TargetPath = $exePath; ^
        $s2.Arguments = 'studiq-agent://start'; ^
        $s2.WorkingDirectory = $installDir; ^
        $s2.Save(); ^
    }; ^
    $unBat = Join-Path $installDir 'uninstall_studiq_agent.bat'; ^
    $unCode = '@echo off' + [Environment]::NewLine + 'powershell -ExecutionPolicy Bypass -Command \"Remove-Item -Path ''HKCU:\\Software\\Classes\\studiq-agent'' -Recurse -Force -ErrorAction SilentlyContinue\"' + [Environment]::NewLine + 'powershell -ExecutionPolicy Bypass -Command \"Remove-ItemProperty -Path ''HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run'' -Name ''StudIQAgent'' -ErrorAction SilentlyContinue\"' + [Environment]::NewLine + 'taskkill /F /IM StudIQAgent.exe 2>nul' + [Environment]::NewLine + 'rmdir /S /Q \"' + $installDir + '\"'; ^
    Set-Content -Path $unBat -Value $unCode -Force; ^
    Write-Host '[Setup] Launching background StudIQ Agent daemon...' -ForegroundColor Green; ^
    Start-Process -FilePath $exePath -ArgumentList 'studiq-agent://start' -WindowStyle Hidden; ^
    Write-Host '=========================================================='; ^
    Write-Host ' SUCCESS: StudIQ Desktop Agent Installed Successfully!' -ForegroundColor Green; ^
    Write-Host \" Installation Directory : $installDir\" -ForegroundColor Green; ^
    Write-Host ' Protocol Handler Registered : studiq-agent://' -ForegroundColor Green; ^
    Write-Host ' Windows Startup Configured  : HKCU Run Key' -ForegroundColor Green; ^
    Write-Host '=========================================================='; ^
    Show-MsgBox (\"StudIQ Desktop Agent was installed successfully!\\n\\nLocation: \" + $installDir + \"\\n\\nBackground monitoring is active.\") 'StudIQ Setup Complete' 64; ^
} catch { ^
    Write-Host (\"[Setup Error] \" + $_.Exception.Message) -ForegroundColor Red; ^
    Show-MsgBox (\"StudIQ Agent setup failed:\\n\" + $_.Exception.Message) 'StudIQ Setup Error' 16; ^
    exit 1; ^
}
exit /b %ERRORLEVEL%

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
