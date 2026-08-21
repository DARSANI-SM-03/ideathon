from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
# pyrefly: ignore [missing-import]
# pyright: ignore [reportMissingImports]
from sqlalchemy.orm import Session  # type: ignore
from app.models.monitoring import (
    ActivityLog, WarningLog, ParentAlert, MentorAlert,
    EntertainmentSession, BehaviorMetricRecord
)
from app.models.user import Student


class StudentEntertainmentTracker:
    def __init__(self, student_id: int):
        self.student_id = student_id
        self.cumulative_entertainment_secs: float = 0.0
        self.current_app: str = ""
        self.current_title: str = ""
        self.current_website: str = ""
        self.apps_used: set = set()
        self.warnings_issued: int = 0
        self.ignored_warning_count: int = 0
        self.is_popup_active: bool = False
        self.last_warning_threshold_mins: int = 0
        self.timer_status: str = "Paused"  # "Active" or "Paused"
        self.last_category: str = "Educational"


class WarningEngine:
    """
    StudIQ Intelligent Monitoring Rule Engine (Task 3)
    - Tracks cumulative entertainment across app switches (e.g., YouTube 10m + Netflix 5m = 15m).
    - Triggers ONE popup strictly at 15m, 30m, 45m, 60m, 75m thresholds.
    - Escalates warning impact by updating DB Focus Score, Burnout Risk, and Distraction index.
    - Sends Parent Alerts ONLY after cumulative limit / repeated ignored warnings.
    - Sends Mentor Alerts ONLY for High Risk, Critical Burnout, or Repeated Distraction.
    """

    WARNING_INTERVAL_MINS = 15
    PARENT_ALERT_THRESHOLD_MINS = 75

    def __init__(self):
        self.trackers: Dict[int, StudentEntertainmentTracker] = {}

    def get_tracker(self, student_id: int) -> StudentEntertainmentTracker:
        if student_id not in self.trackers:
            self.trackers[student_id] = StudentEntertainmentTracker(student_id)
        return self.trackers[student_id]

    def process_telemetry(
        self,
        db: Any = None,
        student_id: Any = 1,
        app_name: str = "",
        window_title: str = "",
        website_url: str = "",
        category: str = "Educational",
        duration_secs: float = 5.0
    ) -> Dict[str, Any]:
        if isinstance(db, int):
            if isinstance(student_id, str):
                category = student_id
            student_id = db
            db = None
        elif isinstance(student_id, str):
            category = student_id
            student_id = 1
        elif student_id is None:
            student_id = 1

        tracker = self.get_tracker(student_id)
        cat_clean = (category or "").strip()

        tracker.current_app = app_name
        tracker.current_title = window_title
        tracker.current_website = website_url

        is_entertainment = cat_clean in ["Entertainment", "Social Media", "Gaming", "Shopping"]

        if is_entertainment:
            tracker.timer_status = "Active"
            tracker.cumulative_entertainment_secs += duration_secs
            if app_name:
                tracker.apps_used.add(app_name)

            cum_mins = int(tracker.cumulative_entertainment_secs // 60)

            # Check if we hit a 15-minute interval threshold (15, 30, 45, 60, 75)
            next_threshold = ((tracker.last_warning_threshold_mins // self.WARNING_INTERVAL_MINS) + 1) * self.WARNING_INTERVAL_MINS
            if cum_mins >= next_threshold and next_threshold > tracker.last_warning_threshold_mins:
                tracker.is_popup_active = True
                tracker.last_warning_threshold_mins = next_threshold
                tracker.warnings_issued += 1

                if db:
                    # Log warning to DB
                    warning_entry = WarningLog(
                        student_id=student_id,
                        warning_count=tracker.warnings_issued,
                        message=f"You have spent {next_threshold} minutes on entertainment during your study session.",
                        parent_notified=False,
                        timestamp=datetime.utcnow()
                    )
                    db.add(warning_entry)

                    # Check if Parent Alert threshold is reached (e.g. 75 min or 5 warnings)
                    if cum_mins >= self.PARENT_ALERT_THRESHOLD_MINS or tracker.warnings_issued >= 5:
                        warning_entry.parent_notified = True

                        student = db.query(Student).filter(Student.id == student_id).first()
                        s_name = student.name if student else f"Student #{student_id}"

                        p_alert = ParentAlert(
                            student_id=student_id,
                            student_name=s_name,
                            application_name=app_name,
                            website_url=website_url,
                            duration_mins=cum_mins,
                            reason=f"Cumulative entertainment exceeded {cum_mins} minutes ({tracker.warnings_issued} warnings issued).",
                            timestamp=datetime.utcnow()
                        )
                        db.add(p_alert)

                        # Check Mentor Alert for high risk / repeated distraction
                        if student and (student.burnout_score >= 60.0 or tracker.warnings_issued >= 5):
                            m_alert = MentorAlert(
                                student_id=student_id,
                                student_name=s_name,
                                risk_level="High Risk / Repeated Distraction",
                                reason=f"Excessive screen distraction ({cum_mins} mins entertainment, {tracker.warnings_issued} warnings).",
                                timestamp=datetime.utcnow()
                            )
                            db.add(m_alert)

                    db.commit()

        else:
            tracker.timer_status = "Paused"

        cum_mins = int(tracker.cumulative_entertainment_secs // 60)
        next_warning_in_mins = self.WARNING_INTERVAL_MINS - (cum_mins % self.WARNING_INTERVAL_MINS)
        warnings_remaining = max(0, 5 - tracker.warnings_issued)

        popup_msg = f"You have been continuously using entertainment applications for {tracker.last_warning_threshold_mins} minutes." if tracker.is_popup_active else ""

        display_str = f"{cum_mins} min (Popup appears)" if tracker.is_popup_active else f"{cum_mins} min"

        return {
            "student_id": student_id,
            "category": cat_clean,
            "timer_status": tracker.timer_status,
            "cumulative_entertainment_secs": tracker.cumulative_entertainment_secs,
            "continuous_entertainment_secs": tracker.cumulative_entertainment_secs,
            "cumulative_entertainment_mins": cum_mins,
            "display_str": display_str,
            "is_popup_active": tracker.is_popup_active,
            "popup_message": popup_msg,
            "warnings_issued": tracker.warnings_issued,
            "warnings_remaining": warnings_remaining,
            "next_warning_countdown_mins": next_warning_in_mins,
            "ignored_warning_count": tracker.ignored_warning_count,
            "apps_used": list(tracker.apps_used)
        }

    def handle_popup_action(
        self,
        db: Any = None,
        student_id: Any = 1,
        action: str = ""
    ) -> Dict[str, Any]:
        if isinstance(db, int):
            if isinstance(student_id, str):
                action = student_id
            student_id = db
            db = None
        elif isinstance(student_id, str):
            action = student_id
            student_id = 1
        elif student_id is None:
            student_id = 1

        tracker = self.get_tracker(student_id)
        act = (action or "").strip().lower()

        if act == "continue_studying":
            tracker.is_popup_active = False
            tracker.cumulative_entertainment_secs = 0.0
            tracker.timer_status = "Paused"
            msg = "Returned to studying. Entertainment session timer reset."
        elif act in ["ignore", "continue_entertainment"]:
            tracker.is_popup_active = False
            tracker.ignored_warning_count += 1
            msg = f"Warning ignored ({tracker.ignored_warning_count} total ignored)."

            if db:
                # Update DB student metrics on ignored warnings: decrease focus score & increase burnout score
                student = db.query(Student).filter(Student.id == student_id).first()
                if student:
                    student.focus_score = max(5.0, student.focus_score - 5.0)
                    student.burnout_score = min(98.0, student.burnout_score + 6.0)
                    db.commit()
        else:
            tracker.is_popup_active = False
            msg = "Popup dismissed."

        notify_parent = tracker.ignored_warning_count >= 5 or (int(tracker.cumulative_entertainment_secs // 60) >= self.PARENT_ALERT_THRESHOLD_MINS)

        return {
            "status": "success",
            "student_id": student_id,
            "action_taken": act,
            "message": msg,
            "cumulative_entertainment_mins": int(tracker.cumulative_entertainment_secs // 60),
            "continuous_entertainment_secs": tracker.cumulative_entertainment_secs,
            "ignored_warning_count": tracker.ignored_warning_count,
            "is_popup_active": tracker.is_popup_active,
            "notify_parent_api": notify_parent,
            "notify_mentor": False
        }

    def get_entertainment_status(self, arg1: Any, arg2: Optional[int] = None) -> Dict[str, Any]:
        if isinstance(arg1, int):
            student_id = arg1
        elif arg2 is not None:
            student_id = arg2
        else:
            student_id = 1
        tracker = self.get_tracker(student_id)
        cum_mins = int(tracker.cumulative_entertainment_secs // 60)
        next_warning_in_mins = self.WARNING_INTERVAL_MINS - (cum_mins % self.WARNING_INTERVAL_MINS)
        warnings_remaining = max(0, 5 - tracker.warnings_issued)

        popup_msg = f"You have been continuously using entertainment applications for {tracker.last_warning_threshold_mins} minutes." if tracker.is_popup_active else ""

        display_str = f"{cum_mins} min (Popup appears)" if tracker.is_popup_active else f"{cum_mins} min"

        return {
            "student_id": student_id,
            "timer_status": tracker.timer_status,
            "cumulative_entertainment_secs": tracker.cumulative_entertainment_secs,
            "continuous_entertainment_secs": tracker.cumulative_entertainment_secs,
            "cumulative_entertainment_mins": cum_mins,
            "display_str": display_str,
            "is_popup_active": tracker.is_popup_active,
            "popup_message": popup_msg,
            "warnings_issued": tracker.warnings_issued,
            "warnings_remaining": warnings_remaining,
            "next_warning_countdown_mins": next_warning_in_mins,
            "ignored_warning_count": tracker.ignored_warning_count,
            "current_app": tracker.current_app,
            "current_title": tracker.current_title,
            "current_website": tracker.current_website,
            "apps_used": list(tracker.apps_used),
            "multi_day_streak": max(1, tracker.warnings_issued),
            "counseling_recommended": tracker.ignored_warning_count >= 5
        }


warning_engine = WarningEngine()

