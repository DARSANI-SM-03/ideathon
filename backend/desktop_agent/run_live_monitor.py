"""
StudIQ Windows Desktop Monitoring Agent - Persistent Streaming Telemetry Console
Runs a real daemon streaming log every 5 seconds without clearing the screen or redrawing.
Hooks directly into collector.py, classifier.py, sender.py, and the production FastAPI backend.
"""

import sys
import os
import time
import subprocess
import webbrowser
import requests
import json
import logging

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
WORKSPACE_ROOT = os.path.dirname(PROJECT_ROOT)

sys.path.insert(0, SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)

from config import AgentConfig
from collector import SystemActivityCollector
from classifier import ActivityClassifier
from sender import TelemetrySender
import update_installed_agent

class ClassificationLogCapture(logging.Handler):
    def __init__(self):
        super().__init__()
        self.last_rule = "Standard Rule Engine Match"
        self.last_keyword = "N/A"

    def emit(self, record):
        msg = record.getMessage()
        for line in msg.splitlines():
            if "Matched Rule:" in line:
                self.last_rule = line.split("Matched Rule:", 1)[1].strip()
            elif "Matched Keyword:" in line:
                self.last_keyword = line.split("Matched Keyword:", 1)[1].strip()

def run_persistent_streaming_monitor():
    print("[INIT] Terminating old StudIQAgent.exe processes...")
    os.system("taskkill /F /IM StudIQAgent.exe >nul 2>&1")
    time.sleep(1)

    print("[INIT] Verifying and updating installed agent binary at %LOCALAPPDATA%\\StudIQ\\Agent...")
    update_installed_agent.update_installed_agent()

    appdata = os.getenv("LOCALAPPDATA", "")
    exe_path = os.path.join(appdata, "StudIQ", "Agent", "StudIQAgent.exe")

    print(f"[INIT] Starting installed agent daemon: '{exe_path}'...")
    subprocess.Popen([exe_path, "--daemon"], cwd=os.path.dirname(exe_path), creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0)

    print("[INIT] Opening production website: https://studiq-frontend.onrender.com ...")
    webbrowser.open("https://studiq-frontend.onrender.com")

    backend_base = "https://studiq-backend.onrender.com/api/v1"
    os.environ["STUDIQ_BACKEND_URL"] = f"{backend_base}/monitoring/update"

    # Initialize Real Pipeline Components
    collector = SystemActivityCollector()
    classifier = ActivityClassifier()
    sender = TelemetrySender(f"{backend_base}/monitoring/update")

    log_capture = ClassificationLogCapture()
    classifier_logger = logging.getLogger("ActivityClassifier")
    classifier_logger.addHandler(log_capture)

    # Fetch Active Cloud Session
    student_id = 701
    student_code = "STU-701-ALICE"
    agent_token = ""

    try:
        s_res = requests.get(f"{backend_base}/monitoring/agent/active-session", timeout=3.0)
        if s_res.ok:
            s_data = s_res.json()
            if s_data.get("active"):
                student_id = s_data.get("student_id", student_id)
                student_code = s_data.get("student_code", student_code)
                agent_token = s_data.get("agent_token", "")
                os.environ["STUDIQ_AGENT_TOKEN"] = agent_token
                os.environ["STUDIQ_STUDENT_ID"] = str(student_id)
                os.environ["STUDIQ_STUDENT_CODE"] = student_code
    except Exception:
        pass

    # Print Persistent Startup Header
    print("\n==========================================================")
    print("   STUDIQ WINDOWS DESKTOP MONITORING AGENT v1.0")
    print("   AI Digital Behaviour Intelligence Daemon")
    print("==========================================================")
    print(f"Target Backend API : {backend_base}")
    print(f"Student ID         : {student_code} (ID: {student_id})")
    print("Sampling Frequency : Every 5 seconds")
    print("Privacy Guarantee  : Zero access to Gallery, Passwords, Bank Apps, Files, Messages")
    print("----------------------------------------------------------\n")
    print("[Agent Loop Started] Monitoring active foreground windows...\n")
    sys.stdout.flush()

    time.sleep(2)

    while True:
        try:
            # 1. Real Windows Collector Capture
            try:
                snap = collector.collect_telemetry_snapshot()
                app_name = snap.get("appName", "Unknown")
                win_title = snap.get("windowTitle", "")
                website_url = snap.get("websiteUrl", "")
                idle_secs = snap.get("idleSeconds", 0.0)
                sess_dur = snap.get("sessionDurationSeconds", 0)
                collector_err = False
            except Exception as e:
                app_name = "ERROR"
                win_title = "NOT AVAILABLE"
                website_url = ""
                idle_secs = 0.0
                sess_dur = 0
                collector_err = True

            if collector_err:
                print("[TELEMETRY PIPELINE TRACE]")
                print("  1. Collector Output : ERROR")
                print("  2. Classifier Input  : NOT AVAILABLE")
                print("  3. Classifier Result : NOT AVAILABLE")
                print("  4. JSON Dispatched   : NOT SENT")
                print("  5. Backend Response  : NOT SENT")
                print("----------------------------------------------------------\n")
                sys.stdout.flush()
                time.sleep(5)
                continue

            # 2. Real AI Classification
            log_capture.last_rule = "Standard Rule Engine Match"
            log_capture.last_keyword = "N/A"
            category, confidence = classifier.classify_activity(app_name, win_title, website_url)

            rule_used = log_capture.last_rule
            keyword_used = log_capture.last_keyword

            # 3. Build Telemetry Payload
            cur_token = os.getenv("STUDIQ_AGENT_TOKEN", agent_token)
            cur_student_id = int(os.getenv("STUDIQ_STUDENT_ID", str(student_id)))
            cur_student_code = os.getenv("STUDIQ_STUDENT_CODE", student_code)

            payload = {
                "student_id": cur_student_id,
                "student_code": cur_student_code,
                "agent_token": cur_token,
                "application_name": app_name,
                "window_title": win_title,
                "website_url": website_url,
                "category": category,
                "confidence": confidence,
                "idle_seconds": idle_secs,
                "session_duration_seconds": sess_dur
            }

            # 4. Dispatch Telemetry via TelemetrySender over HTTPS
            success, resp_data = sender.send_telemetry(payload)

            if success:
                http_status = "200 OK"
                res_msg = "persistent"
                if isinstance(resp_data, dict) and resp_data.get("status"):
                    res_msg = resp_data.get("status")
                backend_res_str = f"[{http_status} {res_msg}]"
            else:
                backend_res_str = "[OFFLINE / Connection Refused or Failed]"

            # 5. Output Persistent Telemetry Trace (NEVER CLEAR SCREEN)
            print("[TELEMETRY PIPELINE TRACE]")
            print(f"  1. Collector Output : App='{app_name}' | Title='{win_title}' | URL='{website_url}'")
            print(f"  2. Classifier Input  : App='{app_name}' | Title='{win_title}' | URL='{website_url}'")
            print("")
            print("[CLASSIFIER LOG]")
            print(f"Matched Rule: {rule_used}")
            if keyword_used != "N/A":
                print(f"Matched Keyword: {keyword_used}")
            print(f"Final Category: {category}")
            print(f"Confidence: {confidence}")
            print("")
            print(f"  3. Classifier Result: Category='{category}' | Confidence={confidence}")
            print(f"  4. JSON Dispatched   : App='{app_name}' | Category='{category}'")
            print(f"  5. Backend Response  : {backend_res_str}")
            print("----------------------------------------------------------\n")
            sys.stdout.flush()

            time.sleep(5)

        except KeyboardInterrupt:
            print("\n[Agent Loop Stopped by User]")
            sys.exit(0)

if __name__ == "__main__":
    run_persistent_streaming_monitor()
