from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.models.activity import Activity
from app.schemas.activity import ActivityOut, ActivityCreate

from datetime import datetime, timedelta
from app.models.monitoring import ActivityLog
from app.ai.central_metrics_engine import central_metrics_engine

router = APIRouter(prefix="/activity", tags=["Activities & Telemetry History"])

@router.get("/history")
def get_activity_history(
    student_id: int = 1,
    timeframe: str = "Today",
    category: str = "All",
    search: str = "",
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Returns filtered ActivityLog database records for Activity History page.
    Filters: Today, 7 Days, 30 Days, Semester.
    """
    now = datetime.utcnow()
    tf_clean = timeframe.lower().strip()

    if tf_clean == "today":
        since_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif tf_clean in ["7 days", "7d", "week"]:
        since_time = now - timedelta(days=7)
    elif tf_clean in ["30 days", "30d", "month"]:
        since_time = now - timedelta(days=30)
    else:  # Semester
        since_time = now - timedelta(days=90)

    query = db.query(ActivityLog).filter(
        ActivityLog.student_id == student_id,
        ActivityLog.timestamp >= since_time
    )

    if category and category != "All":
        query = query.filter(ActivityLog.category == category)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (ActivityLog.application_name.ilike(search_pattern)) |
            (ActivityLog.window_title.ilike(search_pattern)) |
            (ActivityLog.website_url.ilike(search_pattern))
        )

    logs = query.order_by(ActivityLog.timestamp.desc()).limit(limit).all()

    focus_res = central_metrics_engine.calculate_focus_index(db, student_id, hours_lookback=24.0)
    burnout_res = central_metrics_engine.calculate_burnout_risk(db, student_id, hours_lookback=24.0)

    formatted_items = [
        {
            "id": l.id,
            "app": l.application_name,
            "context": l.window_title or l.website_url or l.application_name,
            "category": l.category,
            "duration": f"{max(1, l.duration // 60)} Mins" if l.duration >= 60 else f"{l.duration} Secs",
            "duration_secs": l.duration,
            "focus": int(focus_res["focus_score"]),
            "burnout": int(burnout_res["probability"]),
            "time": l.timestamp.strftime("%I:%M %p") if l.timestamp else "",
            "date": l.timestamp.strftime("%Y-%m-%d") if l.timestamp else ""
        }
        for l in logs
    ]

    return {
        "timeframe": timeframe,
        "total_records": len(formatted_items),
        "avg_focus": focus_res["focus_score"],
        "avg_burnout": burnout_res["probability"],
        "burnout_risk_level": burnout_res["risk_level"],
        "items": formatted_items
    }

@router.get("/student/{student_id}", response_model=List[ActivityOut])
def get_student_activities(student_id: int, limit: int = 50, db: Session = Depends(get_db)):
    return db.query(Activity).filter(Activity.student_id == student_id).order_by(Activity.activity_id.desc()).limit(limit).all()

@router.post("/", response_model=ActivityOut)
def create_activity(activity_in: ActivityCreate, db: Session = Depends(get_db)):
    activity = Activity(
        student_id=activity_in.student_id,
        application_name=activity_in.application_name,
        window_title=activity_in.window_title,
        website=activity_in.website,
        category=activity_in.category,
        duration=activity_in.duration
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity
