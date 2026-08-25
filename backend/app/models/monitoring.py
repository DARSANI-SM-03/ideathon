from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.base import Base

class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    application_name = Column(String, nullable=False)
    window_title = Column(String, nullable=True)
    website_url = Column(String, nullable=True)
    category = Column(String, nullable=False)  # Educational, Productive, Neutral, Entertainment, Gaming
    confidence = Column(Float, default=0.95)
    duration = Column(Integer, default=3)  # in seconds
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

class FocusScore(Base):
    __tablename__ = "focus_scores"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    score = Column(Float, nullable=False)
    calculated_at = Column(DateTime, default=datetime.utcnow)

class BurnoutPrediction(Base):
    __tablename__ = "burnout_predictions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    risk_level = Column(String, nullable=False)  # Low, Medium, High, Critical
    confidence = Column(Float, default=95.0)
    recommendation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class MonitoringLog(Base):
    __tablename__ = "monitoring_logs"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    process_name = Column(String, nullable=False)
    application_name = Column(String, nullable=False)
    window_title = Column(String, nullable=True)
    category = Column(String, nullable=False)
    duration = Column(Integer, default=3)
    session_time = Column(Integer, default=0)
    is_whitelisted = Column(Boolean, default=False)
    is_study_mode = Column(Boolean, default=False)

class ParentWhitelist(Base):
    __tablename__ = "parent_whitelists"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    application_name = Column(String, nullable=False)
    allowed_category = Column(String, default="Educational")
    created_at = Column(DateTime, default=datetime.utcnow)

class StudyModeConfig(Base):
    __tablename__ = "study_mode_configs"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    start_hour = Column(Integer, default=19)
    end_hour = Column(Integer, default=22)
    is_active = Column(Boolean, default=True)

class WarningLog(Base):
    __tablename__ = "warning_logs"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    warning_count = Column(Integer, default=1)
    message = Column(Text, nullable=False)
    parent_notified = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

class AITimelineEvent(Base):
    __tablename__ = "ai_timeline_events"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    time_str = Column(String, nullable=False)
    application_name = Column(String, nullable=False)
    window_title = Column(String, nullable=True)
    category = Column(String, nullable=False)
    duration_mins = Column(Integer, default=15)
    timestamp = Column(DateTime, default=datetime.utcnow)

class BehaviorMetricRecord(Base):
    __tablename__ = "behavior_metric_records"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    focus_score = Column(Float, nullable=False)
    burnout_score = Column(Float, nullable=False)
    burnout_level = Column(String, nullable=False)  # Low, Medium, High, Critical
    digital_wellness_score = Column(Float, nullable=False)
    productivity_score = Column(Float, nullable=False)
    daily_consistency_pct = Column(Float, nullable=False)
    weekly_consistency_pct = Column(Float, nullable=False)
    study_streak_days = Column(Integer, default=0)
    avg_session_length_mins = Column(Float, default=0.0)
    educational_pct = Column(Float, default=0.0)
    productive_pct = Column(Float, default=0.0)
    utilities_pct = Column(Float, default=0.0)
    entertainment_pct = Column(Float, default=0.0)
    gaming_pct = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

class EntertainmentSession(Base):

    __tablename__ = "entertainment_sessions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    apps_used = Column(Text, nullable=False)
    cumulative_secs = Column(Float, default=0.0)
    warnings_issued = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)

class ParentAlert(Base):
    __tablename__ = "parent_alerts"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    student_name = Column(String, nullable=False)
    application_name = Column(String, nullable=False)
    website_url = Column(String, nullable=True)
    duration_mins = Column(Integer, default=0)
    reason = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

class MentorAlert(Base):
    __tablename__ = "mentor_alerts"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    student_name = Column(String, nullable=False)
    risk_level = Column(String, nullable=False)  # High Risk, Critical Burnout, Repeated Distraction
    reason = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

class SessionSummary(Base):
    __tablename__ = "session_summaries"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    educational_mins = Column(Integer, default=0)
    productive_mins = Column(Integer, default=0)
    entertainment_mins = Column(Integer, default=0)
    gaming_mins = Column(Integer, default=0)
    total_study_hours = Column(Float, default=0.0)
    total_entertainment_hours = Column(Float, default=0.0)
    date_str = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class AIPrediction(Base):
    __tablename__ = "ai_predictions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    burnout_risk_level = Column(String, nullable=False)  # Very Low, Low, Medium, High, Critical
    burnout_probability_pct = Column(Float, nullable=False)
    focus_decline_risk = Column(String, nullable=False)
    distraction_risk = Column(String, nullable=False)
    consistency_risk = Column(String, nullable=False)
    detected_patterns = Column(Text, nullable=False)  # JSON text
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

class AIRecommendation(Base):
    __tablename__ = "ai_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    recommendations = Column(Text, nullable=False)  # JSON text
    target_persona = Column(String, default="Student")  # Student, Parent, Mentor
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

class HistoricalTrendSummary(Base):
    __tablename__ = "historical_trend_summaries"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    period_days = Column(Integer, default=7)  # 7, 30, 90
    avg_focus = Column(Float, default=80.0)
    avg_burnout = Column(Float, default=20.0)
    study_trend = Column(String, default="Stable")
    entertainment_trend = Column(String, default="Stable")
    positive_improvements = Column(Text, nullable=True)  # JSON text
    areas_of_concern = Column(Text, nullable=True)  # JSON text
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

class StudentSettings(Base):
    __tablename__ = "student_settings"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, unique=True)
    theme = Column(String, default="dark")
    daily_study_target_mins = Column(Integer, default=240)
    daily_entertainment_limit_mins = Column(Integer, default=60)
    pomodoro_focus_mins = Column(Integer, default=50)
    pomodoro_break_mins = Column(Integer, default=10)
    idle_threshold_secs = Column(Integer, default=300)
    notifications_enabled = Column(Boolean, default=True)
    sound_alerts_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class StudySession(Base):
    __tablename__ = "study_sessions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    session_type = Column(String, default="Pomodoro")  # Pomodoro, Deep Work, Free Study
    planned_duration_mins = Column(Integer, default=50)
    actual_duration_secs = Column(Integer, default=0)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    completed = Column(Boolean, default=False)
    focus_score = Column(Float, default=85.0)
    created_at = Column(DateTime, default=datetime.utcnow)




