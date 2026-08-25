from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.auth.security import decode_access_token
from app.models.user import Student, Admin, Teacher, Mentor, Parent

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> dict:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    role = payload.get("role", "").lower()
    user_id = payload.get("user_id")
    sub = payload.get("sub")

    user_obj = None
    if role == "student":
        if user_id:
            user_obj = db.query(Student).filter(Student.id == user_id).first()
        if not user_obj and sub:
            user_obj = db.query(Student).filter((Student.student_id == sub) | (Student.email == sub)).first()
    elif role == "parent":
        if user_id:
            user_obj = db.query(Parent).filter(Parent.id == user_id).first()
        if not user_obj and sub:
            user_obj = db.query(Parent).filter(Parent.email == sub).first()
    elif role == "mentor":
        if user_id:
            user_obj = db.query(Mentor).filter(Mentor.id == user_id).first()
        if not user_obj and sub:
            user_obj = db.query(Mentor).filter((Mentor.employee_id == sub) | (Mentor.email == sub)).first()
    elif role == "admin":
        if user_id:
            user_obj = db.query(Admin).filter(Admin.id == user_id).first()
        if not user_obj and sub:
            user_obj = db.query(Admin).filter((Admin.username == sub) | (Admin.email == sub)).first()
    elif role == "teacher":
        if user_id:
            user_obj = db.query(Teacher).filter(Teacher.id == user_id).first()
        if not user_obj and sub:
            user_obj = db.query(Teacher).filter((Teacher.teacher_id == sub) | (Teacher.email == sub)).first()

    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated user record not found in database",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_identifier = (
        getattr(user_obj, "student_id", None) or
        getattr(user_obj, "employee_id", None) or
        getattr(user_obj, "parent_id", None) or
        getattr(user_obj, "username", None) or
        getattr(user_obj, "teacher_id", None) or
        user_obj.email
    )

    return {
        "id": user_obj.id,
        "user_id": user_obj.id,
        "sub": user_identifier,
        "user_identifier": user_identifier,
        "name": getattr(user_obj, "full_name", None) or getattr(user_obj, "name", "User"),
        "email": user_obj.email,
        "role": getattr(user_obj, "role", role).lower(),
        "department": getattr(user_obj, "department", "General")
    }

def require_role(roles: list[str]):
    def role_checker(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role", "").lower()
        allowed = [r.lower() for r in roles]
        if user_role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User role '{user_role}' is not authorized to access this resource",
            )
        return current_user
    return role_checker

def get_current_user_optional(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    if not token:
        return None
    try:
        return get_current_user(token, db)
    except Exception:
        return None
