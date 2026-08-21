from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.monitoring import ActivityLog


class TimelineEngine:
    """
    Generates daily AI Activity Timelines capturing sequential study sessions,
    entertainment breaks, and study returns from real telemetry.
    """

    def generate_daily_timeline_from_db(
        self,
        db: Session,
        student_id: int = 1,
        hours_lookback: float = 24.0
    ) -> List[Dict[str, Any]]:
        since_time = datetime.utcnow() - timedelta(hours=hours_lookback)
        logs = db.query(ActivityLog).filter(
            ActivityLog.student_id == student_id,
            ActivityLog.timestamp >= since_time
        ).order_by(ActivityLog.timestamp.asc()).all()

        if not logs:
            return []

        timeline = []
        for log in logs:
            time_str = log.timestamp.strftime("%I:%M %p") if log.timestamp else "10:00 AM"
            timeline.append({
                "id": log.id,
                "time": time_str,
                "app": log.application_name,
                "title": log.window_title or log.application_name,
                "website_url": log.website_url or "",
                "category": log.category,
                "duration_secs": log.duration
            })

        return timeline

    def generate_daily_timeline(self, raw_logs: List[dict] = None) -> List[Dict[str, Any]]:
        """Fallback helper if raw logs list is passed directly."""
        if not raw_logs:
            return []

        timeline = []
        for log in raw_logs:
            timeline.append({
                "time": log.get("time_str", log.get("time", "09:00")),
                "app": log.get("application_name", log.get("app", "App")),
                "title": log.get("window_title", log.get("title", "Session")),
                "category": log.get("category", "Educational")
            })

        return timeline


timeline_engine = TimelineEngine()

