"""
StudIQ Windows Desktop Agent Installer Entrypoint
==================================================
Standalone Windows setup installer compiled with PyInstaller into StudIQAgentSetup.exe.
1. Uses drive_selector to dynamically determine optimal installation drive (zero hardcoded paths).
2. Performs graceful process shutdown and file handle release polling (prevents WinError 32).
3. Extracts bundled StudIQAgent.zip payload directly to target drive (prevents C: Error 112).
4. Registers studiq-agent:// protocol handler in HKCU.
5. Configures HKCU Run key for automatic Windows startup.
6. Creates Start Menu and Desktop shortcuts.
7. Generates uninstaller and launches agent daemon.
"""

import sys
import os
import shutil
import winreg
import subprocess
import time
import zipfile
import urllib.request
import urllib.parse
from drive_selector import select_optimal_installation_path, REQUIRED_FREE_SPACE_BYTES

LOCAL_BRIDGE_URL = "http://127.0.0.1:8765"

def get_base_dir() -> str:
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def log_setup(msg: str):
    try:
        appdata = os.getenv("LOCALAPPDATA", os.path.expanduser("~"))
        log_dir = os.path.join(appdata, "StudIQ")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "installer_setup.log")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except Exception:
        pass

def show_dialog(title: str, message: str, is_error: bool = False):
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        if is_error:
            messagebox.showerror(title, message)
        else:
            messagebox.showinfo(title, message)
        root.destroy()
    except Exception:
        pass

def gracefully_stop_running_agent():
    log_setup("Detecting running StudIQAgent / bridge instances...")
    # 1. Try HTTP /stop request to bridge daemon
    try:
        req = urllib.request.Request(f"{LOCAL_BRIDGE_URL}/stop", method="POST", data=b"{}")
        with urllib.request.urlopen(req, timeout=2.0) as resp:
            log_setup("[Shutdown] HTTP /stop sent successfully.")
    except Exception as e:
        log_setup(f"[Shutdown] HTTP /stop note: {e}")

    time.sleep(1.0)

    # 2. Terminate StudIQAgent.exe processes if still running
    try:
        subprocess.run(["taskkill", "/F", "/IM", "StudIQAgent.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        log_setup(f"[Shutdown] taskkill note: {e}")

    time.sleep(0.5)

def wait_for_file_lock_release(exe_path: str, max_retries: int = 10) -> bool:
    """Polls open file handle to verify StudIQAgent.exe is unlocked before replacing."""
    if not os.path.exists(exe_path):
        return True

    log_setup(f"Polling file lock handle release for {exe_path}...")
    for attempt in range(max_retries):
        try:
            with open(exe_path, "r+b") as f:
                pass
            log_setup(f"File handle verified released on attempt {attempt + 1}.")
            return True
        except PermissionError:
            log_setup(f"Attempt {attempt + 1}/{max_retries}: File is still locked by process. Waiting...")
            time.sleep(0.5)
        except Exception as e:
            log_setup(f"File handle check note: {e}")
            break

    return False

def register_protocol_handler(exe_path: str):
    log_setup(f"Registering studiq-agent:// protocol for exe: {exe_path}")
    key_path = r"Software\Classes\studiq-agent"
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
        winreg.SetValue(key, "", winreg.REG_SZ, "URL:StudIQ Agent Protocol")
        winreg.SetValueEx(key, "URL Protocol", 0, winreg.REG_SZ, "")

    cmd_path = r"Software\Classes\studiq-agent\shell\open\command"
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, cmd_path) as key:
        winreg.SetValue(key, "", winreg.REG_SZ, f'"{exe_path}" "%1"')

def configure_autostart(exe_path: str):
    log_setup("Configuring HKCU Run key for automatic Windows startup...")
    run_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, run_key, 0, winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key, "StudIQAgent", 0, winreg.REG_SZ, f'"{exe_path}" "studiq-agent://start"')

def create_shortcuts(exe_path: str, install_dir: str):
    log_setup("Creating Start Menu and Desktop shortcuts...")
    ps_cmd = f"""
    $WshShell = New-Object -ComObject WScript.Shell
    $sm = [System.Environment]::GetFolderPath('Programs')
    if ($sm) {{
        $s1 = $WshShell.CreateShortcut((Join-Path $sm 'StudIQ Desktop Agent.lnk'))
        $s1.TargetPath = '{exe_path}'
        $s1.Arguments = 'studiq-agent://start'
        $s1.WorkingDirectory = '{install_dir}'
        $s1.Save()
    }}
    $dt = [System.Environment]::GetFolderPath('Desktop')
    if ($dt) {{
        $s2 = $WshShell.CreateShortcut((Join-Path $dt 'StudIQ Desktop Agent.lnk'))
        $s2.TargetPath = '{exe_path}'
        $s2.Arguments = 'studiq-agent://start'
        $s2.WorkingDirectory = '{install_dir}'
        $s2.Save()
    }}
    """
    try:
        subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        log_setup(f"Shortcut creation note: {e}")

