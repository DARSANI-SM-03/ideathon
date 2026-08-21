from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.models.user import Student
from app.schemas.student import StudentOut, StudentCreate, DashboardData
from app.services.student_service import student_service
from app.auth.security import get_password_hash

router = APIRouter(prefix="/students", tags=["Students"])

@router.get("/", response_model=List[StudentOut])
def get_all_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Student).offset(skip).limit(limit).all()

@router.post("/", response_model=StudentOut)
def create_student(student_in: StudentCreate, db: Session = Depends(get_db)):
    existing = db.query(Student).filter(Student.student_id == student_in.student_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Student ID already registered")

    student = Student(
        student_id=student_in.student_id,
        name=student_in.name,
        email=student_in.email,
        department=student_in.department,
        semester=student_in.semester,
        cgpa=student_in.cgpa,
        attendance=student_in.attendance,
        focus_score=student_in.focus_score,
        burnout_score=student_in.burnout_score,
        password_hash=get_password_hash(student_in.password)
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student

@router.get("/{student_id}/dashboard", response_model=DashboardData)
def get_student_dashboard(student_id: str, db: Session = Depends(get_db)):
    return student_service.get_student_dashboard(db, student_id)
