"""
StudIQ Real-Time Telemetry Live Monitor (run_live_monitor.py)
Dedicated real-time diagnostic console that polls authentic Windows hardware activity,
local bridge status, SQLite database ActivityLog records, and production backend APIs.
Displays a 5-event recent history stream and updates continuously every 1-2 seconds.
"""

import sys
import os
import time
import subprocess
import webbrowser
import requests
import json
import psutil

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Absolute path resolution from script location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
WORKSPACE_ROOT = os.path.dirname(PROJECT_ROOT)

sys.path.insert(0, SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)

from collector import SystemActivityCollector
from app.database.session import get_db, engine
from app.database.base import Base
from app.models.monitoring import ActivityLog

def start_live_telemetry_monitor():
    print("[INIT] Stopping any stale StudIQAgent.exe processes...")
    os.system("taskkill /F /IM StudIQAgent.exe >nul 2>&1")
    time.sleep(1)

    print("[INIT] Verifying and updating installed executable in %LOCALAPPDATA%\\StudIQ\\Agent...")
    import update_installed_agent
    update_installed_agent.update_agent_executable()

    appdata = os.getenv("LOCALAPPDATA", "")
    exe_path = os.path.join(appdata, "StudIQ", "Agent", "StudIQAgent.exe")

    print(f"[INIT] Starting installed agent daemon: '{exe_path}'...")
    subprocess.Popen([exe_path, "--daemon"], cwd=os.path.dirname(exe_path), creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0)

    print("[INIT] Opening production website: https://studiq-frontend.onrender.com ...")
    webbrowser.open("https://studiq-frontend.onrender.com")

    collector = SystemActivityCollector()
    Base.metadata.create_all(bind=engine)
    db = next(get_db())

    backend_base = "https://studiq-backend.onrender.com/api/v1"

    print("\n[STUDIQ REAL-TIME MONITOR LAUNCHED — REFRESHING EVERY 1.5 SECONDS...]\n")
    time.sleep(2)

    while True:
        try:
            os.system("cls" if sys.platform == "win32" else "clear")

            now_str = time.strftime("%Y-%m-%d %H:%M:%S")
            exe_size = os.path.getsize(exe_path) if os.path.exists(exe_path) else 0
            exe_mtime = time.ctime(os.path.getmtime(exe_path)) if os.path.exists(exe_path) else "N/A"

            # Check Agent PIDs
            running_pids = []
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] and 'StudIQAgent' in proc.info['name']:
                    running_pids.append(proc.info['pid'])

            agent_status = f"RUNNING (PID: {running_pids[0]})" if running_pids else "STOPPED"
            agent_pid_str = str(running_pids[0]) if running_pids else "NONE"

            # Real Windows Foreground Collector
            snap = collector.collect_telemetry_snapshot()
            app_name = snap.get("appName", "Unknown")
            win_title = snap.get("windowTitle", "Unknown")
            idle_secs = snap.get("idleSeconds", 0.0)

            # Cloud Active Session Lookup
            sync_session = {}
            try:
                s_res = requests.get(f"{backend_base}/monitoring/agent/active-session", timeout=2.0)
                if s_res.ok:
                    sync_session = s_res.json()
            except Exception:
                pass

            student_id = sync_session.get("student_id", "NOT SYNCED")
            session_active = "ACTIVE" if sync_session.get("active") else "INACTIVE"
            token_present = "PRESENT" if sync_session.get("agent_token") else "MISSING"

            # Local Bridge Status
            bridge_res_str = "HTTP 200 OK"
            bridge_conn = "CONNECTED"
            try:
                b_res = requests.get("http://127.0.0.1:8765/status", timeout=1.0)
                if not b_res.ok:
                    bridge_res_str = f"HTTP {b_res.status_code}"
                    bridge_conn = "ERROR"
            except Exception:
                bridge_res_str = "BLOCKED BY BROWSER / UNREACHABLE"
                bridge_conn = "DISCONNECTED"

            # SQLite Database Query for Latest ActivityLog
            latest_log = db.query(ActivityLog).order_by(ActivityLog.id.desc()).first()
            db_app = latest_log.application_name if latest_log else "None"
            db_time = latest_log.timestamp.strftime("%H:%M:%S") if (latest_log and latest_log.timestamp) else "None"
            db_category = latest_log.category if latest_log else "None"
            db_confidence = f"{latest_log.confidence:.2f}" if (latest_log and latest_log.confidence) else "None"
            db_status_str = "INSERTED" if latest_log else "NOT RECEIVED"

            # Fetch Last 5 Real ActivityLog Events
            last_5_logs = db.query(ActivityLog).order_by(ActivityLog.id.desc()).limit(5).all()

            # Dashboard API Polling
            curr_app = "Unavailable"
            curr_title = "Unavailable"
            api_status = "HTTP 401"
            if sync_session.get("agent_token"):
                try:
                    headers = {"Authorization": f"Bearer {sync_session['agent_token']}"}
                    api_res = requests.get(f"{backend_base}/monitoring/current-activity", headers=headers, timeout=2.5)
                    api_status = f"HTTP {api_res.status_code}"
                    if api_res.ok:
                        data = api_res.json()
                        curr_app = data.get("current_application", "N/A")
                        curr_title = data.get("window_title", "N/A")
                except Exception as e:
                    api_status = f"Error: {e}"

            # Calculate Monitoring Status
            mon_label = "🔴 TELEMETRY STOPPED"
            last_sec_ago = "N/A"
            delta_sec = 999.0

            if latest_log and latest_log.timestamp:
                from datetime import datetime
                delta_sec = (datetime.utcnow() - latest_log.timestamp).total_seconds()
                last_sec_ago = f"{delta_sec:.1f}s ago"

            if delta_sec < 30.0:
                mon_label = "🟢 REAL TELEMETRY ACTIVE"
            elif running_pids:
                mon_label = "🟡 AGENT RUNNING — WAITING FOR TELEMETRY"

            print("============================================================")
            print("              STUDIQ REAL-TIME TELEMETRY                    ")
            print("============================================================")
            print(f"TIME        : {now_str}")
            print(f"AGENT       : {agent_status}")
            print(f"AGENT PID   : {agent_pid_str}")
            print(f"EXE         : {exe_path}")
            print(f"VERSION     : {exe_size} bytes | {exe_mtime}")
            print("")
            print("STUDENT SESSION")
            print("------------------------------------------------------------")
            print(f"STUDENT ID  : {student_id}")
            print(f"SESSION     : {session_active}")
            print(f"TOKEN       : {token_present}")
            print("")
            print("WINDOWS COLLECTOR")
            print("------------------------------------------------------------")
            print(f"FOREGROUND APP : {app_name}")
            print(f"WINDOW TITLE   : {win_title}")
            print(f"IDLE TIME      : {idle_secs:.1f}s")
            print(f"COLLECTOR      : {'OK' if app_name else 'ERROR'}")
            print("")
            print("TELEMETRY & SENDER")
            print("------------------------------------------------------------")
            print(f"LAST CAPTURE   : {now_str}")
            print(f"LAST SEND      : {db_time}")
            print(f"SEND STATUS    : {bridge_res_str}")
            print(f"LAST APP       : {db_app}")
            print(f"CATEGORY       : {db_category}")
            print(f"CONFIDENCE     : {db_confidence}")
            print("")
            print("BACKEND & DATABASE")
            print("------------------------------------------------------------")
            print(f"BACKEND URL    : {backend_base}")
            print(f"CONNECTION     : {bridge_conn}")
            print(f"DATABASE       : {db_status_str}")
            print(f"LATEST APP     : {db_app}")
            print(f"LATEST TIME    : {db_time}")
            print("")
            print("DASHBOARD API")
            print("------------------------------------------------------------")
            print(f"API STATUS     : {api_status}")
            print(f"CURRENT APP    : {curr_app}")
            print(f"WINDOW TITLE   : {curr_title}")
            print("")
            print("MONITORING STATUS")
            print("------------------------------------------------------------")
            print(f"STATUS         : {mon_label}")
            print(f"LAST TELEMETRY : {last_sec_ago}")
            print("")
            print("============================================================")
            print("              RECENT 5 REAL TELEMETRY EVENTS                ")
            print("============================================================")
            if last_5_logs:
                for l in reversed(last_5_logs):
                    t_str = l.timestamp.strftime("%H:%M:%S") if l.timestamp else "N/A"
                    print(f"[{t_str}] {l.application_name:<18} -> {l.category}")
            else:
                print("No ActivityLog entries recorded yet.")
            print("")
            print("============================================================")
            print("              LIVE PIPELINE CHECKS                          ")
            print("============================================================")
            print(f"[{'OK' if app_name else 'FAIL'}] WINDOWS COLLECTOR")
            print(f"[{'OK' if running_pids else 'FAIL'}] AGENT")
            print(f"[{'OK' if token_present == 'PRESENT' else 'FAIL'}] STUDENT SESSION")
            print(f"[{'OK' if latest_log else 'FAIL'}] DATABASE INSERT")
            print(f"[{'OK' if curr_app != 'Unavailable' else 'FAIL'}] DASHBOARD API")
            print(f"[{'OK' if delta_sec < 30.0 else 'FAIL'}] LIVE MONITORING")
            print("============================================================")

            time.sleep(1.5)

        except KeyboardInterrupt:
            print("\n[MONITOR TERMINATED BY USER]")
            sys.exit(0)

if __name__ == "__main__":
    start_live_telemetry_monitor()