def create_uninstaller(install_dir: str):
    uninstall_bat = os.path.join(install_dir, "uninstall_studiq_agent.bat")
    content = f"""@echo off
title StudIQ Agent Uninstaller
echo Removing StudIQ Agent protocol, shortcuts, and files...
powershell -ExecutionPolicy Bypass -Command "Remove-Item -Path 'HKCU:\\Software\\Classes\\studiq-agent' -Recurse -Force -ErrorAction SilentlyContinue"
powershell -ExecutionPolicy Bypass -Command "$sm = [System.Environment]::GetFolderPath('Programs'); $lnk1 = Join-Path $sm 'StudIQ Desktop Agent.lnk'; if (Test-Path $lnk1) {{ Remove-Item $lnk1 -Force }}; $dt = [System.Environment]::GetFolderPath('Desktop'); $lnk2 = Join-Path $dt 'StudIQ Desktop Agent.lnk'; if (Test-Path $lnk2) {{ Remove-Item $lnk2 -Force }}"
powershell -ExecutionPolicy Bypass -Command "Remove-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run' -Name 'StudIQAgent' -ErrorAction SilentlyContinue"
taskkill /F /IM StudIQAgent.exe 2>nul
rmdir /S /Q "{install_dir}"
echo StudIQ Desktop Agent uninstalled.
pause
"""
    try:
        with open(uninstall_bat, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        log_setup(f"Uninstaller creation note: {e}")

def main():
    log_setup("==========================================================")
    log_setup("   STARTING STUDIQ AGENT INSTALLER EXECUTION              ")
    log_setup("==========================================================")

    # 1. Dynamic Drive Selection
    install_dir, selected_drive, diag = select_optimal_installation_path(REQUIRED_FREE_SPACE_BYTES)
    log_setup(f"Drive Diagnostics: {diag}")

    if not install_dir or not selected_drive:
        msg = "StudIQ Agent cannot be installed because there is not enough free disk space on any local drive."
        log_setup(f"ERROR: {msg}")
        show_dialog("StudIQ Setup Error", msg, is_error=True)
        sys.exit(1)

    log_setup(f"Selected Target Installation Path: {install_dir} (Drive {selected_drive})")
    os.makedirs(install_dir, exist_ok=True)

    # 2. Stop running agent & release file handles (Fix WinError 32)
    gracefully_stop_running_agent()

    exe_path = os.path.join(install_dir, "StudIQAgent.exe")
    if not wait_for_file_lock_release(exe_path, max_retries=10):
        log_setup(f"WARNING: File {exe_path} remains locked after retries. Attempting forced replacement...")

    # 3. Locate and extract StudIQAgent.zip payload directly to install_dir
    base_dir = get_base_dir()
    zip_payload_path = os.path.join(base_dir, "StudIQAgent.zip")
    if not os.path.exists(zip_payload_path):
        zip_payload_path = os.path.join(base_dir, "installer", "StudIQAgent.zip")

    if not os.path.exists(zip_payload_path):
        # Fallback to direct directory copy if zip is not packaged
        source_dir = os.path.join(base_dir, "payload")
        if not os.path.exists(source_dir):
            source_dir = os.path.join(base_dir, "dist", "StudIQAgent")

        if os.path.exists(source_dir):
            log_setup(f"Extracting directory payload from {source_dir} to {install_dir}...")
            for item in os.listdir(source_dir):
                s = os.path.join(source_dir, item)
                d = os.path.join(install_dir, item)
                if os.path.isdir(s):
                    if os.path.exists(d):
                        shutil.rmtree(d, ignore_errors=True)
                    shutil.copytree(s, d)
                else:
                    shutil.copy2(s, d)
        else:
            msg = "StudIQ Agent payload archive (StudIQAgent.zip) was not found in setup package."
            log_setup(f"ERROR: {msg}")
            show_dialog("StudIQ Setup Error", msg, is_error=True)
            sys.exit(1)
    else:
        log_setup(f"Extracting StudIQAgent.zip payload to {install_dir}...")
        try:
            with zipfile.ZipFile(zip_payload_path, 'r') as zip_ref:
                zip_ref.extractall(install_dir)
            log_setup("Zip payload extracted successfully.")
        except Exception as e:
            msg = f"Failed to extract StudIQAgent.zip: {e}"
            log_setup(f"ERROR: {msg}")
            show_dialog("StudIQ Setup Error", msg, is_error=True)
            sys.exit(1)

    # Verify StudIQAgent.exe exists after extraction
    if not os.path.exists(exe_path):
        msg = f"StudIQAgent.exe missing at {exe_path} after setup extraction."
        log_setup(f"ERROR: {msg}")
        show_dialog("StudIQ Setup Error", msg, is_error=True)
        sys.exit(1)

    log_setup(f"Verified executable file exists at: {exe_path}")

    # 4. System Registrations & Shortcuts
    register_protocol_handler(exe_path)
    configure_autostart(exe_path)
    create_shortcuts(exe_path, install_dir)
    create_uninstaller(install_dir)

    # 5. Launch Background Monitoring Agent
    log_setup("Launching StudIQAgent daemon process...")
    CREATE_NO_WINDOW = 0x08000000
    CREATE_NEW_PROCESS_GROUP = 0x00000200
    flags = CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP

    try:
        subprocess.Popen([exe_path, "studiq-agent://start"], cwd=install_dir, creationflags=flags)
        log_setup("StudIQ Agent process launched successfully.")
    except Exception as e:
        log_setup(f"Error launching agent daemon: {e}")

    show_dialog("StudIQ Agent Setup Complete", f"StudIQ Desktop Agent was installed successfully!\n\nLocation: {install_dir}\nMonitoring service is active.")

if __name__ == "__main__":
    main()
