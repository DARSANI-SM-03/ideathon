from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.admin import AdminDashboardMetrics
from app.services.admin_service import admin_service
from app.services.analytics_service import analytics_service

from pydantic import BaseModel

router = APIRouter(prefix="/admin", tags=["Admin"])

class AssignMentorRequest(BaseModel):
    student_identifier: str
    mentor_name: str

@router.get("/dashboard", response_model=AdminDashboardMetrics)
def get_admin_dashboard(db: Session = Depends(get_db)):
    return admin_service.get_admin_dashboard_metrics(db)

@router.get("/analytics")
def get_institution_analytics(db: Session = Depends(get_db)):
    return analytics_service.get_institution_analytics(db)

@router.post("/assign-mentor")
def assign_mentor(payload: AssignMentorRequest, db: Session = Depends(get_db)):
    return admin_service.assign_mentor(db, payload.student_identifier, payload.mentor_name)
