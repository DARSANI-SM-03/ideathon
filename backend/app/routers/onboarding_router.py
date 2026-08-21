from fastapi import APIRouter, Depends, HTTPException, Body  # type: ignore
from sqlalchemy.orm import Session  # type: ignore
from datetime import datetime
from typing import Dict, Any, Optional
from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.models.user import Student, Parent, Mentor, Institution, Department, ParentConsent, MentorAssignment

router = APIRouter(prefix="/onboarding", tags=["Role Workflow & Parent Approval"])

@router.post("/parent-request")
def submit_parent_request(payload: Dict[str, Any] = Body(...), db: Session = Depends(get_db)):
    """
    Step 4 of Onboarding: Student submits parent email and phone.
    Creates a ParentConsent request with status 'Pending'.
    Student status remains 'Pending Approval' and cannot access dashboard.
    """
    student_id = payload.get("student_id", 1)
    parent_email = payload.get("parent_email", "").strip()
    parent_phone = payload.get("parent_phone", "").strip()
    requested_permissions = payload.get("requested_permissions", "App & Web Monitoring, Focus Analysis, Burnout Risk Alerts")
    monitoring_scope = payload.get("monitoring_scope", "Desktop Application Window Titles, Academic Browsing URLs")

    if not parent_email:
        raise HTTPException(status_code=400, detail="Parent email is required.")

    student = db.query(Student).filter((Student.id == student_id) | (Student.student_id == str(student_id))).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    student.parent_email = parent_email
    student.parent_phone = parent_phone
    student.status = "Pending Approval"
    student.monitoring_authorized = False

    # Check for existing request
    consent = db.query(ParentConsent).filter(ParentConsent.student_id == student.id).first()
    if not consent:
        consent = ParentConsent(
            student_id=student.id,
            parent_email=parent_email,
            parent_phone=parent_phone,
            status="Pending",
            requested_permissions=requested_permissions,
            monitoring_scope=monitoring_scope
        )
        db.add(consent)
    else:
        consent.parent_email = parent_email
        consent.parent_phone = parent_phone
        consent.status = "Pending"
        consent.requested_permissions = requested_permissions
        consent.monitoring_scope = monitoring_scope

    db.commit()

    return {
        "status": "success",
        "message": "Parent approval request submitted successfully. Account status is Pending Approval.",
        "student_id": student.student_id,
        "parent_email": parent_email,
        "approval_status": "Pending"
    }

@router.get("/consent-status/{student_id}")
def get_consent_status(student_id: str, db: Session = Depends(get_db)):
    """Returns current consent status, student status, and monitoring authorization."""
    student = db.query(Student).filter((Student.student_id == str(student_id)) | (Student.id == int(student_id) if str(student_id).isdigit() else False)).first()
    if not student:
        # Initial seed if empty
        return {
            "student_id": student_id,
            "student_name": "Alex Mercer",
            "status": "Pending Approval",
            "monitoring_authorized": False,
            "onboarding_completed": False,
            "consent_status": "Pending"
        }

    consent = db.query(ParentConsent).filter(ParentConsent.student_id == student.id).first()

    return {
        "student_id": student.student_id,
        "student_name": student.name,
        "department": student.department,
        "status": student.status,
        "monitoring_authorized": student.monitoring_authorized,
        "onboarding_completed": student.onboarding_completed,
        "parent_email": student.parent_email,
        "consent_status": consent.status if consent else "Pending",
        "requested_permissions": consent.requested_permissions if consent else "App & Web Monitoring",
        "monitoring_scope": consent.monitoring_scope if consent else "Desktop Window Titles"
    }

@router.post("/parent/approve")
def parent_approve_request(payload: Dict[str, Any] = Body(...), db: Session = Depends(get_db)):
    """
    Parent Portal Action: Approve Student Request.
    Permanently activates student account and authorizes Desktop Monitoring Agent.
    """
    student_id = payload.get("student_id", 1)
    student = db.query(Student).filter((Student.id == student_id) | (Student.student_id == str(student_id))).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    consent = db.query(ParentConsent).filter(ParentConsent.student_id == student.id).first()
    if not consent:
        consent = ParentConsent(student_id=student.id, parent_email=student.parent_email or "parent@gmail.com")
        db.add(consent)

    consent.status = "Approved"
    consent.approved_at = datetime.utcnow()

    student.status = "Active"
    student.monitoring_authorized = True
    student.onboarding_completed = True

    db.commit()

    return {
        "status": "success",
        "message": f"Parent approval granted for {student.name}. Account is now Active and monitoring authorized.",
        "student_id": student.student_id,
        "account_status": "Active",
        "monitoring_authorized": True
    }

