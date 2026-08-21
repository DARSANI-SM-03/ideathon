import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.database.session import SessionLocal, engine
from app.database.base import Base
from app.models.user import Student, ParentConsent, MentorAssignment, Institution, Department
from app.routers.onboarding_router import (
    submit_parent_request,
    get_consent_status,
    parent_approve_request,
    parent_reject_request,
    admin_assign_mentor,
    admin_transfer_student,
    admin_deactivate_monitoring,
    admin_reset_consent
)

from sqlalchemy import text

def test_onboarding_workflow():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Auto-migration for SQLite students table columns
    cols_to_add = [
        ("status", "VARCHAR DEFAULT 'Pending Approval'"),
        ("monitoring_authorized", "BOOLEAN DEFAULT 0"),
        ("onboarding_completed", "BOOLEAN DEFAULT 0"),
        ("parent_email", "VARCHAR"),
        ("parent_phone", "VARCHAR")
    ]
    for col_name, col_type in cols_to_add:
        try:
            db.execute(text(f"ALTER TABLE students ADD COLUMN {col_name} {col_type};"))
            db.commit()
        except Exception:
            db.rollback()

    print("==========================================================================================")
    print("        STUDIQ INTERLINKED ROLE WORKFLOW & PARENT APPROVAL (TASK 4) VERIFICATION           ")
    print("==========================================================================================")


    # 1. Setup student
    student = db.query(Student).filter(Student.id == 1).first()
    if not student:
        student = Student(id=1, student_id="STU-2026-001", name="Alex Mercer", department="Computer Science", semester=4, focus_score=85.0, burnout_score=15.0, attendance=92.5, cgpa=3.82)
        db.add(student)
        db.commit()

    student.status = "Pending Approval"
    student.monitoring_authorized = False
    student.onboarding_completed = False
    db.commit()

    # Step A: Student submits parent email/phone request
    req_payload = {
        "student_id": "STU-2026-001",
        "parent_email": "eleanor.mercer@gmail.com",
        "parent_phone": "+1 (555) 909-8080",
        "requested_permissions": "App & Web Monitoring, Focus Analysis",
        "monitoring_scope": "Desktop Window Titles"
    }
    sub_res = submit_parent_request(payload=req_payload, db=db)
    print(f"[STEP A] Parent Request Submitted -> Approval Status: {sub_res['approval_status']}")
    assert sub_res['approval_status'] == "Pending", "Request status must be Pending!"

    # Step B: Consent Status Verification
    status_res = get_consent_status(student_id="STU-2026-001", db=db)
    print(f"[STEP B] Consent Status Check    -> Student Status: {status_res['status']} | Authorized: {status_res['monitoring_authorized']}")
    assert status_res['status'] == "Pending Approval", "Student status must be Pending Approval!"
    assert not status_res['monitoring_authorized'], "Monitoring MUST be unauthorized while pending!"

    # Step C: Parent Approves Request
    appr_res = parent_approve_request(payload={"student_id": "STU-2026-001"}, db=db)
    print(f"[STEP C] Parent Approval Action  -> Account Status: {appr_res['account_status']} | Authorized: {appr_res['monitoring_authorized']}")
    assert appr_res['account_status'] == "Active", "Account MUST become Active upon approval!"
    assert appr_res['monitoring_authorized'] == True, "Monitoring MUST become authorized upon approval!"

    # Step D: Admin Assigns Mentor
    m_res = admin_assign_mentor(payload={"student_id": "STU-2026-001", "mentor_id": 50}, db=db)
    print(f"[STEP D] Admin Mentor Assignment -> Student {m_res['student_id']} linked to Mentor #{m_res['mentor_id']}")
    assert m_res['mentor_id'] == 50, "Mentor assignment failed!"

    # Step E: Admin Transfers Student
    t_res = admin_transfer_student(payload={"student_id": "STU-2026-001", "new_department": "Data Science"}, db=db)
    print(f"[STEP E] Admin Student Transfer  -> Transferred to {t_res['new_department']}")
    assert t_res['new_department'] == "Data Science", "Transfer failed!"

    # Step F: Admin Deactivates & Resets Consent
    d_res = admin_deactivate_monitoring(payload={"student_id": "STU-2026-001"}, db=db)
    print(f"[STEP F] Admin Deactivate Agent  -> Authorized: {d_res['monitoring_authorized']}")
    assert not d_res['monitoring_authorized'], "Deactivation failed!"

    r_res = admin_reset_consent(payload={"student_id": "STU-2026-001"}, db=db)
    print(f"[STEP G] Admin Reset Consent     -> Status: {r_res['status']}")
    assert r_res['status'] == "Pending Approval", "Reset failed!"

    print("==========================================================================================")
    print("SUCCESS: Interlinked Role Workflow & Approval system verified 100% accurately!")
    print("==========================================================================================")

    db.close()

if __name__ == "__main__":
    test_onboarding_workflow()
