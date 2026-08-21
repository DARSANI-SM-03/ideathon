from datetime import datetime
from sqlalchemy.orm import Session
from app.models.activity import Activity
from app.models.user import Student
from app.ai.behavior_engine import behavior_engine
from app.ai.focus_engine import focus_engine
from app.schemas.activity import TelemetryPayload

class MonitoringService:
    def process_telemetry(self, db: Session, payload: TelemetryPayload) -> dict:
        student = db.query(Student).filter(Student.id == payload.student_id).first()
        if not student:
            return {"status": "error", "message": "Student not found"}

        # Auto-classify category if not provided
        category = payload.category or behavior_engine.classify_activity(
            payload.application_name,
            payload.window_title or "",
            payload.website or ""
        )

        activity = Activity(
            student_id=student.id,
            application_name=payload.application_name,
            window_title=payload.window_title,
            website=payload.website,
            category=category,
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow(),
            duration=payload.duration
        )

        db.add(activity)
        db.commit()
        db.refresh(activity)

        # Recalculate focus score for student
        recent_activities = db.query(Activity).filter(Activity.student_id == student.id).limit(50).all()
        act_dicts = [{"category": a.category, "duration": a.duration} for a in recent_activities]
        new_focus = focus_engine.compute_focus_score(act_dicts)

        student.focus_score = new_focus
        db.commit()

        return {
            "status": "success",
            "activity_id": activity.activity_id,
            "assigned_category": category,
            "updated_focus_score": new_focus
        }

monitoring_service = MonitoringService()
