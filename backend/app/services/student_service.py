from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.user import Student
from app.models.monitoring import ActivityLog, WarningLog
from app.models.academic import AttendanceRecord, QuizScore, Assignment
from app.ai.behavior_intelligence_engine import behavior_intelligence_engine
from datetime import datetime, timedelta


class StudentService:
    def get_student_dashboard(self, db: Session, student_id_or_num) -> dict:
        if isinstance(student_id_or_num, int):
            student = db.query(Student).filter(Student.id == student_id_or_num).first()
        else:
            student = db.query(Student).filter(
                (Student.student_id == student_id_or_num) | (Student.email == student_id_or_num)
            ).first()

        if not student:
            student = db.query(Student).first()

        if not student:
            # Seed initial student if DB empty
            student = Student(student_id="STU-2026-001", name="Alex Mercer", department="Computer Science", semester=4, focus_score=85.0, burnout_score=15.0, attendance=92.5, cgpa=3.82)
            db.add(student)
            db.commit()

        sid = student.id

        # Run AI Behavior Intelligence Engine
        ai_res = behavior_intelligence_engine.evaluate_student_telemetry(db, student_id=sid)

        # Quizzes & Assignments
        quizzes = db.query(QuizScore).filter(QuizScore.student_id == sid).all()
        avg_quiz = sum(q.score for q in quizzes) / max(1, len(quizzes)) if quizzes else 85.0

        pending_assignments = db.query(Assignment).filter(
            Assignment.student_id == sid,
            Assignment.status == "Pending"
        ).count()

        # Warnings
        warnings = db.query(WarningLog).filter(WarningLog.student_id == sid).order_by(WarningLog.timestamp.desc()).limit(10).all()
        warning_list = [
            {
                "id": w.id,
                "title": "Continuous Entertainment Limit",
                "message": w.message,
                "severity": "High" if w.warning_count >= 5 else "Medium",
                "created_at": w.timestamp.strftime("%Y-%m-%d %H:%M") if w.timestamp else ""
            }
            for w in warnings
        ]

        # Weekly Analytics
        now = datetime.utcnow()
        days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        weekly_analytics = []

        for i in range(6, -1, -1):
            day_dt = now - timedelta(days=i)
            day_name = days_of_week[day_dt.weekday()]
            day_start = day_dt.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)

            day_logs = db.query(ActivityLog).filter(
                ActivityLog.student_id == sid,
                ActivityLog.timestamp >= day_start,
                ActivityLog.timestamp < day_end
            ).all()

            day_study_secs = sum(l.duration for l in day_logs if l.category in ["Educational", "Productive"])
            day_ent_secs = sum(l.duration for l in day_logs if l.category in ["Entertainment", "Social Media", "Gaming"])

            weekly_analytics.append({
                "day": day_name,
                "date": day_start.strftime("%Y-%m-%d"),
                "focus": ai_res["focus_score"] if day_logs else 80.0,
                "burnout": ai_res["burnout_score"] if day_logs else 15.0,
                "study_hours": round(day_study_secs / 3600.0, 1),
                "entertainment_mins": int(day_ent_secs // 60)
            })

        return {
            "student_id": student.student_id,
            "name": student.name,
            "department": student.department,
            "semester": student.semester,
            "focus_score": ai_res["focus_score"],
            "burnout_score": ai_res["burnout_score"],
            "burnout_risk_level": ai_res["burnout_level"],
            "burnout_reasons": ai_res["burnout_reasons"],
            "digital_wellness_score": ai_res["digital_wellness_score"],
            "productivity_score": ai_res["productivity_score"],
            "category_contributions": ai_res["category_contributions"],
            "study_consistency": ai_res["study_consistency"],
            "live_activity": ai_res["live_activity"],
            "cgpa": student.cgpa,
            "attendance": student.attendance,
            "today_productive_time_mins": int(ai_res["category_contributions"]["educational_pct"] * 2.4),
            "today_entertainment_time_mins": int(ai_res["category_contributions"]["entertainment_pct"] * 2.4),
            "current_status": ai_res["live_activity"]["current_focus_state"],
            "pending_assignments_count": pending_assignments,
            "avg_quiz_score": round(avg_quiz, 1),
            "recent_warnings": warning_list,
            "weekly_analytics": weekly_analytics,
            "monthly_analytics": [],
            "recommendations": ai_res["burnout_reasons"]
        }


student_service = StudentService()

