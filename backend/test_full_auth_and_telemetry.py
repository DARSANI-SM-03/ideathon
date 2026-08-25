from fastapi.testclient import TestClient
from app.main import app
import json
import time
import sqlite3
import os

client = TestClient(app)
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "studiq.db")

def log_test(msg: str):
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] [E2E Test] {msg}")

def http_post(endpoint: str, data: dict, headers: dict = None) -> tuple[int, dict]:
    url = f"/api/v1{endpoint}" if not endpoint.startswith("/api/v1") else endpoint
    response = client.post(url, json=data, headers=headers)
    try:
        return response.status_code, response.json()
    except Exception:
        return response.status_code, {"raw": response.text}

def http_get(endpoint: str, headers: dict = None) -> tuple[int, dict]:
    url = f"/api/v1{endpoint}" if not endpoint.startswith("/api/v1") else endpoint
    response = client.get(url, headers=headers)
    try:
        return response.status_code, response.json()
    except Exception:
        return response.status_code, {"raw": response.text}

def run_tests():
    log_test("==========================================================")
    log_test("   RUNNING STUDIQ AUTH & TELEMETRY ACCEPTANCE TEST SUITE  ")
    log_test("==========================================================")

    test_ts = int(time.time())
    test_student_id = f"STU-E2E-{test_ts}"
    test_email = f"student.e2e.{test_ts}@studiq.edu"
    test_password = "SecurePassword123!"

    # 1. Fresh Registration
    log_test(f"Test 1: Registering new student ({test_student_id})...")
    status, body = http_post("/auth/register/student", {
        "student_id": test_student_id,
        "full_name": "E2E Test Student",
        "email": test_email,
        "college_name": "Global Institute of Technology",
        "department": "Computer Science",
        "semester": 6,
        "year": 3,
        "password": test_password,
        "parent_email": f"parent.{test_ts}@gmail.com",
        "parent_phone": "+1-555-0199"
    })
    log_test(f"  Register Response ({status}): {body}")
    assert status == 200, f"Registration failed with status {status}"
    assert body.get("status") == "success", "Registration did not return success status"
    log_test("  [OK] Fresh Student Registration PASSED")

    # 2. Duplicate Registration Check
    log_test("Test 2: Testing duplicate registration prevention...")
    status_dup, body_dup = http_post("/auth/register/student", {
        "student_id": test_student_id,
        "full_name": "Duplicate Student",
        "email": test_email,
        "college_name": "Global Institute of Technology",
        "department": "Computer Science",
        "semester": 6,
        "year": 3,
        "password": test_password,
        "parent_email": f"parent.{test_ts}@gmail.com"
    })
    log_test(f"  Duplicate Response ({status_dup}): {body_dup}")
    assert status_dup == 400, f"Duplicate check failed: expected 400 got {status_dup}"
    assert "already registered" in body_dup.get("detail", "").lower(), "Expected clean friendly duplicate message"
    log_test("  [OK] Duplicate Registration Prevention PASSED")

    # 3. Invalid Credentials Login Check
    log_test("Test 3: Testing invalid password login rejection...")
    status_bad, body_bad = http_post("/auth/login", {
        "user_identifier": test_student_id,
        "password": "WrongPassword999",
        "role": "student"
    })
    log_test(f"  Invalid Login Response ({status_bad}): {body_bad}")
    assert status_bad == 401, f"Expected 401 for bad password, got {status_bad}"
    log_test("  [OK] Invalid Password Handling PASSED")

    # 4. Successful Student Login
    log_test("Test 4: Logging in with valid student credentials...")
    status_login, body_login = http_post("/auth/login", {
        "user_identifier": test_student_id,
        "password": test_password,
        "role": "student"
    })
    log_test(f"  Login Response ({status_login}): {body_login}")
    assert status_login == 200, f"Login failed with status {status_login}"
    access_token = body_login.get("access_token")
    student_pk = body_login.get("user_id")
    assert access_token is not None, "Missing access token in login response"
    assert student_pk is not None, "Missing user_id in login response"
    log_test(f"  [OK] Login Successful! Assigned Database Primary Key: {student_pk} PASSED")

    # 5. Session Verification (/auth/me)
    log_test("Test 5: Verifying JWT session via GET /auth/me...")
    status_me, body_me = http_get("/auth/me", headers={"Authorization": f"Bearer {access_token}"})
    log_test(f"  /auth/me Response ({status_me}): {body_me}")
    assert status_me == 200, f"/auth/me failed with status {status_me}"
    assert body_me.get("email") == test_email, "Email mismatch in /auth/me response"
    log_test("  [OK] /auth/me Session Restoration PASSED")

    # 6. Forgot Password & Reset Flow
    log_test("Test 6: Testing Forgot Password & Reset Flow...")
    status_fp, body_fp = http_post("/auth/forgot-password", {"email": test_email})
    assert status_fp == 200, f"Forgot password failed with status {status_fp}"
    reset_token = body_fp.get("reset_token")
    assert reset_token is not None, "Reset token not generated"

    new_pw = "NewPassword456!"
    status_rp, body_rp = http_post("/auth/reset-password", {
        "reset_token": reset_token,
        "new_password": new_pw
    })
    assert status_rp == 200, f"Reset password failed with status {status_rp}"

    # Verify login with new password
    status_relogin, body_relogin = http_post("/auth/login", {
        "user_identifier": test_student_id,
        "password": new_pw,
        "role": "student"
    })
    assert status_relogin == 200, "Login with updated password failed"
    access_token = body_relogin.get("access_token")
    log_test("  [OK] Forgot & Reset Password Flow PASSED")

    # 7. Agent Session Token Generation
    log_test("Test 7: Generating scoped agent session token...")
    status_agent_sess, body_agent_sess = http_post("/monitoring/agent/session", {}, headers={"Authorization": f"Bearer {access_token}"})
    log_test(f"  Agent Session Response ({status_agent_sess}): {body_agent_sess}")
    assert status_agent_sess == 200, "Failed to generate agent session"
    agent_token = body_agent_sess.get("agent_token")
    assert agent_token is not None, "Missing agent token"
    log_test("  [OK] Scoped Agent Session Generation PASSED")

    # 8. Telemetry Ingestion with Agent Token
    log_test("Test 8: Sending telemetry payload with agent_token...")
    status_telem, body_telem = http_post("/monitoring/telemetry", {
        "agent_token": agent_token,
        "student_id": 99999,  # Intentionally send wrong ID in body to verify server resolves real ID from JWT!
        "application_name": "VS Code",
        "window_title": "test_full_auth_and_telemetry.py - StudIQ",
        "website_url": "https://studiq.edu",
        "category": "Educational",
        "confidence": 0.98,
        "duration_seconds": 15
    })
    log_test(f"  Telemetry Ingest Response ({status_telem}): {body_telem}")
    assert status_telem == 200, f"Telemetry ingest failed with status {status_telem}"
    log_test("  [OK] Telemetry Ingestion PASSED")

    # 9. Database Verification: Confirm Telemetry Bound to Correct Student Primary Key
    log_test("Test 9: Verifying database record binding in studiq.db...")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    row = c.execute(
        "SELECT id, student_id, application_name, window_title, category FROM activity_logs WHERE student_id = ? ORDER BY id DESC LIMIT 1",
        (student_pk,)
    ).fetchone()
    conn.close()

    log_test(f"  Database Query Result for Student PK {student_pk}: {row}")
    assert row is not None, f"No ActivityLog record found for student_id {student_pk}!"
    assert row[1] == student_pk, f"Student PK mismatch: expected {student_pk}, got {row[1]}"
    assert row[2] == "VS Code", f"App name mismatch: {row[2]}"
    log_test("  [OK] Telemetry Database Authoritative Student Binding PASSED")

    log_test("==========================================================")
    log_test("  SUCCESS: ALL AUTH & TELEMETRY ACCEPTANCE TESTS PASSED 100%! ")
    log_test("==========================================================")

if __name__ == "__main__":
    run_tests()
