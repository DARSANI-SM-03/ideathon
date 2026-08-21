from typing import List, Dict, Any, Optional
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.monitoring import ActivityLog


class BurnoutEngine:
    """
    Explainable Burnout Engine: Predicts student Burnout Risk % and Risk Level (Low, Moderate, High, Critical)
    from real Desktop Agent telemetry stored in the database.

    Evaluates:
    - Continuous study hours
    - Number of breaks
    - Long continuous sessions
    - Night usage (past 11 PM)
    - Daily study duration
    - Weekly study trend
    - Task switching
    - Idle behavior
    """

    def calculate_burnout_from_telemetry(
        self,
        db: Session,
        student_id: int = 1,
        hours_lookback: float = 24.0
    ) -> Dict[str, Any]:
        now = datetime.utcnow()
        since_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        since_week = now - timedelta(days=7)

        today_logs = db.query(ActivityLog).filter(
            ActivityLog.student_id == student_id,
            ActivityLog.timestamp >= since_today
        ).order_by(ActivityLog.timestamp.asc()).all()

        week_logs = db.query(ActivityLog).filter(
            ActivityLog.student_id == student_id,
            ActivityLog.timestamp >= since_week
        ).all()

        if not today_logs:
            return {
                "burnout_score": 15.0,
                "risk_level": "Low",
                "reasons": ["Low risk because:", "• Optimal study routine. Healthy breaks & low fatigue."]
            }

        # 1. Daily & Continuous Study Hours
        study_logs = [l for l in today_logs if l.category in ["Educational", "Productive"]]
        daily_study_secs = sum(l.duration for l in study_logs)
        daily_study_hours = daily_study_secs / 3600.0

        # Longest continuous study session without a 5+ min break
        max_continuous_secs = 0
        current_continuous_secs = 0
        breaks_count = 0
        last_log_time = None

        for l in today_logs:
            if last_log_time:
                gap_secs = (l.timestamp - last_log_time).total_seconds()
                if gap_secs >= 300:  # 5 minutes break
                    breaks_count += 1

            if l.category in ["Educational", "Productive"]:
                current_continuous_secs += l.duration
                if current_continuous_secs > max_continuous_secs:
                    max_continuous_secs = current_continuous_secs
            else:
                current_continuous_secs = 0

            last_log_time = l.timestamp

        continuous_study_hours = max_continuous_secs / 3600.0

        # 2. Night Usage (11 PM - 5 AM)
        late_night_secs = sum(
            l.duration for l in today_logs
            if l.timestamp.hour >= 23 or l.timestamp.hour < 5
        )
        late_night_hours = late_night_secs / 3600.0

        # 3. Weekly Study Trend
        weekly_study_hours = sum(
            l.duration for l in week_logs
            if l.category in ["Educational", "Productive"]
        ) / 3600.0
        weekly_avg_daily_hours = weekly_study_hours / 7.0

        # 4. Task Switching Count
        task_switches = 0
        last_cat = None
        for l in today_logs:
            if last_cat and l.category != last_cat:
                task_switches += 1
            last_cat = l.category

        return self.calculate_explainable_burnout(
            continuous_study_hours=continuous_study_hours,
            breaks_count=breaks_count,
            late_night_hours=late_night_hours,
            daily_study_hours=daily_study_hours,
            weekly_avg_daily_hours=weekly_avg_daily_hours,
            task_switching_count=task_switches
        )

    def calculate_burnout_score(self, focus_score: float, attendance: float, avg_quiz: float, night_hours: float, daily_study_hours: float) -> float:
        """Backward compatibility helper for student_service."""
        res = self.calculate_explainable_burnout(
            late_night_hours=night_hours,
            daily_study_hours=daily_study_hours
        )
        return res["burnout_score"]

    def calculate_explainable_burnout(
        self,
        continuous_study_hours: float = 2.0,
        breaks_count: int = 3,
        late_night_hours: float = 0.0,
        daily_study_hours: float = 5.0,
        weekly_avg_daily_hours: float = 4.5,
        task_switching_count: int = 5
    ) -> Dict[str, Any]:
        risk_points = 10.0  # Baseline
        reasons = []

        # Continuous Study Factor
        if continuous_study_hours >= 4.0:
            points = (continuous_study_hours - 2.0) * 12.0
            risk_points += points
            reasons.append(f"• {round(continuous_study_hours, 1)} hours continuous study without sufficient rest")
        elif continuous_study_hours >= 2.5:
            risk_points += 10.0
            reasons.append(f"• Prolonged continuous study session ({round(continuous_study_hours, 1)} hrs)")

        # Breaks Factor
        if breaks_count <= 1 and daily_study_hours >= 3.0:
            risk_points += 15.0
            reasons.append(f"• Only {breaks_count} movement break taken today")

        # Night Usage Factor (past 11 PM)
        if late_night_hours >= 0.5:
            points = late_night_hours * 15.0
            risk_points += points
            reasons.append(f"• {round(late_night_hours, 1)} hours late night screen usage after 11 PM")

        # Daily Study Duration Factor
        if daily_study_hours >= 8.0:
            risk_points += 20.0
            reasons.append(f"• High daily study workload ({round(daily_study_hours, 1)} hrs total)")

        # Weekly Trend Spike
        if daily_study_hours > (weekly_avg_daily_hours * 1.5) and daily_study_hours >= 6.0:
            risk_points += 12.0
            reasons.append(f"• Study workload spiked {round((daily_study_hours / max(0.1, weekly_avg_daily_hours) - 1) * 100)}% above weekly average")

        # Task Switching Context Fatigue
        if task_switching_count >= 15:
            risk_points += 10.0
            reasons.append(f"• Frequent context switching ({task_switching_count} app switches)")

        burnout_score = round(float(np.clip(risk_points, 5.0, 98.0)), 1)
        risk_level = self.get_risk_level(burnout_score)

        header_reason = f"{risk_level} risk because:" if reasons else "Low risk because:"
        full_reasons = [header_reason] + (reasons if reasons else ["• Healthy break discipline & study pace."])

        return {
            "burnout_score": burnout_score,
            "risk_level": risk_level,
            "reasons": full_reasons
        }

    def get_risk_level(self, score: float) -> str:
        if score <= 30.0:
            return "Low"
        elif score <= 60.0:
            return "Moderate"
        elif score <= 80.0:
            return "High"
        else:
            return "Critical"


burnout_engine = BurnoutEngine()

