from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.database.session import get_db
from datetime import datetime
from app.schemas.auth import (
    LoginRequest, Token, UserProfile, ContinueAuthRequest,
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

@router.post("/continue")
def continue_auth(request: ContinueAuthRequest, db: Session = Depends(get_db)):
    from sqlalchemy import func
    role = request.role.lower()
    user_identifier = request.user_identifier.strip()
    ident_lower = user_identifier.lower()
    password = request.password

    if not user_identifier or not password:
        raise HTTPException(status_code=400, detail="User ID/Email and Password are required.")

    account_found = False
    user_obj = None

    if role == "student":
        user_obj = db.query(Student).filter(
            (func.lower(Student.student_id) == ident_lower) | (func.lower(Student.email) == ident_lower)
        ).first()
        if user_obj:
            account_found = True
    elif role == "admin":
        user_obj = db.query(Admin).filter(
            (func.lower(Admin.username) == ident_lower) | (func.lower(Admin.email) == ident_lower)
        ).first()
        if user_obj:
            account_found = True
        else:
            raise HTTPException(
                status_code=403,
                detail="Admin account not found. Please contact the system administrator."
            )
    elif role == "mentor":
        user_obj = db.query(Mentor).filter(
            (func.lower(Mentor.employee_id) == ident_lower) | (func.lower(Mentor.email) == ident_lower)
        ).first()
        if user_obj:
            account_found = True
    elif role == "teacher":
        user_obj = db.query(Teacher).filter(
            (func.lower(Teacher.teacher_id) == ident_lower) | (func.lower(Teacher.email) == ident_lower)
        ).first()
        if user_obj:
            account_found = True
    elif role == "parent":
        user_obj = db.query(Parent).filter(func.lower(Parent.email) == ident_lower).first()
        if user_obj:
            account_found = True
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported role '{role}'")

    # Cross-role lookup check if account was not found in the selected role tab
    if not account_found or not user_obj:
        other_role = None
        if db.query(Student).filter((func.lower(Student.student_id) == ident_lower) | (func.lower(Student.email) == ident_lower)).first():
            other_role = "Student"
        elif db.query(Parent).filter(func.lower(Parent.email) == ident_lower).first():
            other_role = "Parent"
        elif db.query(Mentor).filter((func.lower(Mentor.employee_id) == ident_lower) | (func.lower(Mentor.email) == ident_lower)).first():
            other_role = "Mentor"
        elif db.query(Teacher).filter((func.lower(Teacher.teacher_id) == ident_lower) | (func.lower(Teacher.email) == ident_lower)).first():
            other_role = "Teacher"

        if other_role:
            raise HTTPException(
                status_code=400,
                detail=f"An account with this ID or Email exists as a {other_role}. Please select the {other_role} tab to sign in."
            )

        return {
            "status": "registration_required",
            "role": role,
            "user_identifier": user_identifier,
            "message": "No StudIQ account found. Let's create your account."
        }

    # Verify Password for existing account
    if not verify_password(password, user_obj.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Incorrect password. Please check your password and try again."
        )

    # Determine user identifier string
    sub = (
        getattr(user_obj, "student_id", None) or
        getattr(user_obj, "employee_id", None) or
        getattr(user_obj, "parent_id", None) or
        getattr(user_obj, "username", None) or
        getattr(user_obj, "teacher_id", None) or
        user_obj.email
    )

    name = getattr(user_obj, "full_name", None) or getattr(user_obj, "name", "User")
    payload_data = {
        "sub": sub,
        "role": role,
        "user_id": user_obj.id,
        "name": name,
        "email": user_obj.email
    }

    access_token = create_access_token(data=payload_data)
    refresh_token = create_refresh_token(data=payload_data)

    redirect_map = {
        "student": "/student/dashboard",
        "parent": "/parent/dashboard",
        "mentor": "/mentor/dashboard",
        "teacher": "/teacher/dashboard",
        "admin": "/admin/dashboard"
    }

    return {
        "status": "authenticated",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "role": role,
        "user_id": user_obj.id,
        "user_identifier": sub,
        "name": name,
        "email": user_obj.email,
        "redirect": redirect_map.get(role, "/student/dashboard")
    }

@router.post("/register/student")
def register_student(req: StudentRegisterRequest, db: Session = Depends(get_db)):
    from sqlalchemy import func
    sid_lower = req.student_id.strip().lower()
    email_lower = req.email.strip().lower()

    existing = db.query(Student).filter(
        (func.lower(Student.student_id) == sid_lower) | (func.lower(Student.email) == email_lower)
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="ACCOUNT_ALREADY_EXISTS: An account with this Student ID or Email already exists. Please sign in."
        )

    new_student = Student(
        student_id=req.student_id.strip(),
        full_name=req.full_name.strip(),
        name=req.full_name.strip(),
        email=req.email.strip(),
        department=req.department,
        semester=req.semester,
        password_hash=get_password_hash(req.password),
        parent_email=req.parent_email.strip() if req.parent_email else "",
        parent_phone=req.parent_phone.strip() if req.parent_phone else "",
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
        student_name=req.full_name.strip(),
        student_code=req.student_id.strip(),
        college_name=req.college_name or "Global Institute of Technology",
        department=req.department,
        parent_email=req.parent_email.strip() if req.parent_email else "",
        parent_phone=req.parent_phone.strip() if req.parent_phone else "",
        status="Approved"
    )
    db.add(approval_req)
    db.commit()

    # Notify Parent if parent account exists
    parent = db.query(Parent).filter(func.lower(Parent.email) == (req.parent_email.strip().lower() if req.parent_email else "")).first()
    if parent:
        notif = Notification(
            student_id=new_student.id,
            parent_id=parent.id,
            title="Student Registration Completed",
            message=f"{req.full_name} registered as a student on StudIQ."
        )
        db.add(notif)
        db.commit()

    payload_data = {
        "sub": new_student.student_id,
        "role": "student",
        "user_id": new_student.id,
        "name": new_student.full_name,
        "email": new_student.email
    }
    access_token = create_access_token(data=payload_data)
    refresh_token = create_refresh_token(data=payload_data)

    return {
        "status": "success",
        "message": "Account created successfully. Signing you in...",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "role": "student",
        "user_id": new_student.id,
        "user_identifier": new_student.student_id,
        "name": new_student.full_name,
        "email": new_student.email,
        "redirect": "/student/dashboard"
    }

@router.post("/register/parent")
def register_parent(req: ParentRegisterRequest, db: Session = Depends(get_db)):
    from sqlalchemy import func
    email_lower = req.email.strip().lower()

    existing = db.query(Parent).filter(func.lower(Parent.email) == email_lower).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="ACCOUNT_ALREADY_EXISTS: An account with this Email already exists. Please sign in."
        )

    parent_id = f"PAR-{int(datetime.utcnow().timestamp())}"
    new_parent = Parent(
        parent_id=parent_id,
        full_name=req.full_name.strip(),
        name=req.full_name.strip(),
        email=req.email.strip(),
        phone=req.phone.strip() if req.phone else "",
        password_hash=get_password_hash(req.password)
    )
    db.add(new_parent)
    db.commit()
    db.refresh(new_parent)

    payload_data = {
        "sub": parent_id,
        "role": "parent",
        "user_id": new_parent.id,
        "name": new_parent.full_name,
        "email": new_parent.email
    }
    access_token = create_access_token(data=payload_data)
    refresh_token = create_refresh_token(data=payload_data)

    return {
        "status": "success",
        "message": "Account created successfully. Signing you in...",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "role": "parent",
        "user_id": new_parent.id,
        "user_identifier": parent_id,
        "name": new_parent.full_name,
        "email": new_parent.email,
        "redirect": "/parent/dashboard"
    }

