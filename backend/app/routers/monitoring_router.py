from fastapi import APIRouter, Depends, HTTPException, Body  # type: ignore
from sqlalchemy.orm import Session  # type: ignore
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import func  # type: ignore
from app.database.session import get_db
from app.monitoring.windows_service import windows_monitor
from app.ai.behavior_engine import behavior_engine
from app.ai.focus_engine import focus_engine
from app.ai.burnout_engine import burnout_engine
from app.ai.warning_engine import warning_engine
from app.ai.timeline_engine import timeline_engine
from app.ai.replay_engine import replay_engine
from app.ai.recommendation_engine import recommendation_engine
from app.ai.central_metrics_engine import central_metrics_engine
from app.models.monitoring import ParentWhitelist, StudyModeConfig, WarningLog, AITimelineEvent, ActivityLog, ParentAlert, MentorAlert

from app.auth.security import create_agent_token, decode_agent_token
from app.auth.dependencies import get_current_user, get_current_user_optional

router = APIRouter(prefix="/monitoring", tags=["Monitoring & Explainable AI"])

# Global state to track last desktop agent ping
last_agent_ping_time: Optional[float] = None
last_telemetry_payload: Optional[Dict[str, Any]] = None

@router.post("/agent/session")
def create_agent_session(current_user: dict = Depends(get_current_user)):
    """
    Generates a short-lived, scoped agent token for the logged in student.
    """
    student_id = current_user.get("id", 1)
    student_code = current_user.get("user_identifier", "STU-2026-001")
    token = create_agent_token({"student_id": student_id, "student_code": student_code, "scope": "telemetry"})
    return {
        "status": "success",
        "agent_token": token,
        "student_id": student_id,
        "student_code": student_code,
        "expires_in_hours": 24
    }

@router.get("/installer/download")
def download_desktop_agent_installer():
    """
    Serves the packaged StudIQ Desktop Agent 1-click Windows installer script (StudIQAgentSetup.bat).
    """
    from fastapi.responses import FileResponse
    import os
    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    installer_bat = os.path.join(backend_dir, "desktop_agent", "installer", "StudIQAgentSetup.bat")
    
    if os.path.exists(installer_bat):
        file_size = os.path.getsize(installer_bat)
        return FileResponse(
            installer_bat,
            filename="StudIQAgentSetup.bat",
            media_type="application/x-msdos-program",
            headers={
                "Content-Disposition": 'attachment; filename="StudIQAgentSetup.bat"',
                "Content-Length": str(file_size)
            }
        )
    raise HTTPException(status_code=404, detail="StudIQ Agent setup installer script not found on server.")

@router.get("/health")
def get_monitoring_health():
    """
    Returns system monitoring health, last agent heartbeat delta, and telemetry status.
    """
    import time
    global last_agent_ping_time, last_telemetry_payload
    is_active = False
    ping_delta = None
    if last_agent_ping_time:
        ping_delta = round(time.time() - last_agent_ping_time, 1)
        if ping_delta < 30.0:
            is_active = True

    return {
        "status": "healthy",
        "agent_connected": is_active,
        "last_ping_seconds_ago": ping_delta,
        "last_telemetry": last_telemetry_payload,
        "server_timestamp": time.time()
    }

@router.post("/heartbeat")
def receive_agent_heartbeat(payload: Dict[str, Any] = Body(...), db: Session = Depends(get_db)):
    """
    Receives periodic heartbeat pings from the StudIQ Windows Desktop Agent / Bridge.
    """
    global last_agent_ping_time
    import time
    last_agent_ping_time = time.time()
    student_id = payload.get("student_id", 1)
    agent_version = payload.get("agent_version", "1.0.0")

    return {
        "status": "active",
        "student_id": student_id,
        "agent_version": agent_version,
        "server_time": time.time(),
        "message": "Heartbeat received successfully."
    }

