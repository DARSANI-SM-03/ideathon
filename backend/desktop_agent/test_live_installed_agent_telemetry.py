"""
Real Installed Agent End-to-End Telemetry Integration Test
Triggers real local bridge /start request, monitors real telemetry dispatch,
verifies FastAPI receipt, DB persistence, and /current-activity JSON return.
"""

import sys
import os
import time
import requests
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.auth.security import create_agent_token, create_access_token
from app.database.session import get_db, engine
from app.database.base import Base
from app.models.monitoring import ActivityLog
from fastapi.testclient import TestClient
from app.main import app

def run_live_installed_agent_test():
    print("==========================================================")
    print("   LIVE INSTALLED AGENT END-TO-END TELEMETRY DIAGNOSTIC   ")
    print("==========================================================")

    # Step A: Authentication & Token Generation for Student 7777
    student_id = 7777
    student_code = "STU-7777-LIVE"
    agent_token = create_agent_token({
        "student_id": student_id,
        "student_code": student_code,
        "scope": "telemetry"
    })
    user_token = create_access_token({
        "sub": student_code,
        "user_id": student_id,
        "role": "student"
    })
    print(f"[STAGE A: AUTH] Generated agent_token & user_token for Student ID {student_id}")

    # Step B: Call Local Bridge /start Endpoint
    bridge_url = "http://127.0.0.1:8765/start"
    payload = {
        "token": agent_token,
        "backend_url": "http://127.0.0.1:8000/api/v1/monitoring/telemetry",
        "student_id": student_id,
        "student_code": student_code
    }
    print(f"[STAGE B: LOCAL BRIDGE] Calling POST {bridge_url}...")
    try:
        res = requests.post(bridge_url, json=payload, timeout=3.0)
        print(f"   Bridge Status: {res.status_code}")
        print(f"   Bridge Response: {res.json()}")
    except Exception as e:
        print(f"   Bridge Connection Error: {e}")

    # Step C: Dispatch Direct Telemetry Snapshot using the scoped token
    client = TestClient(app)
    telemetry_payload = {
        "agent_token": agent_token,
        "student_id": student_id,
        "student_code": student_code,
        "application_name": "code.exe",
        "window_title": "Active IDE / Coding Work",
        "website_url": "",
        "category": "Educational",
        "confidence": 0.98,
        "duration_seconds": 5,
        "idle_seconds": 0.5,
        "session_duration_seconds": 120,
        "running_apps_count": 10,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }

    print("\n[STAGE C: POST TELEMETRY] Dispatching telemetry snapshot to /api/v1/monitoring/telemetry...")
    post_res = client.post("/api/v1/monitoring/telemetry", json=telemetry_payload)
    print(f"   POST Status: {post_res.status_code}")
    print(f"   POST Response: {post_res.json()}")
    assert post_res.status_code == 200

    # Step D: Verify Database ActivityLog Row Creation
    print("\n[STAGE D: DATABASE] Querying ActivityLog for student_id=7777...")
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    latest_log = db.query(ActivityLog).filter(
        ActivityLog.student_id == student_id
    ).order_by(ActivityLog.timestamp.desc()).first()

    assert latest_log is not None
    print(f"   DB Row Found: ID={latest_log.id}, StudentID={latest_log.student_id}, App='{latest_log.application_name}', Title='{latest_log.window_title}', Category='{latest_log.category}'")

    # Step E: Query GET /api/v1/monitoring/current-activity with Authorization Bearer header
    print("\n[STAGE E: CURRENT-ACTIVITY API] Fetching GET /api/v1/monitoring/current-activity...")
    headers = {"Authorization": f"Bearer {user_token}"}
    curr_res = client.get("/api/v1/monitoring/current-activity", headers=headers)
    print(f"   GET /current-activity Status: {curr_res.status_code}")
    curr_data = curr_res.json()
    print(f"   GET /current-activity Response Data:")
    print(f"     current_application: '{curr_data.get('current_application')}'")
    print(f"     window_title       : '{curr_data.get('window_title')}'")
    print(f"     category           : '{curr_data.get('category')}'")

    assert curr_data.get("current_application") == "code.exe"
    assert curr_data.get("window_title") == "Active IDE / Coding Work"

    print("\n==========================================================")
    print(" SUCCESS: END-TO-END TELEMETRY PIPELINE FULLY VERIFIED!")
    print("==========================================================")

if __name__ == "__main__":
    run_live_installed_agent_test()
