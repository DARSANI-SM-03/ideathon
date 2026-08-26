import os
import shutil
import sys
import subprocess
import time
import psutil

def update_installed_agent():
    print("==========================================================")
    print("   UPDATING INSTALLED AGENT IN %LOCALAPPDATA%\\StudIQ\\Agent")
    print("==========================================================")

    # 1. Force kill any running processes accessing StudIQ directory
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            name = (proc.info['name'] or '').lower()
            exe = (proc.info['exe'] or '').lower()
            if 'studiqagent' in name or 'studiq' in exe:
                print(f"Terminating running process PID {proc.info['pid']} ({proc.info['name']})...")
                proc.kill()
        except Exception:
            pass

    time.sleep(1)

    appdata = os.getenv("LOCALAPPDATA", "")
    target_dir = os.path.join(appdata, "StudIQ", "Agent")
    source_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist", "StudIQAgent")

    os.makedirs(target_dir, exist_ok=True)
    print(f"Source Directory: {source_dir}")
    print(f"Target Directory: {target_dir}")

    for item in os.listdir(source_dir):
        s = os.path.join(source_dir, item)
        d = os.path.join(target_dir, item)
        copied = False
        for attempt in range(5):
            try:
                if os.path.isdir(s):
                    if os.path.exists(d):
                        shutil.rmtree(d, ignore_errors=True)
                    shutil.copytree(s, d)
                else:
                    shutil.copy2(s, d)
                copied = True
                break
            except Exception as e:
                print(f"Attempt {attempt+1} failed copying {item}: {e}. Retrying...")
                time.sleep(1)
        if not copied:
            print(f"ERROR: Unable to replace {item} due to file lock.")

    installed_exe = os.path.join(target_dir, "StudIQAgent.exe")
    if os.path.exists(installed_exe):
        print(f"SUCCESS: Updated installed executable at '{installed_exe}'")
        print(f"File Size: {os.path.getsize(installed_exe)} bytes")

def update_agent_executable():
    return update_installed_agent()

if __name__ == "__main__":
    update_installed_agent()
