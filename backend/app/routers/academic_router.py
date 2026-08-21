from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.models.academic import AttendanceRecord, QuizScore, Assignment
from app.schemas.academic import AttendanceOut, QuizOut, AssignmentOut

router = APIRouter(prefix="/academic", tags=["Academic Records"])

@router.get("/attendance/{student_id}", response_model=List[AttendanceOut])
def get_attendance(student_id: int, db: Session = Depends(get_db)):
    return db.query(AttendanceRecord).filter(AttendanceRecord.student_id == student_id).all()

@router.get("/quizzes/{student_id}", response_model=List[QuizOut])
def get_quizzes(student_id: int, db: Session = Depends(get_db)):
    return db.query(QuizScore).filter(QuizScore.student_id == student_id).all()

@router.get("/assignments/{student_id}", response_model=List[AssignmentOut])
def get_assignments(student_id: int, db: Session = Depends(get_db)):
    return db.query(Assignment).filter(Assignment.student_id == student_id).all()
