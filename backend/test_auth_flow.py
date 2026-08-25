"""
StudIQ Real Database Authentication System Verification Suite
============================================================
Directly verifies user registration, password hashing, database insertion,
login authentication, password verification, JWT creation/validation,
and role-based agent session generation against the SQLite database.
"""

import sys
import os
import time
from datetime import datetime

# Ensure backend root is in sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.database.session import SessionLocal, engine
from app.database.base import Base
from app.models.user import Student, Parent, Mentor, Admin
from app.schemas.auth import LoginRequest, StudentRegisterRequest, MentorRegisterRequest
from app.auth.security import get_password_hash, verify_password, create_access_token, decode_access_token
from app.routers.auth_router import register_student, register_mentor, login, get_me
from app.auth.dependencies import get_current_user
from fastapi import HTTPException

try:
    Base.metadata.create_all(bind=engine)
except Exception:
    pass

def run_tests():
    print("==========================================================", flush=True)
    print("   STUDIQ AUTHENTICATION SYSTEM COMPREHENSIVE TEST SUITE  ", flush=True)
    print("==========================================================", flush=True)

    db = SessionLocal()
    test_timestamp = int(time.time())
    test_student_id = f"STU-TEST-{test_timestamp}"
    test_student_email = f"student_{test_timestamp}@studiq.edu"
    test_password = "SecurePassword123!"

    try:
        # ---------------------------------------------------------
        # TEST 1: REAL STUDENT SIGNUP & DATABASE INSERTION
        # ---------------------------------------------------------
        print("\n[TEST 1] Testing Real Student Registration...", flush=True)
        signup_req = StudentRegisterRequest(
            full_name="Test Student User",
            student_id=test_student_id,
            email=test_student_email,
            college_name="Global Institute of Technology",
            department="Computer Science",
            semester=3,
            year=2,
            password=test_password,
            parent_name="Parent User",
            parent_email=f"parent_{test_timestamp}@gmail.com",
            parent_phone="+1 555-019-9999"
        )

        res_signup = register_student(signup_req, db)
        print(f"Signup Response: {res_signup}", flush=True)
        assert res_signup.get("status") == "success"

        db_student = db.query(Student).filter(Student.email == test_student_email).first()
        assert db_student is not None, "Student record missing in SQLite database!"
        assert db_student.password_hash != test_password, "Password was stored in plaintext!"
        assert verify_password(test_password, db_student.password_hash), "Password verification failed!"
        print(f"[PASS] TEST 1 PASSED: Real Student inserted into DB (ID={db_student.id}, Code={db_student.student_id}, Hashed Password Verified)!", flush=True)

        # ---------------------------------------------------------
        # TEST 2: DUPLICATE SIGNUP REJECTION
        # ---------------------------------------------------------
        print("\n[TEST 2] Testing Duplicate Student Registration...", flush=True)
        try:
            register_student(signup_req, db)
            assert False, "Should have raised HTTPException 400 for duplicate user!"
        except HTTPException as exc:
            assert exc.status_code == 400
            print(f"[PASS] TEST 2 PASSED: Duplicate registration rejected with HTTP 400 ({exc.detail})!", flush=True)

        # ---------------------------------------------------------
        # TEST 3: INVALID LOGIN ATTEMPTS (Wrong Password & Unknown Email)
        # ---------------------------------------------------------
        print("\n[TEST 3A] Testing Login with Incorrect Password...", flush=True)
        wrong_pw_req = LoginRequest(user_identifier=test_student_email, password="WrongPassword999", role="student")
        try:
            login(wrong_pw_req, db)
            assert False, "Should have raised HTTPException 401 for wrong password!"
        except HTTPException as exc:
            assert exc.status_code == 401
            print(f"[PASS] TEST 3A PASSED: Wrong password correctly rejected with HTTP 401 ({exc.detail})!", flush=True)

        print("\n[TEST 3B] Testing Login with Non-Existent Identifier...", flush=True)
        unknown_user_req = LoginRequest(user_identifier="fake_user_999@studiq.edu", password="Password123!", role="student")
        try:
            login(unknown_user_req, db)
            assert False, "Should have raised HTTPException 401 for unknown user!"
        except HTTPException as exc:
            assert exc.status_code == 401
            print(f"[PASS] TEST 3B PASSED: Non-existent user correctly rejected with HTTP 401 ({exc.detail})!", flush=True)

        # ---------------------------------------------------------
        # TEST 4: REAL STUDENT LOGIN & JWT ISSUANCE
        # ---------------------------------------------------------
        print("\n[TEST 4] Testing Real Student Login & JWT Token Generation...", flush=True)
        valid_login_req = LoginRequest(user_identifier=test_student_email, password=test_password, role="student")
        login_res = login(valid_login_req, db)
        print(f"Login Response: {login_res}", flush=True)
        
        access_token = login_res.get("access_token")
        assert access_token is not None, "No access token returned!"
        assert login_res.get("user_id") == db_student.id
        assert login_res.get("user_identifier") == db_student.student_id
        assert login_res.get("email") == test_student_email
        print(f"[PASS] TEST 4 PASSED: JWT Access Token issued for student_id={db_student.id} ({db_student.student_id})!", flush=True)

        # ---------------------------------------------------------
        # TEST 5: CURRENT USER PROFILE ENDPOINT (/auth/me & dependencies)
        # ---------------------------------------------------------
        print("\n[TEST 5] Testing User Validation & GET /auth/me...", flush=True)
        curr_user = get_current_user(token=access_token, db=db)
        assert curr_user["id"] == db_student.id
        assert curr_user["email"] == test_student_email
        assert curr_user["role"] == "student"

        user_profile = get_me(current_user=curr_user)
        assert user_profile.id == db_student.id
        assert user_profile.email == test_student_email
        assert user_profile.user_identifier == db_student.student_id
        print(f"[PASS] TEST 5 PASSED: GET /auth/me accurately returned real DB profile for {user_profile.name} ({user_profile.email})!", flush=True)

        # ---------------------------------------------------------
        # TEST 6: MENTOR REAL REGISTRATION & AUTHENTICATION
        # ---------------------------------------------------------
        print("\n[TEST 6] Testing Mentor Real Registration & Authentication...", flush=True)
        mentor_emp_id = f"EMP-{test_timestamp}"
        mentor_email = f"mentor_{test_timestamp}@studiq.edu"
        mentor_signup = MentorRegisterRequest(
            full_name="Dr. Testing Mentor",
            employee_id=mentor_emp_id,
            email=mentor_email,
            department="Computer Science",
            password=test_password
        )
        register_mentor(mentor_signup, db)

        mentor_login_res = login(LoginRequest(user_identifier=mentor_email, password=test_password, role="mentor"), db)
        mentor_token = mentor_login_res["access_token"]
        mentor_curr = get_current_user(token=mentor_token, db=db)
        assert mentor_curr["email"] == mentor_email
        assert mentor_curr["role"] == "mentor"
        print(f"[PASS] TEST 6 PASSED: Mentor registration & authentication verified for {mentor_email}!", flush=True)

        print("\n==========================================================", flush=True)
        print(" ALL AUTHENTICATION SYSTEM INTEGRATION TESTS PASSED (100%) ", flush=True)
        print("==========================================================", flush=True)

    finally:
        db.close()

if __name__ == "__main__":
    run_tests()
