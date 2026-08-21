from typing import List, Dict, Any, Optional
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.monitoring import ActivityLog


class FocusEngine:
    """
    Explainable Focus Engine: Computes a student's Focus Score (0-100) from real
    Desktop Agent telemetry stored in the database.

    Evaluates:
    - Educational duration
    - Productive duration
    - Entertainment duration
    - Gaming duration
    - Idle Time
    - Task Switching Frequency
    - Continuous Study Sessions
    """

    def calculate_focus_from_telemetry(
        self,
        db: Session,
        student_id: int = 1,
        hours_lookback: float = 24.0
    ) -> Dict[str, Any]:
        since_time = datetime.utcnow() - timedelta(hours=hours_lookback)
        logs = db.query(ActivityLog).filter(
            ActivityLog.student_id == student_id,
            ActivityLog.timestamp >= since_time
        ).order_by(ActivityLog.timestamp.asc()).all()

        if not logs:
            # Baseline when no telemetry is present yet today
            return {
                "focus_score": 85.0,
                "confidence": 90.0,
                "explanation": ["Initial baseline active session. Awaiting active Desktop Agent telemetry."]
            }

        edu_secs = sum(l.duration for l in logs if l.category == "Educational")
        prod_secs = sum(l.duration for l in logs if l.category == "Productive")
        ent_secs = sum(l.duration for l in logs if l.category in ["Entertainment", "Social Media"])
        game_secs = sum(l.duration for l in logs if l.category in ["Gaming", "Shopping"])
        idle_secs = sum(l.duration for l in logs if l.category == "Idle")

        # Task Switching Frequency
        task_switches = 0
        last_cat = None
        for l in logs:
            if last_cat and l.category != last_cat:
                task_switches += 1
            last_cat = l.category

        # Continuous Study Sessions (uninterrupted Educational/Productive sessions >= 15 mins)
        continuous_sessions = 0
        current_study_secs = 0
        for l in logs:
            if l.category in ["Educational", "Productive"]:
                current_study_secs += l.duration
                if current_study_secs >= 900:  # 15 mins
                    continuous_sessions += 1
            else:
                current_study_secs = 0

        return self.calculate_explainable_focus(
            educational_time_mins=int(edu_secs // 60),
            productive_time_mins=int(prod_secs // 60),
            entertainment_time_mins=int(ent_secs // 60),
            gaming_time_mins=int(game_secs // 60),
            idle_time_mins=int(idle_secs // 60),
            task_switching_count=task_switches,
            continuous_study_sessions=continuous_sessions
        )

    def compute_focus_score(self, activity_list: List[dict]) -> float:
        """Backward compatibility helper for activity lists."""
        edu_mins = sum(a.get("duration", 0) for a in activity_list if a.get("category") in ["Educational", "Study"]) // 60
        prod_mins = sum(a.get("duration", 0) for a in activity_list if a.get("category") in ["Productive", "Coding"]) // 60
        ent_mins = sum(a.get("duration", 0) for a in activity_list if a.get("category") in ["Entertainment", "Social Media"]) // 60
        game_mins = sum(a.get("duration", 0) for a in activity_list if a.get("category") in ["Gaming"]) // 60

        res = self.calculate_explainable_focus(
            educational_time_mins=edu_mins,
            productive_time_mins=prod_mins,
            entertainment_time_mins=ent_mins,
            gaming_time_mins=game_mins
        )
        return res["focus_score"]

    def calculate_explainable_focus(
        self,
        attendance: float = 90.0,
        assignment_completion_pct: float = 85.0,
        avg_quiz_score: float = 88.0,
        cgpa: float = 3.8,
        productive_time_mins: int = 60,
        educational_time_mins: int = 120,
        entertainment_time_mins: int = 15,
        gaming_time_mins: int = 0,
        idle_time_mins: int = 0,
        task_switching_count: int = 3,
        continuous_study_sessions: int = 2,
        is_study_mode_active: bool = False
    ) -> Dict[str, Any]:
        explanation = []

        # Positive time points
        study_points = (educational_time_mins * 0.4) + (productive_time_mins * 0.3)
        session_bonus = min(20.0, continuous_study_sessions * 5.0)

        # Distraction penalties
        ent_penalty = (entertainment_time_mins * 0.5) + (gaming_time_mins * 0.8)
        task_switch_penalty = min(15.0, max(0, task_switching_count - 5) * 1.5)
        idle_penalty = min(10.0, (idle_time_mins / 30.0) * 5.0)

        # Calculate base focus score (0-100)
        total_time_mins = max(1, educational_time_mins + productive_time_mins + entertainment_time_mins + gaming_time_mins)
        academic_ratio = ((educational_time_mins + productive_time_mins) / total_time_mins) * 100.0

        raw_score = 65.0 + (academic_ratio * 0.3) + session_bonus - ent_penalty - task_switch_penalty - idle_penalty

        if is_study_mode_active:
            raw_score += 5.0
            explanation.append("Study Mode Active (+5% focus boost for scheduled deep study).")

        if academic_ratio >= 75.0:
            explanation.append(f"High educational/productive usage ({round(academic_ratio)}% of screen time).")
        elif academic_ratio < 40.0:
            explanation.append(f"Low educational ratio ({round(academic_ratio)}%). Entertainment time is suppressing focus.")

        if continuous_study_sessions >= 2:
            explanation.append(f"Strong continuous study discipline ({continuous_study_sessions} deep focus blocks).")

        if task_switch_penalty > 0:
            explanation.append(f"Frequent context switching penalty ({task_switching_count} app switches detected).")

        if entertainment_time_mins > 45:
            explanation.append(f"High entertainment time today ({entertainment_time_mins} mins).")

        focus_score = round(float(np.clip(raw_score, 5.0, 99.0)), 1)
        confidence = 95.0

        return {
            "focus_score": focus_score,
            "confidence": confidence,
            "explanation": explanation
        }


focus_engine = FocusEngine()