@router.post("/update")
@router.post("/telemetry")
def update_telemetry_from_agent(payload: Dict[str, Any] = Body(...), db: Session = Depends(get_db)):
    """
    Receives JSON telemetry updates from StudIQ Windows Desktop Agent.
    Updates continuous entertainment tracker and stores activity log in database.
    """
    global last_agent_ping_time, last_telemetry_payload
    import time
    last_agent_ping_time = time.time()

    student_id = payload.get("student_id", 1)
    app_name = payload.get("application_name", "Unknown Application")
    window_title = payload.get("window_title", "")
    website_url = payload.get("website_url", "")
    category = payload.get("category")
    confidence = payload.get("confidence")
    duration_secs = payload.get("duration_seconds", 5)

    # Re-evaluate with backend behavior_engine if category is missing or Unknown
    if not category or category == "Unknown":
        cat_calc, conf_calc = behavior_engine.classify_with_confidence(app_name, window_title, website_url)
        if cat_calc and cat_calc != "Unknown":
            category = cat_calc
            confidence = conf_calc
        else:
            category = "Utilities" if any(u in app_name.lower() for u in ["explorer", "system", "taskmgr"]) else "Educational"
            confidence = 0.75

    if not confidence:
        confidence = 0.95

    payload["category"] = category
    payload["confidence"] = confidence

    # Process entertainment duration tracking in warning_engine
    ent_res = warning_engine.process_telemetry(
        db=db,
        student_id=student_id,
        app_name=app_name,
        window_title=window_title,
        website_url=website_url,
        category=category,
        duration_secs=float(duration_secs)
    )

    payload["entertainment_status"] = ent_res
    last_telemetry_payload = payload

    try:
        act_log = ActivityLog(
            student_id=student_id,
            application_name=app_name,
            window_title=window_title,
            website_url=website_url,
            category=category,
            confidence=confidence,
            duration=duration_secs
        )
        db.add(act_log)
        db.commit()
    except Exception:
        db.rollback()

    return {
        "status": "success",
        "message": "Desktop agent telemetry stored successfully.",
        "received_category": category,
        "confidence": confidence,
        "show_popup": ent_res["is_popup_active"],
        "popup_message": ent_res["popup_message"],
        "cumulative_entertainment_mins": ent_res["cumulative_entertainment_mins"],
        "warnings_issued": ent_res["warnings_issued"],
        "warnings_remaining": ent_res["warnings_remaining"],
        "ignored_warning_count": ent_res["ignored_warning_count"]
    }

@router.get("/status")
@router.get("/agent-status")
def get_desktop_agent_status(student_id: int = 1, db: Session = Depends(get_db)):
    import time
    global last_agent_ping_time, last_telemetry_payload
    is_connected = False
    ping_delta = None
    if last_agent_ping_time:
        ping_delta = round(time.time() - last_agent_ping_time, 1)
        if ping_delta < 30.0:
            is_connected = True

    ent_status = warning_engine.get_entertainment_status(db, student_id)

    return {
        "connected": is_connected,
        "status": "Active" if is_connected else "Inactive",
        "status_label": "🟢 Monitoring Active" if is_connected else "🔴 Monitoring Inactive",
        "last_ping_seconds_ago": ping_delta,
        "current_telemetry": last_telemetry_payload,
        "entertainment_status": ent_status
    }

