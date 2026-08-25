import os
import sys
import subprocess
import time
import requests
import tempfile

backend_path = os.path.dirname(os.path.abspath(__file__))
installer_exe = os.path.join(backend_path, "desktop_agent", "installer", "StudIQAgentSetup.exe")

def test_exe_installer_flow():
    print("==========================================================")
    print("   TESTING NATIVE STANDALONE StudIQAgentSetup.exe FLOW   ")
    print("==========================================================")

    # 1. Confirm StudIQAgentSetup.exe exists
    assert os.path.exists(installer_exe), f"StudIQAgentSetup.exe missing at '{installer_exe}'"
    exe_size = os.path.getsize(installer_exe)
    print(f"[1/8] Verified StudIQAgentSetup.exe exists ({exe_size} bytes / {exe_size / (1024*1024):.2f} MB).")

    # 2. Execute StudIQAgentSetup.exe (--silent for automated headless test)
    print(f"[2/8] Launching standalone installer executable: {installer_exe} --silent")
    res = subprocess.run([installer_exe, "--silent"], capture_output=True, text=True)
    print(f"      Installer Exit Code: {res.returncode}")
    print(f"      Console Stdout: '{res.stdout.strip()}' (Expected empty - windowed GUI)")
    print(f"      Console Stderr: '{res.stderr.strip()}'")

    assert res.returncode == 0, f"Installer failed with exit code {res.returncode}"
    assert "BEGIN PAYLOAD" not in res.stdout, "No Base64 payload must be output to console!"

    # 3. Check Log File (%TEMP%\StudIQAgentSetup.log)
    temp_log = os.path.join(tempfile.gettempdir(), "StudIQAgentSetup.log")
    assert os.path.exists(temp_log), "Log file %TEMP%\\StudIQAgentSetup.log should exist!"
    print(f"\n[3/8] VERIFIED: Installer log file created at '{temp_log}'. Log preview:")
    with open(temp_log, "r", encoding="utf-8", errors="ignore") as f:
        log_lines = f.readlines()
        for l in log_lines[-10:]:
            print("  ", l.strip())

    # 4. Check Installed Executable Location
    local_app_data = os.getenv("LOCALAPPDATA", os.path.expanduser("~\\AppData\\Local"))
    install_dir = os.path.join(local_app_data, "StudIQ", "Agent")
    agent_exe = os.path.join(install_dir, "StudIQAgent.exe")

    if not os.path.exists(agent_exe):
        # Check if installed to dynamic drive fallback (e.g. D:\StudIQ\Agent)
        for drive_letter in ["D:\\", "E:\\", "C:\\"]:
            fallback = os.path.join(drive_letter, "StudIQ", "Agent", "StudIQAgent.exe")
            if os.path.exists(fallback):
                install_dir = os.path.dirname(fallback)
                agent_exe = fallback
                break

    assert os.path.exists(agent_exe), f"Installed StudIQAgent.exe missing at {agent_exe}"
    print(f"\n[4/8] VERIFIED: StudIQAgent.exe successfully installed at: {agent_exe}")

    # 5. Check Agent Daemon Process Running
    print("\n[5/8] Checking running daemon process...")
    task_res = subprocess.run('tasklist /FI "IMAGENAME eq StudIQAgent.exe"', capture_output=True, text=True, shell=True)
    print("      Tasklist Output:\n", task_res.stdout.strip())
    assert "StudIQAgent.exe" in task_res.stdout, "StudIQAgent.exe process should be running in memory"

    # 6. Check Local Bridge HTTP Status Endpoint
    print("\n[6/8] Checking Local Bridge (http://127.0.0.1:8765/status)...")
    bridge_ok = False
    for _ in range(5):
        try:
            r = requests.get("http://127.0.0.1:8765/status", timeout=2)
            if r.status_code == 200:
                print("      Bridge Status Response:", r.json())
                bridge_ok = True
                break
        except Exception:
            time.sleep(1)

    assert bridge_ok, "Local Bridge http://127.0.0.1:8765/status must return 200 OK!"

    # 7. Check Registry Protocol and Autostart Keys
    print("\n[7/8] Checking Windows Registry Keys...")
    reg_prot = subprocess.run('reg query HKCU\\Software\\Classes\\studiq-agent\\shell\\open\\command', capture_output=True, text=True, shell=True)
    assert reg_prot.returncode == 0, "studiq-agent:// protocol key must exist"
    print("      Protocol Key:", reg_prot.stdout.strip())

    reg_run = subprocess.run('reg query HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v StudIQAgent', capture_output=True, text=True, shell=True)
    assert reg_run.returncode == 0, "StudIQAgent Run key must exist"
    print("      Startup Key :", reg_run.stdout.strip())

    # 8. Test Re-install / Update Idempotency
    print("\n[8/8] Testing Reinstall / Update Idempotency...")
    reinstall_res = subprocess.run([installer_exe, "--silent"], capture_output=True, text=True)
    assert reinstall_res.returncode == 0, f"Reinstall failed with exit code {reinstall_res.returncode}"
    print("      Reinstall Exit Code: 0 (SUCCESS)")

    print("\n==========================================================")
    print("  SUCCESS: Standalone StudIQAgentSetup.exe Fully Verified!")
    print("==========================================================")

if __name__ == "__main__":
    test_exe_installer_flow()
