"""
Unit & Integration Test Suite for Currently Active Activity API & Parent IDOR Isolation.
Tests:
1. Student sees own current activity.
2. Parent sees authorized student's current activity.
3. Parent IDOR protection: Parent cannot query another student's activity (HTTP 403).
4. YouTube educational activity displays Education / Programming.
5. YouTube entertainment activity displays Entertainment / Comedy.
6. VS Code displays Coding/Technical.
7. ChatGPT displays safe metadata only (no conversation text).
8. Idle student displays is_active: False / "No active activity detected".
"""

import unittest
import os
import sys
import time
from datetime import datetime
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app
from app.database.session import get_db, SessionLocal
from app.models.user import Student, Parent
from app.models.monitoring import ActivityLog
from app.auth.security import create_access_token


class TestCurrentActivityEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.db = SessionLocal()

        # Seed test student 801 and parent 801
        existing_student = self.db.query(Student).filter(Student.id == 801).first()
        if not existing_student:
            student = Student(
                id=801,
                student_id="STU-801",
                full_name="Current Activity Test Student",
                name="Test Student",
                email="student801@studiq.edu",
                password_hash="fakehash",
                department="Computer Science",
                role="student"
            )
            self.db.add(student)

        existing_parent = self.db.query(Parent).filter(Parent.id == 801).first()
        if not existing_parent:
            parent = Parent(
                id=801,
                parent_id="PAR-801",
                student_id=801,
                full_name="Current Activity Test Parent",
                name="Test Parent",
                email="parent801@studiq.edu",
                role="parent",
                password_hash="fakehash"
            )
            self.db.add(parent)

        self.db.commit()

        self.student_token = create_access_token({"sub": "STU-801", "role": "student", "user_id": 801})
        self.parent_token = create_access_token({"sub": "parent801@studiq.edu", "role": "parent", "user_id": 801})

    def tearDown(self):
        self.db.close()

    def test_01_student_sees_own_current_activity(self):
        # Insert recent telemetry log for student 801
        log = ActivityLog(
            student_id=801,
            application_name="chrome.exe",
            window_title="Python Full Course for Beginners - YouTube",
            website_url="https://youtube.com/watch?v=kGxSyqKbzsc",
            category="Education",
            confidence=0.98,
            duration=120,
            timestamp=datetime.utcnow()
        )
        self.db.add(log)
        self.db.commit()

        # Simulate recent agent ping
        from app.routers import monitoring_router
        monitoring_router.last_agent_ping_time = time.time()

        resp = self.client.get(
            "/api/v1/monitoring/current-activity",
            headers={"Authorization": f"Bearer {self.student_token}"}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["is_active"])
        self.assertEqual(data["category"], "Education")
        self.assertEqual(data["subcategory"], "Programming")
        self.assertEqual(data["confidence_percent"], "98%")

    def test_02_parent_sees_authorized_student_current_activity(self):
        resp = self.client.get(
            "/api/v1/monitoring/current-activity?student_id=801",
            headers={"Authorization": f"Bearer {self.parent_token}"}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["student_id"], 801)

    def test_03_parent_idor_protection_blocks_unauthorized_student(self):
        # Parent 801 attempts to query student 9999 (unauthorized)
        resp = self.client.get(
            "/api/v1/monitoring/current-activity?student_id=9999",
            headers={"Authorization": f"Bearer {self.parent_token}"}
        )
        self.assertEqual(resp.status_code, 403)
        self.assertIn("Forbidden", resp.json()["detail"])

    def test_04_youtube_educational_display(self):
        log = ActivityLog(
            student_id=801,
            application_name="chrome.exe",
            window_title="Data Structures and Algorithms Tutorial",
            website_url="https://youtube.com/watch?v=dsa123",
            category="Education",
            confidence=0.97,
            duration=180,
            timestamp=datetime.utcnow()
        )
        self.db.add(log)
        self.db.commit()

        resp = self.client.get(
            "/api/v1/monitoring/current-activity",
            headers={"Authorization": f"Bearer {self.student_token}"}
        )
        data = resp.json()
        self.assertEqual(data["category"], "Education")
        self.assertEqual(data["subcategory"], "Programming")

    def test_05_youtube_entertainment_display(self):
        log = ActivityLog(
            student_id=801,
            application_name="chrome.exe",
            window_title="Funny Memes & Pranks Compilation",
            website_url="https://youtube.com/watch?v=funny123",
            category="Entertainment",
            confidence=0.94,
            duration=300,
            timestamp=datetime.utcnow()
        )
        self.db.add(log)
        self.db.commit()

        resp = self.client.get(
            "/api/v1/monitoring/current-activity",
            headers={"Authorization": f"Bearer {self.student_token}"}
        )
        data = resp.json()
        self.assertEqual(data["category"], "Entertainment")
        self.assertEqual(data["subcategory"], "Comedy / Music")

    def test_06_vscode_display(self):
        log = ActivityLog(
            student_id=801,
            application_name="code.exe",
            window_title="studiq / agent.py - Visual Studio Code",
            website_url="",
            category="Coding/Technical",
            confidence=0.95,
            duration=600,
            timestamp=datetime.utcnow()
        )
        self.db.add(log)
        self.db.commit()

        resp = self.client.get(
            "/api/v1/monitoring/current-activity",
            headers={"Authorization": f"Bearer {self.student_token}"}
        )
        data = resp.json()
        self.assertEqual(data["category"], "Coding/Technical")
        self.assertEqual(data["subcategory"], "IDE")

    def test_07_chatgpt_privacy_safe_metadata_only(self):
        log = ActivityLog(
            student_id=801,
            application_name="chrome.exe",
            window_title="ChatGPT - Write my essay code prompt query",
            website_url="https://chatgpt.com/c/123-abc-private-convo",
            category="Other",
            confidence=0.85,
            duration=120,
            timestamp=datetime.utcnow()
        )
        self.db.add(log)
        self.db.commit()

        resp = self.client.get(
            "/api/v1/monitoring/current-activity",
            headers={"Authorization": f"Bearer {self.student_token}"}
        )
        data = resp.json()
        self.assertEqual(data["page_title"], "ChatGPT")
        self.assertEqual(data["website_url"], "https://chatgpt.com")
        self.assertNotIn("Write my essay code prompt query", data["page_title"])

    def test_08_idle_student_display(self):
        # Simulate offline agent ping and old log (older than 60 seconds)
        from app.routers import monitoring_router
        monitoring_router.last_agent_ping_time = 0.0

        resp = self.client.get(
            "/api/v1/monitoring/current-activity?student_id=801",
            headers={"Authorization": f"Bearer {self.student_token}"}
        )
        data = resp.json()
        self.assertFalse(data["is_active"])
        self.assertEqual(data["active_activity_status"], "No active activity detected")


if __name__ == "__main__":
    unittest.main()
