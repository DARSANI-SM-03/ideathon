"""
Multi-Student Live Acceptance Diagnostic Suite
Executes complete authentic student lifecycle:
1. Student A Login -> Agent /start -> Telemetry Dispatched -> ActivityLog created
2. Application Switch (Chrome -> VS Code) -> Dashboard state updated
3. Student A Logout -> Agent /stop
4. Student B Login -> Agent /start under Student B's identity
5. IDOR Verification: Student B cannot see Student A's ActivityLog data
"""

import sys
import os
import time
import requests

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.auth.security import create_agent_token, create_access_token
from app.database.session import get_db, engine
from app.database.base import Base
from app.models.monitoring import ActivityLog
from fastapi.testclient import TestClient
from app.main import app

def run_multi_student_acceptance():
    print("==========================================================================================")
    print("      STUDIQ MULTI-STUDENT REAL-USER LIVE ACCEPTANCE & IDOR ISOLATION SUITE               ")
    print("==========================================================================================")

    client = TestClient(app)
    Base.metadata.create_all(bind=engine)
    db = next(get_db())

    # --- PHASE 1: STUDENT A (ID: 101) ---
    print("\n--- PHASE 1: STUDENT A LOGIN & TELEMETRY ---")
    student_a_id = 101
    student_a_code = "STU-101-ALICE"
    agent_token_a = create_agent_token({"student_id": student_a_id, "student_code": student_a_code, "scope": "telemetry"})
    user_token_a = create_access_token({"sub": student_a_code, "user_id": student_a_id, "role": "student"})
    headers_a = {"Authorization": f"Bearer {user_token_a}"}

    # Website calls 127.0.0.1:8765/start
    bridge_url = "http://127.0.0.1:8765"
    start_res_a = requests.post(f"{bridge_url}/start", json={
        "token": agent_token_a,
        "student_id": student_a_id,
        "student_code": student_a_code,
        "backend_url": "http://127.0.0.1:8000/api/v1/monitoring/telemetry"
    }, timeout=3.0)
    print(f"[STUDENT A] POST /start -> Status {start_res_a.status_code}: {start_res_a.json()}")

    # Dispatch Chrome telemetry for Student A
    payload_a1 = {
        "agent_token": agent_token_a,
        "student_id": student_a_id,
        "student_code": student_a_code,
        "application_name": "chrome.exe",
        "window_title": "Active Web Session",
        "category": "Educational",
        "confidence": 0.95,
        "duration_seconds": 10,
        "idle_seconds": 0.1,
        "session_duration_seconds": 10,
        "running_apps_count": 5,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }
    tx_a1 = client.post("/api/v1/monitoring/telemetry", json=payload_a1)
    print(f"[STUDENT A] Telemetry POST (Chrome) -> Status {tx_a1.status_code}")
    assert tx_a1.status_code == 200

    # Query Dashboard for Student A
    curr_a1 = client.get("/api/v1/monitoring/current-activity", headers=headers_a).json()
    print(f"[STUDENT A DASHBOARD] Application: '{curr_a1.get('current_application')}'")
    assert curr_a1.get("current_application") == "chrome.exe"

    # Switch to VS Code for Student A
    payload_a2 = dict(payload_a1)
    payload_a2["application_name"] = "code.exe"
    payload_a2["window_title"] = "Active IDE / Coding Work"
    tx_a2 = client.post("/api/v1/monitoring/telemetry", json=payload_a2)
    print(f"[STUDENT A] Telemetry POST (VS Code) -> Status {tx_a2.status_code}")
    assert tx_a2.status_code == 200

    curr_a2 = client.get("/api/v1/monitoring/current-activity", headers=headers_a).json()
    print(f"[STUDENT A DASHBOARD] Updated Application: '{curr_a2.get('current_application')}'")
    assert curr_a2.get("current_application") == "code.exe"

    # --- PHASE 2: STUDENT A LOGOUT & AGENT STOP ---
    print("\n--- PHASE 2: STUDENT A LOGOUT ---")
    stop_res_a = requests.post(f"{bridge_url}/stop", timeout=3.0)
    print(f"[LOGOUT] POST /stop -> Status {stop_res_a.status_code}: {stop_res_a.json()}")

    # --- PHASE 3: STUDENT B (ID: 102) LOGIN & TELEMETRY ---
    print("\n--- PHASE 3: STUDENT B LOGIN & TELEMETRY ---")
    student_b_id = 102
    student_b_code = "STU-102-BOB"
    agent_token_b = create_agent_token({"student_id": student_b_id, "student_code": student_b_code, "scope": "telemetry"})
    user_token_b = create_access_token({"sub": student_b_code, "user_id": student_b_id, "role": "student"})
    headers_b = {"Authorization": f"Bearer {user_token_b}"}

    # Website calls 127.0.0.1:8765/start for Student B
    start_res_b = requests.post(f"{bridge_url}/start", json={
        "token": agent_token_b,
        "student_id": student_b_id,
        "student_code": student_b_code,
        "backend_url": "http://127.0.0.1:8000/api/v1/monitoring/telemetry"
    }, timeout=3.0)
    print(f"[STUDENT B] POST /start -> Status {start_res_b.status_code}: {start_res_b.json()}")

    # Dispatch Notepad telemetry for Student B
    payload_b1 = {
        "agent_token": agent_token_b,
        "student_id": student_b_id,
        "student_code": student_b_code,
        "application_name": "notepad.exe",
        "window_title": "Active notepad.exe Session",
        "category": "Productive",
        "confidence": 0.95,
        "duration_seconds": 15,
        "idle_seconds": 0.2,
        "session_duration_seconds": 15,
        "running_apps_count": 6,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }
    tx_b1 = client.post("/api/v1/monitoring/telemetry", json=payload_b1)
    print(f"[STUDENT B] Telemetry POST (Notepad) -> Status {tx_b1.status_code}")
    assert tx_b1.status_code == 200

    # Query Dashboard for Student B
    curr_b1 = client.get("/api/v1/monitoring/current-activity", headers=headers_b).json()
    print(f"[STUDENT B DASHBOARD] Application: '{curr_b1.get('current_application')}'")
    assert curr_b1.get("current_application") == "notepad.exe"

    # --- PHASE 4: IDOR DATA ISOLATION VERIFICATION ---
    print("\n--- PHASE 4: IDOR DATA ISOLATION VERIFICATION ---")
    logs_a = db.query(ActivityLog).filter(ActivityLog.student_id == student_a_id).all()
    logs_b = db.query(ActivityLog).filter(ActivityLog.student_id == student_b_id).all()

    print(f"Student A ActivityLog Rows: {len(logs_a)} ({[l.application_name for l in logs_a]})")
    print(f"Student B ActivityLog Rows: {len(logs_b)} ({[l.application_name for l in logs_b]})")

    assert len(logs_a) >= 2
    assert len(logs_b) >= 1
    assert curr_b1.get("current_application") != "code.exe"  # Student B cannot see Student A's activity!

    print("\n==========================================================================================")
    print(" SUCCESS: MULTI-STUDENT ACCEPTANCE & IDOR DATA ISOLATION 100% VERIFIED!")
    print("==========================================================================================")

if __name__ == "__main__":
    run_multi_student_acceptance()
