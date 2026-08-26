import os
import sys
import psutil
import json

def inspect_installed_agent():
    print("==========================================================")
    print("   INSPECTING LIVE INSTALLED AGENT & PROCESS ENVIRONMENT")
    print("==========================================================")

    appdata = os.getenv("LOCALAPPDATA", "")
    studiq_dir = os.path.join(appdata, "StudIQ")
    agent_exe = os.path.join(studiq_dir, "Agent", "StudIQAgent.exe")
    lock_file = os.path.join(studiq_dir, "agent.lock")
    log_file = os.path.join(studiq_dir, "agent_execution.log")
    queue_file = os.path.join(studiq_dir, "offline_queue.json")

    print(f"1. LOCALAPPDATA StudIQ Directory: {studiq_dir}")
    print(f"   Directory Exists? {os.path.exists(studiq_dir)}")
    print(f"   StudIQAgent.exe Exists? {os.path.exists(agent_exe)}")
    if os.path.exists(agent_exe):
        mtime = time.ctime(os.path.getmtime(agent_exe))
        size = os.path.getsize(agent_exe)
        print(f"   StudIQAgent.exe Modified: {mtime} | Size: {size} bytes")

    print(f"\n2. Checking Running Processes:")
    running_found = []
    for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
        try:
            name = (proc.info['name'] or '').lower()
            if 'studiq' in name or 'agent' in name or 'python' in name:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if 'agent' in cmdline.lower() or 'studiq' in cmdline.lower():
                    running_found.append(proc.info)
                    print(f"   PID {proc.info['pid']}: {proc.info['name']} | EXE: {proc.info['exe']} | CMD: {cmdline}")
        except Exception:
            pass

    if not running_found:
        print("   No running StudIQ process found under psutil scan.")

    print(f"\n3. Checking Execution Log ({log_file}):")
    if os.path.exists(log_file):
        try:
            with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
                print(f"   Total Log Lines: {len(lines)}")
                print("   --- Last 15 Log Entries ---")
                for line in lines[-15:]:
                    print("   " + line.strip())
        except Exception as e:
            print(f"   Error reading log: {e}")
    else:
        print("   Log file does not exist yet.")

    print(f"\n4. Checking Offline Queue ({queue_file}):")
    if os.path.exists(queue_file):
        try:
            with open(queue_file, "r", encoding="utf-8", errors="ignore") as f:
                qdata = json.load(f)
                print(f"   Queued Offline Telemetry Items: {len(qdata)}")
                if qdata:
                    sample = qdata[-1]
                    print(f"   Latest Queued Item: app='{sample.get('application_name')}', token_present={bool(sample.get('agent_token'))}, student_id={sample.get('student_id')}")
        except Exception as e:
            print(f"   Error reading offline queue: {e}")
    else:
        print("   Offline queue file does not exist.")

if __name__ == "__main__":
    import time
    inspect_installed_agent()
