from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class AttendanceOut(BaseModel):
    id: int
    student_id: int
    date: date
    subject: str
    status: str

    class Config:
        from_attributes = True

class QuizOut(BaseModel):
    id: int
    student_id: int
    subject: str
    quiz_name: str
    score: float
    max_score: float
    date: date

    class Config:
        from_attributes = True

class AssignmentOut(BaseModel):
    id: int
    student_id: int
    subject: str
    title: str
    due_date: datetime
    status: str
    grade: Optional[str] = None

    class Config:
        from_attributes = True
