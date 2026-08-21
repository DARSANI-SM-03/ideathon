from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class StudentBase(BaseModel):
    student_id: str
    name: str
    email: str
    department: str
    semester: int = 1
    cgpa: float = 0.0
    attendance: float = 0.0
    focus_score: float = 80.0
    burnout_score: float = 20.0

class StudentCreate(StudentBase):
    password: str

class StudentOut(StudentBase):
    id: int
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

class DashboardData(BaseModel):
    student_id: str
    name: str
    department: str
    semester: int
    focus_score: float
    burnout_score: float
    cgpa: float
    attendance: float
    today_productive_time_mins: int
    today_entertainment_time_mins: int
    current_status: str
    pending_assignments_count: int
    avg_quiz_score: float
    recent_warnings: List[dict]
    weekly_analytics: List[dict]
    monthly_analytics: List[dict]
    recommendations: List[str]
