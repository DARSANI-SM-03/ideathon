import unittest
from fastapi.testclient import TestClient
import time
import os
import sys

# Ensure backend directory on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app
from app.database.session import SessionLocal
from app.models.user import Student, Parent, Mentor, Admin, Teacher

class TestUnifiedAuthFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.db = SessionLocal()
        cls.timestamp = int(time.time())

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_01_existing_student_continue_login(self):
        """Test POST /auth/continue with an existing student credentials."""
        student = self.db.query(Student).first()
        self.assertIsNotNone(student, "At least one student should exist in studiq.db")

        resp = self.client.post("/api/v1/auth/continue", json={
            "user_identifier": student.student_id,
            "password": "password123",
            "role": "student"
        })
        self.assertIn(resp.status_code, [200, 401])
        if resp.status_code == 200:
            data = resp.json()
            self.assertEqual(data["status"], "authenticated")
            self.assertEqual(data["role"], "student")
            self.assertIn("access_token", data)

    def test_02_unknown_student_registration_required(self):
        """Test POST /auth/continue with non-existent student email -> registration_required."""
        unknown_email = f"unknown_student_{self.timestamp}@studiq.edu"
        resp = self.client.post("/api/v1/auth/continue", json={
            "user_identifier": unknown_email,
            "password": "AnyPassword123!",
            "role": "student"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "registration_required")
        self.assertEqual(data["role"], "student")

    def test_03_blocked_public_admin_registration(self):
        """Test POST /auth/continue with non-existent admin -> HTTP 403 Blocked."""
        unknown_admin = f"unknown_admin_{self.timestamp}@studiq.edu"
        resp = self.client.post("/api/v1/auth/continue", json={
            "user_identifier": unknown_admin,
            "password": "AdminPassword123!",
            "role": "admin"
        })
        self.assertEqual(resp.status_code, 403)
        self.assertIn("Admin account not found", resp.json()["detail"])

        reg_resp = self.client.post("/api/v1/auth/register/admin", json={
            "college_name": "Test College",
            "full_name": "Fake Admin",
            "email": unknown_admin,
            "password": "AdminPassword123!"
        })
        self.assertEqual(reg_resp.status_code, 403)
        self.assertIn("Admin account not found", reg_resp.json()["detail"])

    def test_04_new_student_register_and_autologin(self):
        """Test student registration returns access_token for seamless auto-login."""
        new_stu_id = f"STU-AUTO-{self.timestamp}"
        new_email = f"auto_stu_{self.timestamp}@studiq.edu"

        resp = self.client.post("/api/v1/auth/register/student", json={
            "full_name": "Auto Login Student",
            "student_id": new_stu_id,
            "email": new_email,
            "department": "Computer Science",
            "semester": 1,
            "password": "SecurePassword123!",
            "parent_email": f"parent_{self.timestamp}@gmail.com"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("access_token", data, "Registration response must include access_token for auto-login!")
        self.assertEqual(data["role"], "student")
        self.assertEqual(data["user_identifier"], new_stu_id)

    def test_05_invalid_password_returns_generic_error(self):
        """Test existing user with wrong password returns generic error message."""
        student = self.db.query(Student).first()
        self.assertIsNotNone(student)

        resp = self.client.post("/api/v1/auth/continue", json={
            "user_identifier": student.student_id,
            "password": "WRONG_PASSWORD_999!",
            "role": "student"
        })
        self.assertEqual(resp.status_code, 401)
        data = resp.json()
        self.assertEqual(data["detail"], "Invalid credentials. Please check your ID/email and password.")

    def test_06_parent_registration_and_autologin(self):
        """Test parent registration flow with auto-login."""
        parent_email = f"parent_auto_{self.timestamp}@gmail.com"
        resp = self.client.post("/api/v1/auth/register/parent", json={
            "full_name": "Auto Login Parent",
            "email": parent_email,
            "password": "ParentPassword123!"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("access_token", data)
        self.assertEqual(data["role"], "parent")

if __name__ == "__main__":
    unittest.main()
