from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.models.user import Student
from app.schemas.student import StudentOut, StudentCreate, DashboardData
from app.services.student_service import student_service
from app.auth.security import get_password_hash

from fastapi import Body
from datetime import datetime
from app.models.monitoring import StudentSettings, StudySession, ActivityLog

router = APIRouter(prefix="/students", tags=["Students"])

@router.get("/settings")
def get_student_settings(student_id: int = 1, db: Session = Depends(get_db)):
    settings = db.query(StudentSettings).filter(StudentSettings.student_id == student_id).first()
    if not settings:
        settings = StudentSettings(student_id=student_id)
        db.add(settings)
        db.commit()
        db.refresh(settings)

    return {
        "student_id": settings.student_id,
        "theme": settings.theme,
        "daily_study_target_mins": settings.daily_study_target_mins,
        "daily_entertainment_limit_mins": settings.daily_entertainment_limit_mins,
        "pomodoro_focus_mins": settings.pomodoro_focus_mins,
        "pomodoro_break_mins": settings.pomodoro_break_mins,
        "idle_threshold_secs": settings.idle_threshold_secs,
        "notifications_enabled": settings.notifications_enabled,
        "sound_alerts_enabled": settings.sound_alerts_enabled
    }

@router.put("/settings")
def update_student_settings(payload: dict = Body(...), student_id: int = 1, db: Session = Depends(get_db)):
    settings = db.query(StudentSettings).filter(StudentSettings.student_id == student_id).first()
    if not settings:
        settings = StudentSettings(student_id=student_id)
        db.add(settings)

    if "theme" in payload: settings.theme = payload["theme"]
    if "daily_study_target_mins" in payload: settings.daily_study_target_mins = payload["daily_study_target_mins"]
    if "daily_entertainment_limit_mins" in payload: settings.daily_entertainment_limit_mins = payload["daily_entertainment_limit_mins"]
    if "pomodoro_focus_mins" in payload: settings.pomodoro_focus_mins = payload["pomodoro_focus_mins"]
    if "pomodoro_break_mins" in payload: settings.pomodoro_break_mins = payload["pomodoro_break_mins"]
    if "idle_threshold_secs" in payload: settings.idle_threshold_secs = payload["idle_threshold_secs"]
    if "notifications_enabled" in payload: settings.notifications_enabled = payload["notifications_enabled"]
    if "sound_alerts_enabled" in payload: settings.sound_alerts_enabled = payload["sound_alerts_enabled"]

    db.commit()
    return {"status": "success", "message": "Settings updated successfully"}

@router.post("/sessions")
def create_study_session(payload: dict = Body(...), student_id: int = 1, db: Session = Depends(get_db)):
    session_type = payload.get("session_type", "Pomodoro")
    duration_mins = payload.get("planned_duration_mins", 50)

    session = StudySession(
        student_id=student_id,
        session_type=session_type,
        planned_duration_mins=duration_mins,
        started_at=datetime.utcnow(),
        completed=False
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return {"status": "started", "session_id": session.id, "planned_duration_mins": duration_mins}

@router.patch("/sessions/{session_id}")
def update_study_session(session_id: int, payload: dict = Body(...), db: Session = Depends(get_db)):
    session = db.query(StudySession).filter(StudySession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Study session not found")

    completed = payload.get("completed", True)
    actual_secs = payload.get("actual_duration_secs", session.planned_duration_mins * 60)

    session.completed = completed
    session.actual_duration_secs = actual_secs
    session.ended_at = datetime.utcnow()

    # Log to ActivityLog for session metrics
    log = ActivityLog(
        student_id=session.student_id,
        application_name="StudIQ Pomodoro Workspace",
        window_title=f"Focus Session: {session.session_type}",
        website_url="",
        category="Educational",
        confidence=0.98,
        duration=actual_secs
    )
    db.add(log)
    db.commit()

    return {"status": "completed", "session_id": session.id, "duration_secs": actual_secs}

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
