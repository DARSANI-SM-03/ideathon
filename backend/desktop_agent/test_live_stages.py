"""
Live Pipeline Stage Diagnostic Test
Examines all 8 stages of the StudIQ telemetry pipeline locally on Windows.
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collector import SystemActivityCollector
from classifier import ActivityClassifier
from sender import TelemetrySender
from config import AgentConfig
from app.auth.security import create_agent_token, decode_agent_token
from app.database.session import get_db, engine
from app.database.base import Base
from app.models.monitoring import ActivityLog
from fastapi.testclient import TestClient
from app.main import app

def test_stage_1_collector():
    print("\n--- STAGE 1: TESTING COLLECTOR (Windows Foreground Window API) ---")
    collector = SystemActivityCollector()
    snapshot = collector.collect_telemetry_snapshot()
    print(f"Captured Snapshot:")
    print(f"  appName     : {snapshot.get('appName')}")
    print(f"  windowTitle : {snapshot.get('windowTitle')}")
    print(f"  websiteUrl  : {snapshot.get('websiteUrl')}")
    print(f"  idleSeconds : {snapshot.get('idleSeconds')}")
    return snapshot

def test_stage_2_classifier(snapshot):
    print("\n--- STAGE 2: TESTING CLASSIFIER ---")
    classifier = ActivityClassifier()
    category, confidence = classifier.classify_with_confidence(
        snapshot["appName"], snapshot["windowTitle"], snapshot.get("websiteUrl", "")
    )
    print(f"Classifier Output: category='{category}', confidence={confidence}")
    return category, confidence

def test_stage_3_auth():
    print("\n--- STAGE 3: TESTING AGENT JWT TOKEN GENERATION & DECODING ---")
    student_id = 8888
    student_code = "STU-8888-TEST"
    token = create_agent_token({"student_id": student_id, "student_code": student_code, "scope": "telemetry"})
    print(f"Generated Token (length {len(token)})")
    
    decoded = decode_agent_token(token)
    print(f"Decoded Token Claims: student_id={decoded.get('student_id')}, student_code={decoded.get('student_code')}")
    assert decoded.get("student_id") == str(student_id) or decoded.get("student_id") == student_id
    return student_id, student_code, token

def test_stage_4_telemetry_post(student_id, student_code, token, snapshot, category, confidence):
    print("\n--- STAGE 4: TESTING POST /api/v1/monitoring/telemetry API ENDPOINT ---")
    client = TestClient(app)
    payload = {
        "agent_token": token,
        "student_id": student_id,
        "student_code": student_code,
        "application_name": snapshot["appName"],
        "window_title": snapshot["windowTitle"],
        "website_url": snapshot.get("websiteUrl", ""),
        "category": category,
        "confidence": confidence,
        "duration_seconds": 5,
        "idle_seconds": snapshot["idleSeconds"],
        "session_duration_seconds": snapshot["sessionDurationSeconds"],
        "running_apps_count": snapshot["runningAppsCount"],
        "timestamp": snapshot["timestamp"]
    }
    
    response = client.post("/api/v1/monitoring/telemetry", json=payload)
    print(f"HTTP Response Code: {response.status_code}")
    print(f"HTTP Response Body: {response.json()}")
    assert response.status_code == 200

def test_stage_5_db_verification(student_id):
    print("\n--- STAGE 5: TESTING DATABASE ActivityLog PERSISTENCE ---")
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    latest_log = db.query(ActivityLog).filter(
        ActivityLog.student_id == student_id
    ).order_by(ActivityLog.timestamp.desc()).first()
    
    assert latest_log is not None
    print(f"DB Row Found: ID={latest_log.id}, StudentID={latest_log.student_id}, App='{latest_log.application_name}', Title='{latest_log.window_title}', Category='{latest_log.category}'")

def test_stage_6_current_activity(token):
    print("\n--- STAGE 6: TESTING GET /api/v1/monitoring/current-activity ---")
    client = TestClient(app)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/monitoring/current-activity", headers=headers)
    print(f"GET /current-activity Status: {response.status_code}")
    data = response.json()
    print(f"Returned Data: current_application='{data.get('current_application')}', window_title='{data.get('window_title')}', category='{data.get('category')}'")
    assert data.get("current_application") != "Desktop Agent" or data.get("window_title") != "Awaiting Active Telemetry"

if __name__ == "__main__":
    print("==========================================================")
    print("   RUNNING HARD TELEMETRY PIPELINE STAGE DIAGNOSTIC")
    print("==========================================================")
    snap = test_stage_1_collector()
    cat, conf = test_stage_2_classifier(snap)
    sid, scode, tok = test_stage_3_auth()
    test_stage_4_telemetry_post(sid, scode, tok, snap, cat, conf)
    test_stage_5_db_verification(sid)
    test_stage_6_current_activity(tok)
    print("\nALL 6 DIAGNOSTIC STAGES EXECUTED SUCCESSFULLY!")
