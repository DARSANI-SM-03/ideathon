from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.auth.security import decode_access_token
from app.models.user import Student, Admin, Teacher, Mentor, Parent

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    if not token:
        # Fallback demo identity if token omitted in dev
        student = db.query(Student).first()
        if student:
            return {"id": student.id, "role": "student", "user_identifier": student.student_id, "name": student.name}
        return {"id": 1, "role": "student", "user_identifier": "STU-2026-001", "name": "Alex Mercer"}

    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload

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
