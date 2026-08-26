"""
StudIQ Live End-to-End Telemetry Pipeline Integration Test
Verifies real-world collector snapshot dispatch, authenticated API endpoint receipt,
database persistence, and current-activity retrieval.
"""

import unittest
import time
import os
import sys

# Ensure backend path is on import path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app
from app.database.session import get_db, engine
from app.database.base import Base
from app.models.monitoring import ActivityLog
from app.auth.security import create_agent_token
from desktop_agent.collector import SystemActivityCollector
from desktop_agent.classifier import ActivityClassifier

class TestLiveTelemetryPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        cls.client = TestClient(app)
        cls.student_id = 9999
        cls.student_code = "STU-TEST-9999"
        cls.agent_token = create_agent_token({
            "student_id": cls.student_id,
            "student_code": cls.student_code,
            "scope": "telemetry"
        })

    def test_01_real_collector_snapshot(self):
        collector = SystemActivityCollector()
        snapshot = collector.collect_telemetry_snapshot()
        self.assertIn("appName", snapshot)
        self.assertIn("windowTitle", snapshot)
        self.assertIn("idleSeconds", snapshot)
        print(f"[TEST 1 PASS] Real Collector Snapshot: appName='{snapshot['appName']}', windowTitle='{snapshot['windowTitle']}'")

    def test_02_telemetry_dispatch_and_database_persistence(self):
        collector = SystemActivityCollector()
        classifier = ActivityClassifier()
        snapshot = collector.collect_telemetry_snapshot()
        category, confidence = classifier.classify_with_confidence(
            snapshot["appName"], snapshot["windowTitle"], snapshot.get("websiteUrl", "")
        )

        payload = {
            "agent_token": self.agent_token,
            "student_id": self.student_id,
            "student_code": self.student_code,
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

        # Dispatch telemetry to API
        response = self.client.post("/api/v1/monitoring/telemetry", json=payload)
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        self.assertEqual(res_json["status"], "success")

        # Verify DB query
        db = next(get_db())
        latest_log = db.query(ActivityLog).filter(
            ActivityLog.student_id == self.student_id
        ).order_by(ActivityLog.timestamp.desc()).first()

        self.assertIsNotNone(latest_log)
        self.assertEqual(latest_log.application_name, snapshot["appName"])
        self.assertEqual(latest_log.window_title, snapshot["windowTitle"])
        print(f"[TEST 2 PASS] Telemetry API & DB Persistence verified: App='{latest_log.application_name}', Category='{latest_log.category}'")

    def test_03_current_activity_endpoint_retrieval(self):
        # Retrieve current activity for authenticated student
        headers = {"Authorization": f"Bearer {self.agent_token}"}
        response = self.client.get("/api/v1/monitoring/current-activity", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertIn("current_application", data)
        self.assertIn("window_title", data)
        self.assertNotEqual(data["current_application"], "Desktop Agent")
        self.assertNotEqual(data["window_title"], "Awaiting Active Telemetry")
        print(f"[TEST 3 PASS] GET /current-activity retrieved real activity: app='{data['current_application']}', title='{data['window_title']}'")

if __name__ == "__main__":
    unittest.main()
