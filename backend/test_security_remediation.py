import unittest
from fastapi.testclient import TestClient
import time
import os
import sys
import json
import shutil

# Ensure backend and desktop_agent directories are on sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)
sys.path.insert(0, os.path.join(backend_dir, "desktop_agent"))

from app.main import app
from app.database.session import SessionLocal
from app.models.user import Student
from app.auth.security import create_agent_token
from desktop_agent.collector import SystemActivityCollector
from desktop_agent.sender import TelemetrySender

class TestSecurityRemediation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.db = SessionLocal()
        cls.timestamp = int(time.time())

        # Create or fetch a test student
        cls.student = cls.db.query(Student).first()
        if not cls.student:
            cls.student = Student(
                student_id=f"STU-SEC-{cls.timestamp}",
                full_name="Security Test Student",
                name="Security Test Student",
                email=f"sec_test_{cls.timestamp}@studiq.edu",
                password_hash="hashed_pass"
            )
            cls.db.add(cls.student)
            cls.db.commit()
            cls.db.refresh(cls.student)

        cls.student_id = cls.student.id
        cls.student_code = cls.student.student_id
        cls.agent_token = create_agent_token({
            "student_id": cls.student_id,
            "student_code": cls.student_code,
            "scope": "telemetry"
        })

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_01_unauthenticated_telemetry_rejected_401(self):
        """P0-1: Confirm unauthenticated telemetry without token is rejected with HTTP 401."""
        resp = self.client.post("/api/v1/monitoring/telemetry", json={
            "student_id": self.student_id,
            "application_name": "chrome.exe",
            "duration_seconds": 5
        })
        self.assertEqual(resp.status_code, 401)
        self.assertIn("Valid agent session token required", resp.json()["detail"])

    def test_02_idor_student_mismatch_rejected_403(self):
        """P0-2: Confirm student A token with student B payload ID is rejected with HTTP 403."""
        fake_other_student_id = self.student_id + 9999
        resp = self.client.post("/api/v1/monitoring/telemetry", json={
            "agent_token": self.agent_token,
            "student_id": fake_other_student_id,
            "application_name": "code.exe",
            "duration_seconds": 5
        })
        self.assertEqual(resp.status_code, 403)
        self.assertIn("student ID mismatch", resp.json()["detail"])

    def test_03_authenticated_telemetry_accepted_200(self):
        """P0-1 & P0-2: Confirm valid authenticated telemetry with matching token is accepted."""
        resp = self.client.post("/api/v1/monitoring/telemetry", json={
            "agent_token": self.agent_token,
            "student_id": self.student_id,
            "application_name": "code.exe",
            "window_title": "Active IDE / Coding Work",
            "duration_seconds": 5
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "success")

    def test_04_privacy_by_design_window_title_anonymization(self):
        """P1-1: Confirm raw window titles containing sensitive PII are anonymized locally."""
        collector = SystemActivityCollector()
        
        # Test sensitive Chrome web title containing email and banking info
        raw_title = "Chase Online Banking - Account Balance ($5,000) - john.doe@gmail.com - Google Chrome"
        anon_title, website_url = collector.sanitize_and_abstract_window_title("chrome.exe", raw_title)
        
        self.assertNotIn("john.doe@gmail.com", anon_title)
        self.assertNotIn("$5,000", anon_title)
        self.assertEqual(anon_title, "Active Web Session")

        # Test youtube domain extraction
        raw_yt = "Python Tutorial for Beginners - YouTube - Google Chrome"
        anon_yt, url_yt = collector.sanitize_and_abstract_window_title("chrome.exe", raw_yt)
        self.assertEqual(url_yt, "youtube.com")
        self.assertEqual(anon_yt, "Web Activity (youtube.com)")

    def test_05_durable_disk_queue_persistence(self):
        """P1-2: Confirm offline telemetry queue persists to disk and recovers cleanly."""
        # Clean queue file for test before sender creation
        dummy_sender = TelemetrySender(backend_url="http://127.0.0.1:9999/fake-offline-url")
        queue_path = dummy_sender.queue_file
        if os.path.exists(queue_path):
            try:
                os.remove(queue_path)
            except Exception:
                pass

        sender = TelemetrySender(backend_url="http://127.0.0.1:9999/fake-offline-url")
        test_payload = {
            "application_name": "offline_test.exe",
            "duration_seconds": 5,
            "timestamp": "2026-08-26T00:00:00Z"
        }
        sender.queue_offline_payload(test_payload)

        self.assertTrue(os.path.exists(queue_path), "Offline queue file must exist on disk!")
        
        # Create a new sender instance (simulating agent restart)
        sender2 = TelemetrySender(backend_url="http://127.0.0.1:9999/fake-offline-url")
        self.assertEqual(len(sender2.offline_queue), 1)
        self.assertEqual(sender2.offline_queue[0]["application_name"], "offline_test.exe")

    def test_06_fail_fast_production_secret_key(self):
        """P0-4: Confirm production startup fails fast if SECRET_KEY is missing."""
        from app.config import Settings
        os.environ["STUDIQ_ENV"] = "production"
        if "SECRET_KEY" in os.environ:
            del os.environ["SECRET_KEY"]

        with self.assertRaises(RuntimeError):
            _ = Settings()

        # Reset back to development mode for clean test state
        os.environ["STUDIQ_ENV"] = "development"

if __name__ == "__main__":
    unittest.main()
