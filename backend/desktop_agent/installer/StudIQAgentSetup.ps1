# StudIQ Desktop Agent Installer PowerShell Core Engine
$ErrorActionPreference = 'Stop'

Add-Type -AssemblyName System.Windows.Forms -ErrorAction SilentlyContinue

function Show-MsgBox([string]$msg, [string]$title, [int]$icon = 64) {
    try {
        [System.Windows.Forms.MessageBox]::Show($msg, $title, [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]$icon) | Out-Null
    } catch {
        Write-Host "[$title] $msg"
    }
}

try {
    Write-Host '==========================================================' -ForegroundColor Cyan
    Write-Host '   StudIQ Windows Desktop Agent Native Setup Engine' -ForegroundColor Cyan
    Write-Host '==========================================================' -ForegroundColor Cyan
    Write-Host '[Setup] Resolving Windows per-user installation path...' -ForegroundColor Yellow

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
        Write-Host '[ERROR] Insufficient disk space on all drives.' -ForegroundColor Red
        Show-MsgBox 'StudIQ Agent setup failed: Insufficient free disk space on all local drives.' 'StudIQ Setup Error' 16
        exit 1
    }

    Write-Host "[Setup] Selected target directory: $installDir (Drive $targetDrive)" -ForegroundColor Green

    if (-not (Test-Path $installDir)) {
        New-Item -ItemType Directory -Path $installDir -Force | Out-Null
    }

    Write-Host '[Setup] Checking for active StudIQAgent processes...' -ForegroundColor Yellow
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

    Write-Host '[Setup] Extracting binary payload directly to installation drive...' -ForegroundColor Green
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

    Write-Host '[Setup] Configuring Windows Registry protocol and startup keys...' -ForegroundColor Green
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

    Write-Host '[Setup] Launching background StudIQ Agent daemon...' -ForegroundColor Green
    Start-Process -FilePath $exePath -ArgumentList 'studiq-agent://start' -WindowStyle Hidden

    Write-Host '==========================================================' -ForegroundColor Green
    Write-Host ' SUCCESS: StudIQ Desktop Agent Installed Successfully!' -ForegroundColor Green
    Write-Host " Installation Directory : $installDir" -ForegroundColor Green
    Write-Host ' Protocol Handler Registered : studiq-agent://' -ForegroundColor Green
    Write-Host ' Windows Startup Configured  : HKCU Run Key' -ForegroundColor Green
    Write-Host '==========================================================' -ForegroundColor Green

    Show-MsgBox "StudIQ Desktop Agent was installed successfully!`n`nLocation: $installDir`n`nBackground monitoring is active." "StudIQ Setup Complete" 64
} catch {
    Write-Host "[Setup Error] $($_.Exception.Message)" -ForegroundColor Red
    Show-MsgBox "StudIQ Agent setup failed:`n$($_.Exception.Message)" "StudIQ Setup Error" 16
    exit 1
}
