"""
StudIQ Windows Desktop Agent Installer Entrypoint
==================================================
Standalone Windows setup script compiled with PyInstaller into StudIQAgentSetup.exe.
Installs StudIQAgent.exe to %LOCALAPPDATA%\\StudIQ\\Agent, registers studiq-agent://,
configures Windows startup, creates shortcuts, and launches the daemon.
"""

import sys
import os
import shutil
import winreg
import subprocess
import time

def get_base_dir():
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

def kill_running_agent():
    log_setup("Stopping active StudIQAgent processes if any...")
    try:
        subprocess.run(["taskkill", "/F", "/IM", "StudIQAgent.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        log_setup(f"taskkill note: {e}")

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
        log_setup(f"Shortcut creation error: {e}")

def create_uninstaller(install_dir: str):
    uninstall_bat = os.path.join(install_dir, "uninstall_studiq_agent.bat")
    content = """@echo off
title StudIQ Agent Uninstaller
echo Removing StudIQ Agent protocol, shortcuts, and files...
powershell -ExecutionPolicy Bypass -Command "Remove-Item -Path 'HKCU:\\Software\\Classes\\studiq-agent' -Recurse -Force -ErrorAction SilentlyContinue"
powershell -ExecutionPolicy Bypass -Command "$sm = [System.Environment]::GetFolderPath('Programs'); $lnk1 = Join-Path $sm 'StudIQ Desktop Agent.lnk'; if (Test-Path $lnk1) { Remove-Item $lnk1 -Force }; $dt = [System.Environment]::GetFolderPath('Desktop'); $lnk2 = Join-Path $dt 'StudIQ Desktop Agent.lnk'; if (Test-Path $lnk2) { Remove-Item $lnk2 -Force }"
powershell -ExecutionPolicy Bypass -Command "Remove-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run' -Name 'StudIQAgent' -ErrorAction SilentlyContinue"
taskkill /F /IM StudIQAgent.exe 2>nul
rmdir /S /Q "%LOCALAPPDATA%\\StudIQ\\Agent"
echo StudIQ Desktop Agent uninstalled.
pause
"""
    with open(uninstall_bat, "w", encoding="utf-8") as f:
        f.write(content)

def show_dialog(title: str, message: str):
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        messagebox.showinfo(title, message)
        root.destroy()
    except Exception:
        pass

def main():
    log_setup("Starting StudIQ Agent Setup...")
    base_dir = get_base_dir()
    
    local_app_data = os.getenv("LOCALAPPDATA", os.path.expanduser("~"))
    install_dir = os.path.join(local_app_data, "StudIQ", "Agent")
    os.makedirs(install_dir, exist_ok=True)
    
    kill_running_agent()
    
    # Locate payload directory containing StudIQAgent.exe & _internal
    payload_dir = os.path.join(base_dir, "payload")
    if not os.path.exists(payload_dir):
        payload_dir = os.path.join(base_dir, "dist", "StudIQAgent")
    if not os.path.exists(payload_dir):
        payload_dir = base_dir

    log_setup(f"Copying files from {payload_dir} to {install_dir}...")
    
    # Copy files from payload_dir to install_dir
    for item in os.listdir(payload_dir):
        s = os.path.join(payload_dir, item)
        d = os.path.join(install_dir, item)
        if os.path.isdir(s):
            if os.path.exists(d):
                shutil.rmtree(d, ignore_errors=True)
            shutil.copytree(s, d)
        else:
            shutil.copy2(s, d)
            
    exe_path = os.path.join(install_dir, "StudIQAgent.exe")
    if not os.path.exists(exe_path):
        log_setup(f"ERROR: {exe_path} missing after copy!")
        show_dialog("StudIQ Setup Error", f"Failed to install StudIQAgent.exe to {install_dir}")
        sys.exit(1)
        
    register_protocol_handler(exe_path)
    configure_autostart(exe_path)
    create_shortcuts(exe_path, install_dir)
    create_uninstaller(install_dir)
    
    log_setup("Launching StudIQAgent daemon...")
    CREATE_NO_WINDOW = 0x08000000
    CREATE_NEW_PROCESS_GROUP = 0x00000200
    flags = CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP
    
    subprocess.Popen([exe_path, "studiq-agent://start"], cwd=install_dir, creationflags=flags)
    
    log_setup("StudIQ Agent installation completed successfully.")
    show_dialog("StudIQ Agent Setup Complete", "StudIQ Desktop Agent was installed successfully and background monitoring has been started!")

if __name__ == "__main__":
    main()
