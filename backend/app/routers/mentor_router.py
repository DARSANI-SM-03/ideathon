from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.models.user import Student
from app.models.monitoring import ActivityLog
from app.ai.burnout_engine import burnout_engine
from app.ai.warning_engine import warning_engine

router = APIRouter(prefix="/mentor", tags=["Mentor Portal"])

@router.get("/students")
def get_assigned_students(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    students = db.query(Student).all()
    if not students:
        # Initial seed if empty
        default_students = [
            Student(student_id="STU-2026-001", name="Alex Mercer", department="Computer Science", semester=4, focus_score=85.0, burnout_score=15.0, attendance=92.5, cgpa=3.82),
            Student(student_id="STU-2026-002", name="Sophia Patel", department="Computer Science", semester=4, focus_score=48.0, burnout_score=74.0, attendance=72.0, cgpa=3.10),
            Student(student_id="STU-2026-003", name="Marcus Chen", department="Electronics & Comm", semester=4, focus_score=35.0, burnout_score=88.0, attendance=64.5, cgpa=2.85),
        ]
        db.add_all(default_students)
        db.commit()
        students = db.query(Student).all()

    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    result = []
    for s in students:
        logs = db.query(ActivityLog).filter(
            ActivityLog.student_id == s.id,
            ActivityLog.timestamp >= today_start
        ).all()

        study_secs = sum(l.duration for l in logs if l.category in ["Educational", "Productive"])
        ent_secs = sum(l.duration for l in logs if l.category in ["Entertainment", "Social Media", "Gaming"])

        counseling = s.burnout_score >= 60.0 or s.attendance < 75.0

        result.append({
            "id": str(s.id),
            "name": s.name,
            "email": f"{s.name.lower().replace(' ', '.')}@studiq.edu",
            "studentId": s.student_id,
            "department": s.department,
            "semester": s.semester,
            "attendance": s.attendance,
            "cgpa": s.cgpa,
            "focusScore": round(s.focus_score, 1),
            "burnoutRisk": burnout_engine.get_risk_level(s.burnout_score).lower(),
            "burnoutScore": round(s.burnout_score, 1),
            "currentStatus": "studying" if s.focus_score >= 70 else "distracted",
            "lastActive": datetime.utcnow().isoformat(),
            "assignmentCompletion": 85,
            "quizAverage": 82.0,
            "totalStudyHours": round(study_secs / 3600.0, 1),
            "entertainmentHours": round(ent_secs / 3600.0, 1),
            "isActive": True,
            "counselingRequired": counseling,
            "mentorId": "50"
        })

    return result

@router.get("/priority-queue")
def get_priority_queue(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    high_risk = db.query(Student).filter(Student.burnout_score >= 50.0).order_by(Student.burnout_score.desc()).all()
    
    queue = []
    for s in high_risk:
        categories = []
        if s.burnout_score >= 75.0:
            categories.append("critical_burnout")
        elif s.burnout_score >= 55.0:
            categories.append("high_burnout")

        if s.attendance < 75.0:
            categories.append("low_attendance")

        if s.focus_score < 50.0:
            categories.append("low_focus")

        reason = f"Burnout score ({round(s.burnout_score, 1)}%) with attendance {s.attendance}%. Intervention requested."

        queue.append({
            "student": {
                "id": str(s.id),
                "name": s.name,
                "email": f"{s.name.lower().replace(' ', '.')}@studiq.edu",
                "studentId": s.student_id,
                "department": s.department,
                "semester": s.semester,
                "attendance": s.attendance,
                "cgpa": s.cgpa,
                "focusScore": round(s.focus_score, 1),
                "burnoutRisk": burnout_engine.get_risk_level(s.burnout_score).lower(),
                "burnoutScore": round(s.burnout_score, 1),
                "currentStatus": "distracted",
                "lastActive": datetime.utcnow().isoformat(),
                "assignmentCompletion": 65,
                "quizAverage": 70.0,
                "totalStudyHours": 12.0,
                "entertainmentHours": 18.0,
                "isActive": True,
                "counselingRequired": True,
                "mentorId": "50"
            },
            "categories": categories if categories else ["high_burnout"],
            "priorityScore": int(s.burnout_score),
            "reason": reason
        })

    return queue

@router.get("/dashboard")
def get_mentor_dashboard(db: Session = Depends(get_db)):
    students_list = get_assigned_students(current_user={}, db=db)
    priority_q = get_priority_queue(current_user={}, db=db)

    # Focus Ranking (High to Low)
    focus_rank = sorted(students_list, key=lambda s: s["focusScore"], reverse=True)
    # Burnout Ranking (High to Low)
    burnout_rank = sorted(students_list, key=lambda s: s["burnoutScore"], reverse=True)
    # Most Distracted
    most_distracted = sorted(students_list, key=lambda s: s["entertainmentHours"], reverse=True)

    high_risk_students = [s for s in students_list if s["burnoutScore"] >= 50.0]
    critical_students = [s for s in students_list if s["burnoutScore"] >= 75.0]

    return {
        "totalStudents": len(students_list),
        "students": students_list,
        "priorityQueue": priority_q,
        "highRiskStudents": high_risk_students,
        "criticalStudents": critical_students,
        "focusRanking": focus_rank,
        "burnoutRanking": burnout_rank,
        "mostDistractedStudents": most_distracted
    }

from pydantic import BaseModel
from typing import Optional

class ScheduleInterventionRequest(BaseModel):
    student_name: str
    notes: Optional[str] = None
    date: Optional[str] = None

class SendWarningRequest(BaseModel):
    student_name: str
    warning_message: Optional[str] = None

@router.post("/schedule-intervention")
def schedule_intervention(payload: ScheduleInterventionRequest, db: Session = Depends(get_db)):
    return {
        "status": "success",
        "message": f"Successfully scheduled intervention session for {payload.student_name}."
    }

@router.post("/send-warning")
def send_warning(payload: SendWarningRequest, db: Session = Depends(get_db)):
    return {
        "status": "success",
        "message": f"Successfully sent automated warning notification for {payload.student_name}."
    }



