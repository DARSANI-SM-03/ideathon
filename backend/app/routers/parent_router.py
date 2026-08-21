from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict, Any, List
from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.ai.warning_engine import warning_engine
from app.ai.focus_engine import focus_engine
from app.ai.burnout_engine import burnout_engine
from app.ai.timeline_engine import timeline_engine
from app.models.monitoring import ActivityLog, WarningLog
from app.models.user import Student, ParentApprovalRequest, Device

router = APIRouter(prefix="/parent", tags=["Parent Portal"])

@router.get("/pending-approvals")
def get_pending_approvals(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    reqs = db.query(ParentApprovalRequest).filter(ParentApprovalRequest.status == "Pending").order_by(ParentApprovalRequest.created_at.desc()).all()
    return [
        {
            "id": r.id,
            "student_id": r.student_id,
            "student_name": r.student_name,
            "student_code": r.student_code,
            "college_name": r.college_name,
            "department": r.department,
            "parent_email": r.parent_email,
            "parent_phone": r.parent_phone,
            "registration_time": r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else ""
        }
        for r in reqs
    ]

@router.post("/approve-student")
def approve_student_request(payload: Dict[str, Any] = Body(...), current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    req_id = payload.get("request_id")
    action = payload.get("action", "approve").lower()

    approval_req = db.query(ParentApprovalRequest).filter(ParentApprovalRequest.id == req_id).first()
    if not approval_req:
        raise HTTPException(status_code=404, detail="Approval request not found.")

    student = db.query(Student).filter(Student.id == approval_req.student_id).first()

    if action == "approve":
        approval_req.status = "Approved"
        approval_req.updated_at = datetime.utcnow()
        if student:
            student.status = "Active"
            student.monitoring_authorized = True
        db.commit()
        return {"status": "success", "message": f"Approved student registration for {approval_req.student_name}."}
    else:
        approval_req.status = "Rejected"
        approval_req.updated_at = datetime.utcnow()
        if student:
            student.status = "Rejected"
            student.monitoring_authorized = False
        db.commit()
        return {"status": "success", "message": f"Rejected student registration for {approval_req.student_name}."}

@router.get("/devices")
def get_parent_devices(student_id: int = 1, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    devices = db.query(Device).filter(Device.student_id == student_id).order_by(Device.last_seen.desc()).all()
    if not devices:
        return [
            {
                "id": 1,
                "device_id": "DESKTOP-STUDIQ-WIN11",
                "device_name": "Alex Primary Workstation",
                "os_name": "Windows 11 Pro 64-bit",
                "agent_version": "v2.4",
                "is_trusted": True,
                "status_str": "Trusted Active Device",
                "last_seen": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            }
        ]
    return [
        {
            "id": d.id,
            "device_id": d.device_id,
            "device_name": d.device_name,
            "os_name": d.os_name,
            "agent_version": d.agent_version,
            "is_trusted": d.is_trusted,
            "status_str": "Trusted Active Device" if d.is_trusted else "Unknown Device Detected",
            "last_seen": d.last_seen.strftime("%Y-%m-%d %H:%M:%S") if d.last_seen else ""
        }
        for d in devices
    ]

@router.get("/children")

def get_parent_children(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    students = db.query(Student).limit(10).all()
    if not students:
        return [
            {"id": 1, "name": "Alex Mercer", "student_id": "STU-2026-001", "department": "Computer Science", "status": "Active"},
            {"id": 2, "name": "Sam Mercer", "student_id": "STU-2026-002", "department": "Data Science", "status": "Active"},
            {"id": 3, "name": "Jordan Mercer", "student_id": "STU-2026-003", "department": "Artificial Intelligence", "status": "Active"}
        ]
    return [
        {
            "id": s.id,
            "name": s.name or s.full_name,
            "student_id": s.student_id,
            "department": s.department or "Computer Science",
            "status": s.status or "Active"
        }
        for s in students
    ]

@router.get("/dashboard")
def get_parent_dashboard(student_id: int = 1, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    student_name = student.name if student else "Alex Mercer"


    ent_status = warning_engine.get_entertainment_status(db, student_id)


    # 1. Fetch Today's Activity Logs
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_logs = db.query(ActivityLog).filter(
        ActivityLog.student_id == student_id,
        ActivityLog.timestamp >= today_start
    ).order_by(ActivityLog.timestamp.desc()).all()

    # 2. Latest Monitored App/Website/Category
    latest_log = today_logs[0] if today_logs else None
    current_app = latest_log.application_name if latest_log else "VS Code"
    current_title = latest_log.window_title if latest_log else "studiq / main.py"
    current_website = latest_log.website_url if latest_log else ""
    current_category = latest_log.category if latest_log else "Productive"

    # 3. Category Duration Sums (mins)
    edu_secs = sum(l.duration for l in today_logs if l.category == "Educational")
    prod_secs = sum(l.duration for l in today_logs if l.category == "Productive")
    ent_secs = sum(l.duration for l in today_logs if l.category in ["Entertainment", "Social Media"])
    game_secs = sum(l.duration for l in today_logs if l.category in ["Gaming", "Shopping"])

    edu_mins = int(edu_secs // 60)
    prod_mins = int(prod_secs // 60)
    ent_mins = int(ent_secs // 60)
    game_mins = int(game_secs // 60)

    # 4. Most Used Apps
    app_durations = {}
    for l in today_logs:
        name = l.application_name
        if name not in app_durations:
            app_durations[name] = {"secs": 0, "category": l.category}
        app_durations[name]["secs"] += l.duration

    sorted_apps = sorted(app_durations.items(), key=lambda x: x[1]["secs"], reverse=True)
    most_used_apps = []
    for app_name, info in sorted_apps[:6]:
        total_mins = int(info["secs"] // 60)
        hrs = total_mins // 60
        mins = total_mins % 60
        duration_str = f"{hrs} hr {mins} min" if hrs > 0 else f"{mins} min"
        most_used_apps.append({
            "appName": app_name,
            "durationStr": duration_str,
            "mins": total_mins,
            "category": info["category"]
        })

    # 5. Daily Timeline
    daily_timeline = timeline_engine.generate_daily_timeline_from_db(db, student_id=student_id)

    # 6. Real Focus Score & Burnout Risk
    focus_res = focus_engine.calculate_focus_from_telemetry(db, student_id=student_id)
    burnout_res = burnout_engine.calculate_burnout_from_telemetry(db, student_id=student_id)

    # 7. Parent Notifications & Warnings
    notifications = list(ent_status.get("parent_notifications", []))
    if ent_status["ignored_warning_count"] >= 5 and not notifications:
        notifications.append(
            "ALERT: Student ignored 5 continuous entertainment usage warnings. High screen distraction detected."
        )

    warning_logs = db.query(WarningLog).filter(WarningLog.student_id == student_id).order_by(WarningLog.timestamp.desc()).limit(5).all()
    warnings_received = [
        {
            "id": w.id,
            "message": w.message,
            "time": w.timestamp.strftime("%I:%M %p") if w.timestamp else "10:00 AM"
        }
        for w in warning_logs
    ]

    return {
        "studentName": student_name,
        "studentAvatar": "",
        "status": {
            "status": "ENTERTAINMENT" if ent_status["timer_status"] == "Active" else "STUDYING",
            "currentApp": current_app,
            "currentTitle": current_title,
            "currentWebsite": current_website,
            "currentCategory": current_category,
            "lastSyncTime": datetime.utcnow().isoformat(),
        },
        "focusScore": focus_res["focus_score"],
        "burnoutScore": burnout_res["burnout_score"],
        "burnoutRisk": burnout_res["risk_level"],
        "burnoutReasons": burnout_res.get("reasons", []),
        "attendance": student.attendance if student else 92.5,
        "cgpa": student.cgpa if student else 3.82,
        "todayEducationalTime": edu_mins,
        "todayProductiveTime": prod_mins,
        "todayEntertainmentTime": ent_mins,
        "todayGamingTime": game_mins,
        "todayStudyTime": edu_mins + prod_mins,
        "mostUsedApps": most_used_apps,
        "dailyTimeline": daily_timeline,
        "warningsReceived": warnings_received,
        "ignoredWarningCount": ent_status["ignored_warning_count"],
        "parentAlerts": notifications,
        "lastSyncTime": datetime.utcnow().isoformat()
    }

@router.get("/academic")
def get_parent_academic(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    return {
        "attendancePercent": 92.5,
        "assignmentsCompleted": 14,
        "assignmentsPending": 2,
        "assignmentsTotal": 16,
        "quizAverage": 86.4,
        "cgpa": 3.82,
        "cgpaTrend": [
            {"semester": "Sem 1", "cgpa": 3.65},
            {"semester": "Sem 2", "cgpa": 3.74},
            {"semester": "Sem 3", "cgpa": 3.80},
            {"semester": "Sem 4", "cgpa": 3.82}
        ],
        "subjects": [
            {"subject": "Data Structures & Algorithms", "code": "CS301", "attendance": 95, "grade": "A", "marks": 88, "maxMarks": 100, "quizAvg": 90},
            {"subject": "Operating Systems", "code": "CS302", "attendance": 90, "grade": "A-", "marks": 82, "maxMarks": 100, "quizAvg": 84},
            {"subject": "Database Management Systems", "code": "CS303", "attendance": 92, "grade": "A", "marks": 89, "maxMarks": 100, "quizAvg": 88},
            {"subject": "Computer Networks", "code": "CS304", "attendance": 88, "grade": "B+", "marks": 78, "maxMarks": 100, "quizAvg": 79}
        ],
        "teacherFeedback": [
            {"id": "1", "teacher": "Dr. Sarah Jenkins", "subject": "CS301", "message": "Alex shows exceptional problem-solving skills in lab exercises.", "date": "2026-07-25", "sentiment": "positive"},
            {"id": "2", "teacher": "Prof. David Miller", "subject": "CS304", "message": "Consistent performance, though could participate more in group discussions.", "date": "2026-07-20", "sentiment": "neutral"}
        ]
    }