@router.post("/register/admin")
def register_admin(req: AdminRegisterRequest, db: Session = Depends(get_db)):
    raise HTTPException(status_code=403, detail="Admin account not found. Please contact the system administrator.")

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
    db.refresh(new_mentor)

    payload_data = {
        "sub": new_mentor.employee_id,
        "role": "mentor",
        "user_id": new_mentor.id,
        "name": new_mentor.full_name,
        "email": new_mentor.email
    }
    access_token = create_access_token(data=payload_data)
    refresh_token = create_refresh_token(data=payload_data)

    return {
        "status": "success",
        "message": "Account created successfully. Signing you in...",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "role": "mentor",
        "user_id": new_mentor.id,
        "user_identifier": new_mentor.employee_id,
        "name": new_mentor.full_name,
        "email": new_mentor.email,
        "redirect": "/mentor/dashboard"
    }

@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    role = request.role.lower()
    user_id = None
    name = None
    email = None
    user_identifier = request.user_identifier.strip()

    if role == "student":
        student = db.query(Student).filter(
            (Student.student_id == user_identifier) | (Student.email == user_identifier)
        ).first()
        if not student:
            raise HTTPException(status_code=401, detail="No student account found for this ID or email.")
        if student.status in ["Rejected", "Blocked"]:
            raise HTTPException(status_code=403, detail="Registration rejected by Parent or Admin.")
        if not verify_password(request.password, student.password_hash):
            raise HTTPException(status_code=401, detail="Invalid password for student account.")
        
        user_id = student.id
        name = student.full_name or student.name
        email = student.email
        user_identifier = student.student_id or student.email

    elif role == "admin":
        admin = db.query(Admin).filter(
            (Admin.username == user_identifier) | (Admin.email == user_identifier)
        ).first()
        if not admin:
            raise HTTPException(status_code=401, detail="No admin account found for this username or email.")
        if not verify_password(request.password, admin.password_hash):
            raise HTTPException(status_code=401, detail="Invalid password for admin account.")
        
        user_id = admin.id
        name = admin.full_name or admin.name
        email = admin.email
        user_identifier = admin.username or admin.email

    elif role == "mentor":
        mentor = db.query(Mentor).filter(
            (Mentor.employee_id == user_identifier) | (Mentor.email == user_identifier)
        ).first()
        if not mentor:
            raise HTTPException(status_code=401, detail="No mentor account found for this Employee ID or email.")
        if not verify_password(request.password, mentor.password_hash):
            raise HTTPException(status_code=401, detail="Invalid password for mentor account.")
        
        user_id = mentor.id
        name = mentor.full_name or mentor.name
        email = mentor.email
        user_identifier = mentor.employee_id or mentor.email

    elif role == "parent":
        parent = db.query(Parent).filter(Parent.email == user_identifier).first()
        if not parent:
            raise HTTPException(status_code=401, detail="No parent account found for this email address.")
        if not verify_password(request.password, parent.password_hash):
            raise HTTPException(status_code=401, detail="Invalid password for parent account.")
        
        user_id = parent.id
        name = parent.full_name or parent.name
        email = parent.email
        user_identifier = parent.parent_id or parent.email

    else:
        raise HTTPException(status_code=400, detail=f"Unsupported role '{role}'")

    payload_data = {
        "sub": user_identifier,
        "role": role,
        "user_id": user_id,
        "name": name,
        "email": email
    }

    access_token = create_access_token(data=payload_data)
    refresh_token = create_refresh_token(data=payload_data)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "role": role,
        "user_id": user_id,
        "user_identifier": user_identifier,
        "name": name,
        "email": email
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
        "name": decoded.get("name"),
        "email": decoded.get("email")
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
    user_id = current_user.get("user_id")

    student = db.query(Student).filter(Student.id == user_id).first()
    if student:
        if not verify_password(old_pw, student.password_hash):
            raise HTTPException(status_code=400, detail="Incorrect old password.")
        student.password_hash = get_password_hash(new_pw)
        db.commit()

    return {"status": "success", "message": "Password changed successfully."}

@router.get("/me", response_model=UserProfile)
def get_me(current_user: dict = Depends(get_current_user)):
    return UserProfile(
        id=current_user["id"],
        user_identifier=current_user["user_identifier"],
        name=current_user["name"],
        email=current_user["email"],
        role=current_user["role"],
        department=current_user.get("department", "General")
    )