@router.get("/current-activity")
def get_current_activity(
    student_id: int = 1,
    current_user: Optional[dict] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    if current_user and current_user.get("role") == "student":
        student_id = current_user.get("user_id", student_id)
    import time
    from datetime import datetime, date
    from app.ai.behavior_intelligence_engine import behavior_intelligence_engine

    is_connected = False
    if last_agent_ping_time and (time.time() - last_agent_ping_time) < 15.0:
        is_connected = True

    ent_status = warning_engine.get_entertainment_status(db, student_id)
    behavior_metrics = behavior_intelligence_engine.evaluate_student_telemetry(db, student_id)

    # Calculate today's category durations from ActivityLog
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_logs = db.query(ActivityLog).filter(
        ActivityLog.student_id == student_id,
        ActivityLog.timestamp >= today_start
    ).all()

    edu_secs = sum(l.duration for l in today_logs if l.category == "Educational")
    prod_secs = sum(l.duration for l in today_logs if l.category == "Productive")
    ent_secs = sum(l.duration for l in today_logs if l.category == "Entertainment")
    game_secs = sum(l.duration for l in today_logs if l.category == "Gaming")
    util_secs = sum(l.duration for l in today_logs if l.category == "Utilities")

    app_name = "Desktop Agent"
    window_title = "Awaiting Active Telemetry"
    website_url = ""
    category = "Educational"
    confidence = 0.85
    idle_secs = 0
    sess_dur = 0

    if last_telemetry_payload:
        app_name = last_telemetry_payload.get("application_name", app_name)
        window_title = last_telemetry_payload.get("window_title", window_title)
        website_url = last_telemetry_payload.get("website_url", website_url)
        category = last_telemetry_payload.get("category", category)
        confidence = last_telemetry_payload.get("confidence", confidence)
        idle_secs = last_telemetry_payload.get("idle_seconds", 0)
        sess_dur = last_telemetry_payload.get("session_duration_seconds", sess_dur)

    latest_log = db.query(ActivityLog).filter(ActivityLog.student_id == student_id).order_by(ActivityLog.timestamp.desc()).first()
    started_at = latest_log.timestamp.strftime("%H:%M:%S") if latest_log and latest_log.timestamp else "N/A"

    focus_res = central_metrics_engine.calculate_focus_index(db, student_id, 24.0)
    burnout_res = central_metrics_engine.calculate_burnout_risk(db, student_id, 24.0)

    return {
        "current_application": app_name,
        "window_title": window_title,
        "website_url": website_url if website_url else "N/A",
        "category": category,
        "confidence": confidence,
        "session_duration": sess_dur,
        "educational_duration": edu_secs,
        "productive_duration": prod_secs,
        "entertainment_duration": ent_secs,
        "gaming_duration": game_secs,
        "utilities_duration": util_secs,
        "idle_seconds": idle_secs,
        "focus_score": focus_res["focus_score"],
        "burnout_probability": burnout_res["probability"],
        "burnout_risk_level": burnout_res["risk_level"],
        "focus_breakdown": focus_res,
        "burnout_breakdown": burnout_res,
        "current_activity_started_at": started_at,
        "agent_connected": is_connected,
        "entertainment_status": ent_status,

        "recent_logs": [
            {
                "id": l.id,
                "application": l.application_name,
                "window_title": l.window_title,
                "website": l.website_url,
                "category": l.category,
                "confidence": getattr(l, "confidence", 0.95) if hasattr(l, "confidence") else 0.95,
                "timestamp": l.timestamp.strftime("%Y-%m-%d %H:%M:%S") if l.timestamp else "",
                "duration": l.duration
            } for l in today_logs[-10:]
        ]
    }

@router.get("/entertainment-status")
@router.get("/timer")
def get_entertainment_tracker_status(student_id: int = 1, db: Session = Depends(get_db)):
    return warning_engine.get_entertainment_status(db, student_id)


@router.post("/popup-action")
def handle_entertainment_popup_action(payload: Dict[str, Any] = Body(...), db: Session = Depends(get_db)):
    student_id = payload.get("student_id", 1)
    action = payload.get("action", "continue_studying")
    return warning_engine.handle_popup_action(db=db, student_id=student_id, action=action)

@router.get("/warnings")
def get_warning_history(student_id: int = 1, db: Session = Depends(get_db)):
    warnings = db.query(WarningLog).filter(WarningLog.student_id == student_id).order_by(WarningLog.timestamp.desc()).all()
    return [
        {
            "id": w.id,
            "warning_count": w.warning_count,
            "message": w.message,
            "parent_notified": w.parent_notified,
            "timestamp": w.timestamp.isoformat()
        }
        for w in warnings
    ]

@router.get("/alerts")
def get_alert_history(student_id: int = 1, db: Session = Depends(get_db)):
    p_alerts = db.query(ParentAlert).filter(ParentAlert.student_id == student_id).order_by(ParentAlert.timestamp.desc()).all()
    m_alerts = db.query(MentorAlert).filter(MentorAlert.student_id == student_id).order_by(MentorAlert.timestamp.desc()).all()
    return {
        "parent_alerts": [
            {
                "id": a.id,
                "student_name": a.student_name,
                "app": a.application_name,
                "website": a.website_url,
                "duration_mins": a.duration_mins,
                "reason": a.reason,
                "timestamp": a.timestamp.isoformat()
            }
            for a in p_alerts
        ],
        "mentor_alerts": [
            {
                "id": a.id,
                "student_name": a.student_name,
                "risk_level": a.risk_level,
                "reason": a.reason,
                "timestamp": a.timestamp.isoformat()
            }
            for a in m_alerts
        ]
    }

@router.get("/summary/today")
def get_today_summary(student_id: int = 1, db: Session = Depends(get_db)):
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    logs = db.query(ActivityLog).filter(ActivityLog.student_id == student_id, ActivityLog.timestamp >= today_start).all()
    edu_secs = sum(l.duration for l in logs if l.category in ["Educational", "Productive"])
    ent_secs = sum(l.duration for l in logs if l.category in ["Entertainment", "Social Media", "Gaming", "Shopping"])
    return {
        "student_id": student_id,
        "date": today_start.strftime("%Y-%m-%d"),
        "today_educational_mins": int(edu_secs // 60),
        "today_entertainment_mins": int(ent_secs // 60),
        "total_study_hours": round(edu_secs / 3600.0, 1),
        "total_entertainment_hours": round(ent_secs / 3600.0, 1)
    }

@router.get("/summary/weekly")
def get_weekly_summary(student_id: int = 1, db: Session = Depends(get_db)):
    now = datetime.utcnow()
    days_data = []
    for i in range(6, -1, -1):
        day_start = (now - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        logs = db.query(ActivityLog).filter(ActivityLog.student_id == student_id, ActivityLog.timestamp >= day_start, ActivityLog.timestamp < day_end).all()
        edu_secs = sum(l.duration for l in logs if l.category in ["Educational", "Productive"])
        ent_secs = sum(l.duration for l in logs if l.category in ["Entertainment", "Social Media", "Gaming", "Shopping"])
        days_data.append({
            "date": day_start.strftime("%Y-%m-%d"),
            "day": day_start.strftime("%a"),
            "educational_hours": round(edu_secs / 3600.0, 1),
            "entertainment_hours": round(ent_secs / 3600.0, 1)
        })
    return days_data


@router.post("/start")
def start_monitoring(student_id: int = 1):
    windows_monitor.start(student_id)
    return {"status": "started", "message": "Windows 11 Background Monitoring Service Active."}

@router.post("/stop")
def stop_monitoring():
    windows_monitor.stop()
    return {"status": "stopped", "message": "Monitoring service paused."}

@router.get("/focus-score")
def get_explainable_focus_score(student_id: int = 1, db: Session = Depends(get_db)):
    """Calculates Focus Score (0-100%) from real database telemetry."""
    return focus_engine.calculate_focus_from_telemetry(db, student_id=student_id)

@router.get("/burnout")
def get_explainable_burnout(student_id: int = 1, db: Session = Depends(get_db)):
    """Calculates Burnout Risk %, Risk Level, and Diagnostic Reasons from real database telemetry."""
    return burnout_engine.calculate_burnout_from_telemetry(db, student_id=student_id)

@router.get("/recommendations")
def get_intelligent_recommendations(student_id: int = 1, db: Session = Depends(get_db)):
    focus_res = focus_engine.calculate_focus_from_telemetry(db, student_id=student_id)
    burnout_res = burnout_engine.calculate_burnout_from_telemetry(db, student_id=student_id)
    ent_status = warning_engine.get_entertainment_status(db, student_id)

    recs = recommendation_engine.generate_recommendations(
        focus_res["focus_score"],
        burnout_res["burnout_score"],
        attendance_rate=92.0,
        entertainment_mins=ent_status.get("cumulative_entertainment_mins", 0)
    )
    return {
        "focus_score": focus_res["focus_score"],
        "burnout_score": burnout_res["burnout_score"],
        "recommendations": focus_res.get("explanation", []) + burnout_res.get("reasons", []) + recs
    }

@router.get("/timeline")
def get_daily_ai_timeline(student_id: int = 1, db: Session = Depends(get_db)):
    """Generates daily activity timeline from real database telemetry."""
    timeline = timeline_engine.generate_daily_timeline_from_db(db, student_id=student_id)
    return {
        "date": datetime.utcnow().strftime("%Y-%m-%d"),
        "timeline": timeline
    }

@router.get("/most-used-apps")
def get_most_used_apps(student_id: int = 1, db: Session = Depends(get_db)):
    """Returns top applications used today formatted with actual duration strings."""
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    logs = db.query(ActivityLog).filter(
        ActivityLog.student_id == student_id,
        ActivityLog.timestamp >= today_start
    ).all()

    app_durations: Dict[str, Dict[str, Any]] = {}
    for l in logs:
        name = l.application_name
        if name not in app_durations:
            app_durations[name] = {"secs": 0, "category": l.category}
        app_durations[name]["secs"] += l.duration

    sorted_apps = sorted(app_durations.items(), key=lambda x: x[1]["secs"], reverse=True)

    result = []
    for app_name, info in sorted_apps[:6]:
        total_mins = int(info["secs"] // 60)
        hrs = total_mins // 60
        mins = total_mins % 60
        duration_str = f"{hrs} hr {mins} min" if hrs > 0 else f"{mins} min"
        result.append({
            "appName": app_name,
            "durationStr": duration_str,
            "mins": total_mins,
            "category": info["category"]
        })

    return result

@router.get("/analytics")
def get_telemetry_analytics(student_id: int = 1, days: int = 7, db: Session = Depends(get_db)):
    """Returns daily category breakdowns and focus/burnout trends from database logs."""
    now = datetime.utcnow()
    days_data = []

    for i in range(days - 1, -1, -1):
        day_start = (now - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        day_label = day_start.strftime("%b %d")

        logs = db.query(ActivityLog).filter(
            ActivityLog.student_id == student_id,
            ActivityLog.timestamp >= day_start,
            ActivityLog.timestamp < day_end
        ).all()

        edu_mins = sum(l.duration for l in logs if l.category == "Educational") // 60
        prod_mins = sum(l.duration for l in logs if l.category == "Productive") // 60
        ent_mins = sum(l.duration for l in logs if l.category in ["Entertainment", "Social Media"]) // 60
        game_mins = sum(l.duration for l in logs if l.category in ["Gaming", "Shopping"]) // 60

        days_data.append({
            "day": day_label,
            "educationalMins": edu_mins,
            "productiveMins": prod_mins,
            "entertainmentMins": ent_mins,
            "gamingMins": game_mins,
            "studyHours": round((edu_mins + prod_mins) / 60.0, 1)
        })

    return days_data

@router.post("/whitelist")
def add_parent_whitelist_app(student_id: int = Body(...), app_name: str = Body(...), db: Session = Depends(get_db)):
    existing = db.query(ParentWhitelist).filter(
        ParentWhitelist.student_id == student_id,
        ParentWhitelist.application_name == app_name
    ).first()

    if not existing:
        whitelist_entry = ParentWhitelist(student_id=student_id, application_name=app_name)
        db.add(whitelist_entry)
        db.commit()

    return {
        "status": "success",
        "message": f"Application '{app_name}' successfully whitelisted by Parent.",
        "student_id": student_id
    }

@router.post("/study-mode")
def configure_study_mode(student_id: int = Body(...), start_hour: int = Body(19), end_hour: int = Body(22), is_active: bool = Body(True), db: Session = Depends(get_db)):
    config = db.query(StudyModeConfig).filter(StudyModeConfig.student_id == student_id).first()
    if not config:
        config = StudyModeConfig(student_id=student_id, start_hour=start_hour, end_hour=end_hour, is_active=is_active)
        db.add(config)
    else:
        config.start_hour = start_hour
        config.end_hour = end_hour
        config.is_active = is_active

    db.commit()
    return {
        "status": "success",
        "study_mode": {
            "start_hour": start_hour,
            "end_hour": end_hour,
            "is_active": is_active
        }
    }

from app.ai.behavior_intelligence_engine import behavior_intelligence_engine

@router.get("/behavior-intelligence")
def get_behavior_intelligence_metrics(student_id: int = 1, db: Session = Depends(get_db)):
    """
    Real AI Behavior Intelligence Engine:
    Calculates Focus Score, Burnout Risk & Level, Digital Wellness Score, Productivity Score,
    Category Contributions %, Study Consistency, and Live Activity status from SQLite telemetry.
    """
    return behavior_intelligence_engine.evaluate_student_telemetry(db, student_id=student_id)

@router.get("/digital-wellness")
def get_digital_wellness_metrics(student_id: int = 1, db: Session = Depends(get_db)):
    eval_res = behavior_intelligence_engine.evaluate_student_telemetry(db, student_id=student_id, persist_snapshot=False)
    return {
        "digital_wellness_score": eval_res["digital_wellness_score"],
        "student_id": student_id
    }

@router.get("/productivity")
def get_productivity_metrics(student_id: int = 1, db: Session = Depends(get_db)):
    eval_res = behavior_intelligence_engine.evaluate_student_telemetry(db, student_id=student_id, persist_snapshot=False)
    return {
        "productivity_score": eval_res["productivity_score"],
        "category_contributions": eval_res["category_contributions"]
    }

@router.get("/consistency")
def get_study_consistency_metrics(student_id: int = 1, db: Session = Depends(get_db)):
    eval_res = behavior_intelligence_engine.evaluate_student_telemetry(db, student_id=student_id, persist_snapshot=False)
    return eval_res["study_consistency"]


