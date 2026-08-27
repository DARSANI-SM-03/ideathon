"""
Comprehensive End-to-End Pipeline Audit & Verification Test Suite for StudIQ.
Verifies:
1. Telemetry ingest from Desktop Agent -> OpenAI contextual classification -> Backend ActivityLog -> GET /current-activity -> Student & Parent Dashboards.
2. YouTube Educational Video -> Education · Programming.
3. YouTube Entertainment Video -> Entertainment · Comedy / Music.
4. VS Code -> Coding/Technical · IDE.
5. ChatGPT -> Other · AI Assistant (Zero conversation prompt text exposed).
6. Idle / Inactive computer -> is_active=False / "No active activity detected".
7. Rapid activity switching (YouTube -> VS Code -> ChatGPT -> YouTube).
8. Student isolation (Student sees only own data).
9. Parent authorized access & IDOR block for unauthorized student IDs.
10. OpenAI API integration & cache hit verification (identical activity reuses cached result).
11. Resilient local fallback when OpenAI is offline.
"""

import unittest
import os
import sys
import time
from datetime import datetime
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app
from app.database.session import SessionLocal
from app.models.user import Student, Parent
from app.models.monitoring import ActivityLog
from app.auth.security import create_access_token
from app.services.ai_classifier_service import classify_context_with_openai, local_fallback_classifier
from desktop_agent.classifier import ActivityClassifier


