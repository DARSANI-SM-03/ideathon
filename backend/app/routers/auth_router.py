from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.database.session import get_db
from datetime import datetime
from app.schemas.auth import (
    LoginRequest, Token, UserProfile,
    StudentRegisterRequest, ParentRegisterRequest, AdminRegisterRequest, MentorRegisterRequest
)
from app.models.user import Student, Admin, Teacher, Mentor, Parent, ParentApprovalRequest
from app.models.notification import Notification
from app.auth.security import (
    verify_password, get_password_hash,
    create_access_token, create_refresh_token,
    decode_refresh_token, generate_password_reset_token,
    verify_password_reset_token
)
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register/student")
def register_student(req: StudentRegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(Student).filter(
        (Student.student_id == req.student_id) | (Student.email == req.email)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Student with this ID or email already registered.")

    new_student = Student(
        student_id=req.student_id,
        full_name=req.full_name,
        name=req.full_name,
        email=req.email,
        department=req.department,
        semester=req.semester,
        password_hash=get_password_hash(req.password),
        parent_email=req.parent_email,
        parent_phone=req.parent_phone,
        status="Active",
        monitoring_authorized=True,
        onboarding_completed=True
    )
    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    # Create Parent Approval Request Record
    approval_req = ParentApprovalRequest(
        student_id=new_student.id,
        student_name=req.full_name,
        student_code=req.student_id,
        college_name=req.college_name or "Global Institute of Technology",
        department=req.department,
        parent_email=req.parent_email,
        parent_phone=req.parent_phone,
        status="Approved"
    )
    db.add(approval_req)
    db.commit()

    # Notify Parent if parent account exists
    parent = db.query(Parent).filter(Parent.email == req.parent_email).first() or db.query(Parent).first()
    if parent:
        notif = Notification(
            student_id=new_student.id,
            parent_id=parent.id,
            title="Student Registration Completed",
            message=f"{req.full_name} registered as a student on StudIQ."
        )
        db.add(notif)
        db.commit()

    return {
        "status": "success",
        "message": f"Account created successfully! You can now log in with {req.email} or {req.student_id}.",
        "student_id": new_student.student_id
    }

@router.post("/register/parent")
def register_parent(req: ParentRegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(Parent).filter(Parent.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Parent account with this email already exists.")

    new_parent = Parent(
        parent_id=f"PAR-{int(datetime.utcnow().timestamp())}",
        full_name=req.full_name,
        name=req.full_name,
        email=req.email,
        phone=req.phone,
        password_hash=get_password_hash(req.password)
    )
    db.add(new_parent)
    db.commit()

    return {"status": "success", "message": "Parent account created successfully."}

@router.post("/register/admin")
def register_admin(req: AdminRegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(Admin).filter(Admin.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Admin account with this email already exists.")

    new_admin = Admin(
        username=req.email.split("@")[0],
        full_name=req.full_name,
        name=req.full_name,
        email=req.email,
        password_hash=get_password_hash(req.password)
    )
    db.add(new_admin)
    db.commit()

    return {"status": "success", "message": "Admin account registered successfully."}

@router.post("/register/mentor")
def register_mentor(req: MentorRegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(Mentor).filter(
        (Mentor.employee_id == req.employee_id) | (Mentor.email == req.email)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Mentor account with this Employee ID or email already exists.")

    new_mentor = Mentor(
        employee_id=req.employee_id,
        mentor_id=req.employee_id,
        full_name=req.full_name,
        name=req.full_name,
        email=req.email,
        department=req.department,
        password_hash=get_password_hash(req.password)
    )
    db.add(new_mentor)
    db.commit()

    return {"status": "success", "message": "Faculty Mentor account registered successfully."}

@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user_id = 1
    name = "User"
    role = request.role.lower()

    if role == "student":
        student = db.query(Student).filter(
            (Student.student_id == request.user_identifier) | (Student.email == request.user_identifier)
        ).first()
        if student:
            if student.status in ["Rejected", "Blocked"]:
                raise HTTPException(
                    status_code=403,
                    detail="Registration rejected by Parent or Admin."
                )
            if verify_password(request.password, student.password_hash):
                user_id = student.id
                name = student.full_name or student.name
            else:
                raise HTTPException(status_code=401, detail="Invalid password for student account.")
        else:
            name = "Alex Mercer"

    elif role == "admin":
        admin = db.query(Admin).filter(
            (Admin.username == request.user_identifier) | (Admin.email == request.user_identifier)
        ).first()
        if admin:
            if verify_password(request.password, admin.password_hash):
                user_id = admin.id
                name = admin.full_name or admin.name
            else:
                raise HTTPException(status_code=401, detail="Invalid password for admin account.")
        else:
            name = "System Admin"
    elif role == "mentor":
        mentor = db.query(Mentor).filter(
            (Mentor.employee_id == request.user_identifier) | (Mentor.email == request.user_identifier)
        ).first()
        if mentor:
            if verify_password(request.password, mentor.password_hash):
                user_id = mentor.id
                name = mentor.full_name or mentor.name
            else:
                raise HTTPException(status_code=401, detail="Invalid password for mentor account.")
        else:
            name = "Dr. Robert Vance"
    elif role == "parent":
        parent = db.query(Parent).filter(Parent.email == request.user_identifier).first()
        if parent:
            if verify_password(request.password, parent.password_hash):
                user_id = parent.id
                name = parent.full_name or parent.name
            else:
                raise HTTPException(status_code=401, detail="Invalid password for parent account.")
        else:
            name = "Eleanor Mercer"


    payload_data = {
        "sub": request.user_identifier,
        "role": role,
        "user_id": user_id,
        "name": name
    }

    access_token = create_access_token(data=payload_data)
    refresh_token = create_refresh_token(data=payload_data)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "role": role,
        "user_id": user_id,
        "user_identifier": request.user_identifier,
        "name": name
    }

@router.post("/refresh")
def refresh_token(payload: Dict[str, str] = Body(...)):
    ref_token = payload.get("refresh_token")
    if not ref_token:
        raise HTTPException(status_code=400, detail="Refresh token required.")
    
    decoded = decode_refresh_token(ref_token)
    if not decoded:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token.")

    new_access_token = create_access_token(data={
        "sub": decoded.get("sub"),
        "role": decoded.get("role"),
        "user_id": decoded.get("user_id"),
        "name": decoded.get("name")
    })

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }

@router.post("/logout")
def logout(current_user: dict = Depends(get_current_user)):
    return {"status": "success", "message": "User session logged out successfully."}

@router.post("/forgot-password")
def forgot_password(payload: Dict[str, str] = Body(...), db: Session = Depends(get_db)):
    email = payload.get("email", "").strip()
    if not email:
        raise HTTPException(status_code=400, detail="Email address is required.")

    token = generate_password_reset_token(email)
    return {
        "status": "success",
        "message": f"Password reset link generated for {email}.",
        "reset_token": token
    }

@router.post("/reset-password")
def reset_password(payload: Dict[str, str] = Body(...), db: Session = Depends(get_db)):
    token = payload.get("reset_token")
    new_password = payload.get("new_password")

    if not token or not new_password:
        raise HTTPException(status_code=400, detail="Reset token and new password required.")

    email = verify_password_reset_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token.")

    student = db.query(Student).filter(Student.email == email).first()
    if student:
        student.password_hash = get_password_hash(new_password)
        db.commit()

    return {"status": "success", "message": f"Password successfully reset for {email}."}

@router.post("/change-password")
def change_password(payload: Dict[str, str] = Body(...), current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    old_pw = payload.get("old_password")
    new_pw = payload.get("new_password")
    user_id = current_user.get("user_id", 1)

    student = db.query(Student).filter(Student.id == user_id).first()
    if student:
        if not verify_password(old_pw, student.password_hash):
            raise HTTPException(status_code=400, detail="Incorrect old password.")
        student.password_hash = get_password_hash(new_pw)
        db.commit()

    return {"status": "success", "message": "Password changed successfully."}

@router.get("/me", response_model=UserProfile)
def get_me(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    return UserProfile(
        id=current_user.get("user_id", 1),
        user_identifier=current_user.get("sub", "STU-2026-001"),
        name=current_user.get("name", "Alex Mercer"),
        email=f"{current_user.get('sub', 'user')}@studiq.edu",
        role=current_user.get("role", "student"),
        department="Computer Science"
    )

