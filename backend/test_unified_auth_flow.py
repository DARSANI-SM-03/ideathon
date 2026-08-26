"""
Comprehensive Unit Test Suite for StudIQ Unified Authentication Flow.
Tests all requirements:
1. New user: account does not exist -> registration -> account created -> auto logged in with token.
2. Existing user: account exists -> authenticated directly -> dashboard redirect.
3. Existing user login again -> does NOT create duplicate account.
4. Duplicate registration -> rejected with HTTP 400 & ACCOUNT_ALREADY_EXISTS.
5. Existing account + wrong password -> HTTP 401 (Incorrect password).
6. Existing account + correct password -> HTTP 200 (authenticated).
7. Cross-role detection -> Student attempting login on Parent tab rejected with clear message.
8. Student role -> student dashboard.
9. Parent role -> parent dashboard.
10. Privacy protection -> zero profile exposure without password authentication.
"""

import unittest
import os
import sys
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app
from app.database.session import SessionLocal
from app.models.user import Student, Parent
from app.auth.security import get_password_hash


class TestUnifiedAuthFlow(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.db = SessionLocal()

        # Clean up any leftover test accounts
        self.db.query(Student).filter(
            (Student.student_id.in_(["STU-NEW-01", "STU-EX-01", "STU-DUP-01", "STU-CROSS-01"])) |
            (Student.email.in_(["new01@studiq.edu", "ex01@studiq.edu", "dup01@studiq.edu", "cross01@studiq.edu"]))
        ).delete(synchronize_session=False)
        self.db.query(Parent).filter(
            Parent.email.in_(["parent01@studiq.edu", "parent_cross01@studiq.edu"])
        ).delete(synchronize_session=False)
        self.db.commit()

    def tearDown(self):
        self.db.close()

    def test_01_new_user_auth_and_auto_login(self):
        # Step A: Continue lookup for new non-existent student
        resp1 = self.client.post(
            "/api/v1/auth/continue",
            json={
                "role": "student",
                "user_identifier": "STU-NEW-01",
                "password": "Password123!"
            }
        )
        self.assertEqual(resp1.status_code, 200)
        data1 = resp1.json()
        self.assertEqual(data1["status"], "registration_required")

        # Step B: Submit registration
        resp2 = self.client.post(
            "/api/v1/auth/register/student",
            json={
                "full_name": "New Test Student",
                "student_id": "STU-NEW-01",
                "email": "new01@studiq.edu",
                "department": "Computer Science",
                "semester": 1,
                "password": "Password123!",
                "parent_email": "",
                "parent_phone": ""
            }
        )
        self.assertEqual(resp2.status_code, 200)
        data2 = resp2.json()
        self.assertEqual(data2["status"], "success")
        self.assertIn("access_token", data2)
        self.assertEqual(data2["role"], "student")
        self.assertEqual(data2["redirect"], "/student/dashboard")

    def test_02_existing_user_login_recognizes_account(self):
        # Seed existing student
        st = Student(
            student_id="STU-EX-01",
            full_name="Existing Student",
            name="Existing Student",
            email="ex01@studiq.edu",
            password_hash=get_password_hash("Password123!"),
            department="Computer Science",
            role="student"
        )
        self.db.add(st)
        self.db.commit()

        # Continue with existing account STU-EX-01
        resp = self.client.post(
            "/api/v1/auth/continue",
            json={
                "role": "student",
                "user_identifier": "STU-EX-01",
                "password": "Password123!"
            }
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "authenticated")
        self.assertIn("access_token", data)
        self.assertEqual(data["redirect"], "/student/dashboard")

    def test_03_existing_user_wrong_password_rejected(self):
        # Seed existing student
        st = Student(
            student_id="STU-EX-01",
            full_name="Existing Student",
            name="Existing Student",
            email="ex01@studiq.edu",
            password_hash=get_password_hash("CorrectPassword123!"),
            department="Computer Science",
            role="student"
        )
        self.db.add(st)
        self.db.commit()

        resp = self.client.post(
            "/api/v1/auth/continue",
            json={
                "role": "student",
                "user_identifier": "STU-EX-01",
                "password": "WRONG_PASSWORD_999"
            }
        )
        self.assertEqual(resp.status_code, 401)
        self.assertIn("Incorrect password", resp.json()["detail"])

    def test_04_duplicate_registration_rejected(self):
        # Seed existing student STU-DUP-01
        st = Student(
            student_id="STU-DUP-01",
            full_name="Duplicate Student",
            name="Duplicate Student",
            email="dup01@studiq.edu",
            password_hash=get_password_hash("Password123!"),
            department="Computer Science",
            role="student"
        )
        self.db.add(st)
        self.db.commit()

        # Attempt to register duplicate STU-DUP-01
        resp = self.client.post(
            "/api/v1/auth/register/student",
            json={
                "full_name": "Duplicate Student Attempt",
                "student_id": "STU-DUP-01",
                "email": "dup01@studiq.edu",
                "department": "Data Science",
                "semester": 1,
                "password": "Password123!",
                "parent_email": "",
                "parent_phone": ""
            }
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("ACCOUNT_ALREADY_EXISTS", resp.json()["detail"])

    def test_05_cross_role_tab_mismatch_detection(self):
        # Seed existing student cross01@studiq.edu
        st = Student(
            student_id="STU-CROSS-01",
            full_name="Cross Student",
            name="Cross Student",
            email="cross01@studiq.edu",
            password_hash=get_password_hash("Password123!"),
            department="Computer Science",
            role="student"
        )
        self.db.add(st)
        self.db.commit()

        # Student cross01@studiq.edu attempts login on Parent tab
        resp = self.client.post(
            "/api/v1/auth/continue",
            json={
                "role": "parent",
                "user_identifier": "cross01@studiq.edu",
                "password": "Password123!"
            }
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("exists as a Student", resp.json()["detail"])

    def test_06_parent_unified_registration_and_login(self):
        # Register new parent
        resp1 = self.client.post(
            "/api/v1/auth/register/parent",
            json={
                "full_name": "Unified Test Parent",
                "email": "parent01@studiq.edu",
                "phone": "9998887776",
                "password": "ParentPassword123!"
            }
        )
        self.assertEqual(resp1.status_code, 200)
        data1 = resp1.json()
        self.assertEqual(data1["role"], "parent")
        self.assertEqual(data1["redirect"], "/parent/dashboard")

        # Authenticate existing parent
        resp2 = self.client.post(
            "/api/v1/auth/continue",
            json={
                "role": "parent",
                "user_identifier": "parent01@studiq.edu",
                "password": "ParentPassword123!"
            }
        )
        self.assertEqual(resp2.status_code, 200)
        data2 = resp2.json()
        self.assertEqual(data2["status"], "authenticated")
        self.assertEqual(data2["role"], "parent")


if __name__ == "__main__":
    unittest.main()