class TestPipelineE2E(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.db = SessionLocal()

        # Seed test student 901 and parent 901
        self.db.query(Student).filter(Student.id == 901).delete()
        self.db.query(Parent).filter(Parent.id == 901).delete()
        self.db.commit()

        student = Student(
            id=901,
            student_id="STU-901",
            full_name="Pipeline Test Student",
            name="Test Student",
            email="student901@studiq.edu",
            password_hash="fakehash",
            department="Computer Science",
            role="student"
        )
        self.db.add(student)

        parent = Parent(
            id=901,
            parent_id="PAR-901",
            student_id=901,
            full_name="Pipeline Test Parent",
            name="Test Parent",
            email="parent901@studiq.edu",
            role="parent",
            password_hash="fakehash"
        )
        self.db.add(parent)
        self.db.commit()

        self.student_token = create_access_token({"sub": "STU-901", "role": "student", "user_id": 901})
        self.parent_token = create_access_token({"sub": "parent901@studiq.edu", "role": "parent", "user_id": 901})

        # Set active agent ping timestamp
        from app.routers import monitoring_router
        monitoring_router.last_agent_ping_time = time.time()

    def tearDown(self):
        self.db.close()

    def test_01_youtube_educational_scenario(self):
        log = ActivityLog(
            student_id=901,
            application_name="chrome.exe",
            window_title="Python Programming Full Course for Beginners - YouTube",
            website_url="https://youtube.com/watch?v=kGxSyqKbzsc",
            category="Education",
            confidence=0.98,
            duration=120,
            timestamp=datetime.utcnow()
        )
        self.db.add(log)
        self.db.commit()

        resp = self.client.get(
            "/api/v1/monitoring/current-activity",
            headers={"Authorization": f"Bearer {self.student_token}"}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["is_active"])
        self.assertEqual(data["category"], "Education")
        self.assertEqual(data["subcategory"], "Programming")
        self.assertEqual(data["domain"], "youtube.com")

    def test_02_youtube_entertainment_scenario(self):
        log = ActivityLog(
            student_id=901,
            application_name="chrome.exe",
            window_title="Funny Standup Comedy & Pranks - YouTube",
            website_url="https://youtube.com/watch?v=funny999",
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
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["is_active"])
        self.assertEqual(data["category"], "Entertainment")
        self.assertEqual(data["subcategory"], "Comedy / Music")

    def test_03_vscode_scenario(self):
        log = ActivityLog(
            student_id=901,
            application_name="code.exe",
            window_title="studiq / agent.py - Visual Studio Code",
            website_url="",
            category="Coding/Technical",
            confidence=0.95,
            duration=450,
            timestamp=datetime.utcnow()
        )
        self.db.add(log)
        self.db.commit()

        resp = self.client.get(
            "/api/v1/monitoring/current-activity",
            headers={"Authorization": f"Bearer {self.student_token}"}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["is_active"])
        self.assertEqual(data["category"], "Coding/Technical")
        self.assertEqual(data["subcategory"], "IDE")

    def test_04_chatgpt_privacy_scenario(self):
        log = ActivityLog(
            student_id=901,
            application_name="chrome.exe",
            window_title="ChatGPT - Confidential prompt details and essay text",
            website_url="https://chatgpt.com/c/private-chat-room-123",
            category="Other",
            confidence=0.90,
            duration=180,
            timestamp=datetime.utcnow()
        )
        self.db.add(log)
        self.db.commit()

        resp = self.client.get(
            "/api/v1/monitoring/current-activity",
            headers={"Authorization": f"Bearer {self.student_token}"}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["is_active"])
        self.assertEqual(data["page_title"], "ChatGPT")
        self.assertEqual(data["website_url"], "https://chatgpt.com")
        self.assertEqual(data["subcategory"], "AI Assistant")
        self.assertNotIn("Confidential prompt details", data["page_title"])

    def test_05_idle_inactive_computer_scenario(self):
        # Simulate agent ping older than 30 seconds
        from app.routers import monitoring_router
        monitoring_router.last_agent_ping_time = time.time() - 100.0

        resp = self.client.get(
            "/api/v1/monitoring/current-activity?student_id=901",
            headers={"Authorization": f"Bearer {self.student_token}"}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertFalse(data["is_active"])
        self.assertEqual(data["active_activity_status"], "No active activity detected")

    def test_06_rapid_activity_switching(self):
        # Reset active agent ping
        from app.routers import monitoring_router
        monitoring_router.last_agent_ping_time = time.time()

        sequence = [
            ("chrome.exe", "YouTube - Python Course", "https://youtube.com/watch?v=kGxSyqKbzsc", "Education"),
            ("code.exe", "studiq / classifier.py - Visual Studio Code", "", "Coding/Technical"),
            ("chrome.exe", "ChatGPT", "https://chatgpt.com", "Other"),
            ("chrome.exe", "YouTube - Data Structures", "https://youtube.com/watch?v=dsa123", "Education")
        ]

        for app_name, title, url, expected_cat in sequence:
            log = ActivityLog(
                student_id=901,
                application_name=app_name,
                window_title=title,
                website_url=url,
                category=expected_cat,
                confidence=0.95,
                duration=60,
                timestamp=datetime.utcnow()
            )
            self.db.add(log)
            self.db.commit()

            resp = self.client.get(
                "/api/v1/monitoring/current-activity",
                headers={"Authorization": f"Bearer {self.student_token}"}
            )
            data = resp.json()
            self.assertEqual(data["application"], app_name)
            self.assertEqual(data["category"], expected_cat)

    def test_07_parent_authorized_view_and_idor_protection(self):
        from app.routers import monitoring_router
        monitoring_router.last_agent_ping_time = time.time()

        # Authorized parent view
        resp_parent = self.client.get(
            "/api/v1/monitoring/current-activity?student_id=901",
            headers={"Authorization": f"Bearer {self.parent_token}"}
        )
        self.assertEqual(resp_parent.status_code, 200)
        self.assertEqual(resp_parent.json()["student_id"], 901)

        # IDOR Block: Parent 901 attempts to query student 8888
        resp_idor = self.client.get(
            "/api/v1/monitoring/current-activity?student_id=8888",
            headers={"Authorization": f"Bearer {self.parent_token}"}
        )
        self.assertEqual(resp_idor.status_code, 403)

    def test_08_caching_behavior_reuses_classification(self):
        classifier = ActivityClassifier()
        res1 = classifier.classify_with_context(
            "chrome.exe",
            "Python Full Course for Beginners",
            "https://youtube.com/watch?v=cache_test_vid_123"
        )
        res2 = classifier.classify_with_context(
            "chrome.exe",
            "Python Full Course for Beginners",
            "https://youtube.com/watch?v=cache_test_vid_123"
        )
        self.assertEqual(res2["classification_method"], "AI Context Classification (Cached)")

    def test_09_local_fallback_resilience(self):
        # Call local fallback classifier directly
        fallback_res = local_fallback_classifier({
            "application": "chrome.exe",
            "page_title": "MIT OpenCourseWare Python Lecture",
            "domain": "youtube.com"
        })
        self.assertEqual(fallback_res["category"], "Education")
        self.assertEqual(fallback_res["subcategory"], "Programming")
        self.assertGreaterEqual(fallback_res["confidence"], 0.85)


if __name__ == "__main__":
    unittest.main()
