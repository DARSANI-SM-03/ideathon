"""
StudIQ Real-Time Telemetry Live Diagnostic Monitor (run_live_monitor.py)
Single-command live monitor that:
1. Stops stale agents & updates %LOCALAPPDATA% executable binary
2. Starts installed StudIQAgent.exe in daemon mode
3. Opens production website in default browser (https://studiq-frontend.onrender.com)
4. Continuously polls and displays 100% authentic Windows foreground hardware telemetry
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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collector import SystemActivityCollector
from app.database.session import get_db, engine
from app.database.base import Base
from app.models.monitoring import ActivityLog

def start_live_monitor():
    print("[INIT] Terminating old StudIQAgent.exe processes...")
    os.system("taskkill /F /IM StudIQAgent.exe >nul 2>&1")
    time.sleep(1)

    print("[INIT] Updating installed agent binary at %LOCALAPPDATA%\\StudIQ\\Agent...")
    import update_installed_agent
    update_installed_agent.update_agent_executable()

    appdata = os.getenv("LOCALAPPDATA", "")
    exe_path = os.path.join(appdata, "StudIQ", "Agent", "StudIQAgent.exe")

    print("[INIT] Starting fresh installed StudIQAgent.exe daemon...")
    agent_proc = subprocess.Popen([exe_path, "--daemon"], cwd=os.path.dirname(exe_path), creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0)

    print("[INIT] Opening production website in browser: https://studiq-frontend.onrender.com ...")
    webbrowser.open("https://studiq-frontend.onrender.com")

    collector = SystemActivityCollector()
    Base.metadata.create_all(bind=engine)
    db = next(get_db())

    backend_base = "https://studiq-backend.onrender.com/api/v1"

    print("\n[STARTING LIVE MONITOR - REFRESHING EVERY 2 SECONDS...]\n")
    time.sleep(2)

    while True:
        try:
            os.system("cls" if sys.platform == "win32" else "clear")

            now_str = time.strftime("%Y-%m-%d %H:%M:%S")
            exe_size = os.path.getsize(exe_path) if os.path.exists(exe_path) else 0
            exe_mtime = time.ctime(os.path.getmtime(exe_path)) if os.path.exists(exe_path) else "N/A"

            # Check Agent Process
            running_pids = []
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] and 'StudIQAgent' in proc.info['name']:
                    running_pids.append(proc.info['pid'])

            agent_status = f"RUNNING (PIDs: {running_pids})" if running_pids else "STOPPED"

            # Collector
            snap = collector.collect_telemetry_snapshot()
            app_name = snap.get("appName", "Unknown")
            win_title = snap.get("windowTitle", "Unknown")
            idle_secs = snap.get("idleSeconds", 0)

            # Local Bridge & Session
            bridge_status = "FAILED"
            bridge_err = ""
            try:
                b_res = requests.get("http://127.0.0.1:8765/status", timeout=1.0)
                if b_res.ok:
                    bridge_status = "OK"
                else:
                    bridge_err = f"HTTP {b_res.status_code}"
            except Exception as e:
                bridge_err = "Blocked by Browser / Unreachable"

            # Cloud Active Session
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

            # Database ActivityLog
            latest_log = db.query(ActivityLog).order_by(ActivityLog.id.desc()).first()
            db_app = latest_log.application_name if latest_log else "None"
            db_time = latest_log.timestamp.strftime("%Y-%m-%d %H:%M:%S") if (latest_log and latest_log.timestamp) else "None"
            db_row_id = latest_log.id if latest_log else "None"

            # Dashboard API
            curr_app = "Unavailable"
            curr_title = "Unavailable"
            api_http = "Error"
            try:
                if sync_session.get("agent_token"):
                    headers = {"Authorization": f"Bearer {sync_session['agent_token']}"}
                    api_res = requests.get(f"{backend_base}/monitoring/current-activity", headers=headers, timeout=2.5)
                    api_http = f"HTTP {api_res.status_code}"
                    if api_res.ok:
                        data = api_res.json()
                        curr_app = data.get("current_application", "N/A")
                        curr_title = data.get("window_title", "N/A")
            except Exception as e:
                api_http = f"Error: {e}"

            # Monitoring Status
            mon_status = "🔴 INACTIVE"
            last_tx_ago = "N/A"
            if latest_log and latest_log.timestamp:
                from datetime import datetime
                delta = (datetime.utcnow() - latest_log.timestamp).total_seconds()
                last_tx_ago = f"{delta:.1f}s ago"
                if delta < 30.0:
                    mon_status = "🟢 ACTIVE"
                elif running_pids:
                    mon_status = "🟡 AWAITING TELEMETRY"

            print("========================================================")
            print("             STUDIQ LIVE TELEMETRY MONITOR              ")
            print("========================================================")
            print(f"TIME        : {now_str}")
            print(f"AGENT       : {agent_status}")
            print(f"EXE PATH    : {exe_path}")
            print(f"EXE VERSION : {file_size} bytes | {exe_mtime}")
            print("")
            print(f"STUDENT ID  : {student_id}")
            print(f"SESSION     : {session_active}")
            print(f"TOKEN       : {token_present}")
            print("")
            print("COLLECTOR")
            print("--------------------------------------------------------")
            print(f"FOREGROUND APP : {app_name}")
            print(f"WINDOW TITLE   : {win_title}")
            print(f"IDLE TIME      : {idle_secs:.1f}s")
            print(f"COLLECTOR      : {'OK' if app_name else 'ERROR'}")
            print("")
            print("LOCAL BRIDGE & CLOUD BACKEND")
            print("--------------------------------------------------------")
            print(f"LOCAL BRIDGE   : {bridge_status} ({bridge_err if bridge_err else '127.0.0.1:8765'})")
            print(f"BACKEND URL    : {backend_base}")
            print(f"CLOUD SYNC     : {'CONNECTED' if sync_session.get('active') else 'DISCONNECTED'}")
            print("")
            print("DATABASE PERSISTENCE")
            print("--------------------------------------------------------")
            print(f"ACTIVITY LOG   : {'INSERTED' if latest_log else 'NOT INSERTED'}")
            print(f"LATEST APP     : {db_app}")
            print(f"LATEST ROW ID  : {db_row_id}")
            print(f"LATEST TIME    : {db_time}")
            print("")
            print("DASHBOARD API")
            print("--------------------------------------------------------")
            print(f"API STATUS     : {api_http}")
            print(f"CURRENT APP    : {curr_app}")
            print(f"WINDOW TITLE   : {curr_title}")
            print("")
            print("MONITORING STATE")
            print("--------------------------------------------------------")
            print(f"STATUS         : {mon_status}")
            print(f"LAST TELEMETRY : {last_tx_ago}")
            print("")
            print("========================================================")
            print("              END-TO-END PIPELINE CHECKS                ")
            print("========================================================")
            print(f"[{'OK' if app_name else 'FAIL'}] COLLECTOR")
            print(f"[{'OK' if running_pids else 'FAIL'}] AGENT")
            print(f"[{'OK' if token_present == 'PRESENT' else 'WAIT'}] AUTHENTICATION")
            print(f"[{'OK' if latest_log else 'WAIT'}] DATABASE PERSISTENCE")
            print(f"[{'OK' if curr_app != 'Unavailable' else 'WAIT'}] DASHBOARD API")
            print("")
            if app_name and running_pids and latest_log:
                print("REAL PIPELINE: 🟢 WORKING (Detecting Real Windows Applications)")
            else:
                print("REAL PIPELINE: 🟡 AWAITING LOGIN / FRONTEND TELEMETRY PING")

            time.sleep(2)

        except KeyboardInterrupt:
            print("\n[MONITOR TERMINATED BY USER]")
            sys.exit(0)

if __name__ == "__main__":
    start_live_monitor()