@router.post("/parent/reject")
def parent_reject_request(payload: Dict[str, Any] = Body(...), db: Session = Depends(get_db)):
    """
    Parent Portal Action: Reject Student Request.
    Blocks student dashboard access and revokes monitoring authorization.
    """
    student_id = payload.get("student_id", 1)
    rejection_reason = payload.get("rejection_reason", "Monitoring scope not accepted by parent.")

    student = db.query(Student).filter((Student.id == student_id) | (Student.student_id == str(student_id))).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    consent = db.query(ParentConsent).filter(ParentConsent.student_id == student.id).first()
    if not consent:
        consent = ParentConsent(student_id=student.id, parent_email=student.parent_email or "parent@gmail.com")
        db.add(consent)

    consent.status = "Rejected"
    consent.rejection_reason = rejection_reason

    student.status = "Blocked"
    student.monitoring_authorized = False

    db.commit()

    return {
        "status": "success",
        "message": f"Parent rejected request for {student.name}. Account remains Blocked.",
        "student_id": student.student_id,
        "account_status": "Blocked",
        "monitoring_authorized": False
    }

@router.post("/admin/assign-mentor")
def admin_assign_mentor(payload: Dict[str, Any] = Body(...), db: Session = Depends(get_db)):
    """Admin workflow: Assign mentor to student."""
    student_id = payload.get("student_id", 1)
    mentor_id = payload.get("mentor_id", 50)

    student = db.query(Student).filter((Student.id == student_id) | (Student.student_id == str(student_id))).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    student.mentor_id = mentor_id

    assignment = MentorAssignment(student_id=student.id, mentor_id=mentor_id, assigned_by_admin_id=99, assigned_at=datetime.utcnow())
    db.add(assignment)

    db.commit()

    return {
        "status": "success",
        "message": f"Mentor #{mentor_id} successfully assigned to student {student.name}.",
        "student_id": student.student_id,
        "mentor_id": mentor_id
    }

@router.post("/admin/transfer-student")
def admin_transfer_student(payload: Dict[str, Any] = Body(...), db: Session = Depends(get_db)):
    """Admin workflow: Transfer student to new department."""
    student_id = payload.get("student_id", 1)
    new_department = payload.get("new_department", "Computer Science")

    student = db.query(Student).filter((Student.id == student_id) | (Student.student_id == str(student_id))).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    student.department = new_department
    db.commit()

    return {
        "status": "success",
        "message": f"Student {student.name} transferred to {new_department}.",
        "student_id": student.student_id,
        "new_department": new_department
    }

@router.post("/admin/deactivate-monitoring")
def admin_deactivate_monitoring(payload: Dict[str, Any] = Body(...), db: Session = Depends(get_db)):
    """Admin workflow: Deactivate desktop monitoring agent for student."""
    student_id = payload.get("student_id", 1)

    student = db.query(Student).filter((Student.id == student_id) | (Student.student_id == str(student_id))).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    student.monitoring_authorized = False
    db.commit()

    return {
        "status": "success",
        "message": f"Monitoring authorization deactivated for {student.name}.",
        "student_id": student.student_id,
        "monitoring_authorized": False
    }

@router.post("/admin/reset-consent")
def admin_reset_consent(payload: Dict[str, Any] = Body(...), db: Session = Depends(get_db)):
    """Admin workflow: Reset student consent status back to Pending Approval."""
    student_id = payload.get("student_id", 1)

    student = db.query(Student).filter((Student.id == student_id) | (Student.student_id == str(student_id))).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    student.status = "Pending Approval"
    student.monitoring_authorized = False
    student.onboarding_completed = False

    consent = db.query(ParentConsent).filter(ParentConsent.student_id == student.id).first()
    if consent:
        consent.status = "Pending"

    db.commit()

    return {
        "status": "success",
        "message": f"Consent status reset for {student.name}.",
        "student_id": student.student_id,
        "status": "Pending Approval"
    }
