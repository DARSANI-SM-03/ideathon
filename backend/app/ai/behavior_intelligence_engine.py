from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import numpy as np
from sqlalchemy.orm import Session
from app.models.monitoring import ActivityLog, BehaviorMetricRecord
from app.models.user import Student
from app.ai.behavior_engine import behavior_engine


class BehaviorIntelligenceEngine:
    """
    Real AI Behavior Intelligence Engine:
    Calculates dynamic metrics strictly from 5-second Desktop Agent telemetry
    persisted in SQLite database.

    Metrics computed:
    1. Focus Score (0 - 100)
    2. Burnout Score (0 - 100%) & Risk Level (Low, Medium, High, Critical)
    3. Digital Wellness Score (0 - 100)
    4. Productivity Score (0 - 100) & Category Breakdown (%)
    5. Study Consistency (Daily, Weekly, Streak, Avg Session Length)
    6. Live Activity Status
    """

    def evaluate_student_telemetry(
        self,
        db: Session,
        student_id: int = 1,
        hours_lookback: float = 24.0,
        persist_snapshot: bool = True
    ) -> Dict[str, Any]:
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        since_time = now - timedelta(hours=hours_lookback)
        since_week = now - timedelta(days=7)

        # 1. Fetch Telemetry Logs from SQLite
        today_logs = db.query(ActivityLog).filter(
            ActivityLog.student_id == student_id,
            ActivityLog.timestamp >= today_start
        ).order_by(ActivityLog.timestamp.asc()).all()

        week_logs = db.query(ActivityLog).filter(
            ActivityLog.student_id == student_id,
            ActivityLog.timestamp >= since_week
        ).order_by(ActivityLog.timestamp.asc()).all()

        lookback_logs = db.query(ActivityLog).filter(
            ActivityLog.student_id == student_id,
            ActivityLog.timestamp >= since_time
        ).order_by(ActivityLog.timestamp.asc()).all()

        active_logs = today_logs if today_logs else lookback_logs

        # Categorized Durations (Seconds)
        edu_secs = sum(l.duration for l in active_logs if l.category == "Educational")
        prod_secs = sum(l.duration for l in active_logs if l.category == "Productive")
        util_secs = sum(l.duration for l in active_logs if l.category == "Utilities")
        ent_secs = sum(l.duration for l in active_logs if l.category in ["Entertainment", "Social Media", "Shopping"])
        game_secs = sum(l.duration for l in active_logs if l.category == "Gaming")
        idle_secs = sum(l.duration for l in active_logs if l.category == "Idle")

        total_secs = max(1, edu_secs + prod_secs + util_secs + ent_secs + game_secs + idle_secs)
        edu_mins = edu_secs / 60.0
        prod_mins = prod_secs / 60.0
        util_mins = util_secs / 60.0
        ent_mins = ent_secs / 60.0
        game_mins = game_secs / 60.0
        idle_mins = idle_secs / 60.0

        # Uninterrupted study blocks (>= 15 mins = 900s) & breaks (>= 5 mins gap)
        uninterrupted_sessions = 0
        current_study_secs = 0
        study_session_durations = []
        breaks_count = 0
        last_log_time = None
        task_switches = 0
        last_cat = None

        for l in active_logs:
            if last_cat and l.category != last_cat:
                task_switches += 1
            last_cat = l.category

            if last_log_time:
                gap = (l.timestamp - last_log_time).total_seconds()
                if gap >= 300:
                    breaks_count += 1

            if l.category in ["Educational", "Productive"]:
                current_study_secs += l.duration
                if current_study_secs >= 900:
                    uninterrupted_sessions += 1
            else:
                if current_study_secs >= 600:
                    study_session_durations.append(current_study_secs / 60.0)
                current_study_secs = 0

            last_log_time = l.timestamp

        if current_study_secs >= 600:
            study_session_durations.append(current_study_secs / 60.0)

        # -------------------------------------------------------------
        # A. FOCUS SCORE CALCULATION (0 - 100)
        # -------------------------------------------------------------
        positive_points = (edu_mins * 0.5) + (prod_mins * 0.4) + min(20.0, uninterrupted_sessions * 5.0)
        distraction_penalty = (ent_mins * 0.6) + (game_mins * 1.0) + min(15.0, max(0, task_switches - 5) * 1.2) + min(15.0, idle_mins * 0.3)
        academic_ratio = ((edu_secs + prod_secs) / total_secs) * 100.0

        raw_focus = 60.0 + (academic_ratio * 0.3) + positive_points - distraction_penalty
        focus_score = round(float(np.clip(raw_focus, 5.0, 99.0)), 1)

        # -------------------------------------------------------------
        # B. BURNOUT SCORE (0 - 100%) & RISK LEVEL
        # -------------------------------------------------------------
        daily_study_hours = (edu_secs + prod_secs) / 3600.0
        max_continuous_study_hours = max([d / 60.0 for d in study_session_durations], default=0.0)

        # Late night usage past 11 PM (23:00 - 05:00)
        late_night_secs = sum(l.duration for l in active_logs if l.timestamp.hour >= 23 or l.timestamp.hour < 5)
        late_night_hours = late_night_secs / 3600.0

        # Weekly average daily hours
        weekly_study_secs = sum(l.duration for l in week_logs if l.category in ["Educational", "Productive"])
        weekly_daily_avg_hours = (weekly_study_secs / 3600.0) / 7.0

        burnout_points = 10.0
        burnout_reasons = []

        if max_continuous_study_hours >= 3.0:
            burnout_points += (max_continuous_study_hours - 1.5) * 15.0
            burnout_reasons.append(f"Continuous study duration reached {round(max_continuous_study_hours, 1)} hrs without adequate breaks.")
        elif max_continuous_study_hours >= 2.0:
            burnout_points += 10.0
            burnout_reasons.append(f"Extended uninterrupted study block ({round(max_continuous_study_hours, 1)} hrs).")

        if breaks_count <= 1 and daily_study_hours >= 3.0:
            burnout_points += 15.0
            burnout_reasons.append(f"Insufficient break frequency ({breaks_count} breaks logged today).")

        if late_night_hours >= 0.5:
            burnout_points += late_night_hours * 20.0
            burnout_reasons.append(f"Late night screen activity ({round(late_night_hours, 1)} hrs after 11 PM).")

        if daily_study_hours >= 7.0:
            burnout_points += 15.0
            burnout_reasons.append(f"Heavy daily study workload ({round(daily_study_hours, 1)} hrs).")

        if daily_study_hours > (weekly_daily_avg_hours * 1.4) and daily_study_hours >= 5.0:
            burnout_points += 12.0
            burnout_reasons.append(f"Workload spike {round((daily_study_hours / max(0.1, weekly_daily_avg_hours) - 1) * 100)}% above 7-day average.")

        if task_switches >= 15:
            burnout_points += 10.0
            burnout_reasons.append(f"Frequent task switching context fatigue ({task_switches} switches).")

        burnout_score = round(float(np.clip(burnout_points, 5.0, 98.0)), 1)
        if burnout_score <= 30.0:
            burnout_level = "Low"
        elif burnout_score <= 60.0:
            burnout_level = "Medium"
        elif burnout_score <= 80.0:
            burnout_level = "High"
        else:
            burnout_level = "Critical"

        # -------------------------------------------------------------
        # C. DIGITAL WELLNESS SCORE (0 - 100)
        # -------------------------------------------------------------
        break_subscore = max(0.0, 100.0 - (15.0 if (breaks_count == 0 and daily_study_hours >= 2.0) else 0.0))
        ent_mod_subscore = max(0.0, 100.0 - (ent_mins + game_mins) * 0.5)
        sleep_subscore = max(0.0, 100.0 - (late_night_hours * 40.0))
        idle_subscore = max(0.0, 100.0 - min(50.0, idle_mins * 1.0))

        wellness_score = round(float(np.clip(
            (break_subscore * 0.3) + (ent_mod_subscore * 0.3) + (sleep_subscore * 0.3) + (idle_subscore * 0.1),
            0.0, 100.0
        )), 1)

        # -------------------------------------------------------------
        # D. PRODUCTIVITY SCORE & CATEGORY CONTRIBUTIONS (%)
        # -------------------------------------------------------------
        active_screen_secs = max(1, edu_secs + prod_secs + util_secs + ent_secs + game_secs)
        edu_pct = round((edu_secs / active_screen_secs) * 100.0, 1)
        prod_pct = round((prod_secs / active_screen_secs) * 100.0, 1)
        util_pct = round((util_secs / active_screen_secs) * 100.0, 1)
        ent_pct = round((ent_secs / active_screen_secs) * 100.0, 1)
        game_pct = round((game_secs / active_screen_secs) * 100.0, 1)

        prod_score_val = (edu_pct * 1.0) + (prod_pct * 0.9) + (util_pct * 0.5) - ((ent_pct + game_pct) * 0.5)
        productivity_score = round(float(np.clip(prod_score_val, 0.0, 100.0)), 1)

        # -------------------------------------------------------------
        # E. STUDY CONSISTENCY METRICS
        # -------------------------------------------------------------
        daily_target_hours = 4.0
        daily_consistency_pct = round(min(100.0, (daily_study_hours / daily_target_hours) * 100.0), 1)

        # Calculate 7-day consistency & streak
        past_7_days_study = {}
        for i in range(7):
            d_start = today_start - timedelta(days=i)
            d_end = d_start + timedelta(days=1)
            day_secs = sum(l.duration for l in week_logs if d_start <= l.timestamp < d_end and l.category in ["Educational", "Productive"])
            past_7_days_study[i] = day_secs / 3600.0

        days_met = sum(1 for d_hrs in past_7_days_study.values() if d_hrs >= 2.0)
        weekly_consistency_pct = round((days_met / 7.0) * 100.0, 1)

        streak_days = 0
        for i in range(7):
            if past_7_days_study.get(i, 0.0) >= 1.5:
                streak_days += 1
            else:
                break

        avg_session_len_mins = round(float(np.mean(study_session_durations)) if study_session_durations else round(daily_study_hours * 60 / max(1, uninterrupted_sessions + 1), 1), 1)

        # -------------------------------------------------------------
        # F. LIVE ACTIVITY STATUS
        # -------------------------------------------------------------
        latest_log = active_logs[-1] if active_logs else None
        current_app = latest_log.application_name if latest_log else "Desktop Agent Standing By"
        current_title = latest_log.window_title if latest_log and latest_log.window_title else current_app
        current_website = latest_log.website_url if latest_log and latest_log.website_url else ""
        current_category = latest_log.category if latest_log else "Productive"

        session_mins = int((today_logs[-1].timestamp - today_logs[0].timestamp).total_seconds() // 60) if len(today_logs) > 1 else 15

        if focus_score >= 80.0:
            current_focus_state = "Deep Flow State 🟢"
        elif focus_score >= 60.0:
            current_focus_state = "Active Study Session 🟢"
        elif focus_score >= 40.0:
            current_focus_state = "Distraction Alert 🟡"
        else:
            current_focus_state = "Fatigue & Heavy Distraction 🔴"

        # Update Student Table
        student = db.query(Student).filter(Student.id == student_id).first()
        if student:
            student.focus_score = focus_score
            student.burnout_score = burnout_score
            db.commit()

        # Persist DB Snapshot
        if persist_snapshot:
            snapshot = BehaviorMetricRecord(
                student_id=student_id,
                focus_score=focus_score,
                burnout_score=burnout_score,
                burnout_level=burnout_level,
                digital_wellness_score=wellness_score,
                productivity_score=productivity_score,
                daily_consistency_pct=daily_consistency_pct,
                weekly_consistency_pct=weekly_consistency_pct,
                study_streak_days=streak_days,
                avg_session_length_mins=avg_session_len_mins,
                educational_pct=edu_pct,
                productive_pct=prod_pct,
                utilities_pct=util_pct,
                entertainment_pct=ent_pct,
                gaming_pct=game_pct,
                timestamp=now
            )
            db.add(snapshot)
            db.commit()

        return {
            "student_id": student_id,
            "focus_score": focus_score,
            "burnout_score": burnout_score,
            "burnout_level": burnout_level,
            "burnout_probability_pct": burnout_score,
            "digital_wellness_score": wellness_score,
            "productivity_score": productivity_score,
            "focus_breakdown": {
                "educational_hours": round(edu_mins / 60.0, 2),
                "productive_hours": round(prod_mins / 60.0, 2),
                "entertainment_hours": round(ent_mins / 60.0, 2),
                "idle_mins": round(idle_mins, 1),
                "app_switches_count": task_switches,
                "positive_points": round(positive_points, 1),
                "distraction_penalty": round(distraction_penalty, 1),
                "academic_ratio_pct": round(academic_ratio, 1),
                "formula_str": "Focus Score = 60 + (Academic Ratio * 0.3) + (Edu + Prod Boost) - (Ent + Gaming + Switches Penalties)"
            },
            "burnout_breakdown": {
                "continuous_usage_hours": round(max_continuous_study_hours, 2),
                "late_night_hours": round(late_night_hours, 2),
                "daily_study_hours": round(daily_study_hours, 2),
                "breaks_count": breaks_count,
                "entertainment_hours": round(ent_mins / 60.0, 2),
                "gaming_hours": round(game_mins / 60.0, 2),
                "factors": burnout_reasons if burnout_reasons else ["Balanced study pace & break frequency."]
            },
            "category_contributions": {
                "educational_pct": edu_pct,
                "productive_pct": prod_pct,
                "utilities_pct": util_pct,
                "entertainment_pct": ent_pct,
                "gaming_pct": game_pct
            },
            "study_consistency": {
                "daily_consistency_pct": daily_consistency_pct,
                "weekly_consistency_pct": weekly_consistency_pct,
                "study_streak_days": streak_days,
                "avg_session_length_mins": avg_session_len_mins
            },
            "live_activity": {
                "current_application": current_app,
                "current_window_title": current_title,
                "current_website": current_website,
                "current_category": current_category,
                "session_duration_mins": session_mins,
                "current_focus_state": current_focus_state,
                "monitoring_status": "Active"
            },
            "burnout_reasons": burnout_reasons if burnout_reasons else ["Healthy break discipline & study pace."]
        }



behavior_intelligence_engine = BehaviorIntelligenceEngine()
