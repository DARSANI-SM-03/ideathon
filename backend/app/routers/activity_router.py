from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.models.activity import Activity
from app.schemas.activity import ActivityOut, ActivityCreate

router = APIRouter(prefix="/activities", tags=["Activities"])

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
