from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.user import Student
from app.models.activity import Activity

class AnalyticsService:
    def get_institution_analytics(self, db: Session) -> dict:
        students = db.query(Student).all()
        if not students:
            return {}

        focus_distribution = {
            "High (80-100)": sum(1 for s in students if s.focus_score >= 80),
            "Moderate (60-79)": sum(1 for s in students if 60 <= s.focus_score < 80),
            "Low (<60)": sum(1 for s in students if s.focus_score < 60)
        }

        burnout_distribution = {
            "Low (<30)": sum(1 for s in students if s.burnout_score < 30),
            "Moderate (30-59)": sum(1 for s in students if 30 <= s.burnout_score < 60),
            "High (60-79)": sum(1 for s in students if 60 <= s.burnout_score < 80),
            "Critical (80+)": sum(1 for s in students if s.burnout_score >= 80)
        }

        scatter_data = [
            {
                "student_id": s.student_id,
                "name": s.name,
                "department": s.department,
                "focus_score": round(s.focus_score, 1),
                "burnout_score": round(s.burnout_score, 1),
                "cgpa": s.cgpa
            }
            for s in students[:100]  # sample 100 for fast scatter rendering
        ]

        return {
            "focus_distribution": focus_distribution,
            "burnout_distribution": burnout_distribution,
            "scatter_data": scatter_data
        }

analytics_service = AnalyticsService()
