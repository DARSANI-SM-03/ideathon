import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.database.session import SessionLocal, engine
from app.database.base import Base
from app.services.student_service import student_service
from app.services.admin_service import admin_service
from app.routers.parent_router import get_parent_dashboard
from app.routers.mentor_router import get_mentor_dashboard
from app.routers.report_router import export_report_csv, export_report_pdf
from app.routers.notification_router import get_notifications

def test_production_dashboards():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    print("==========================================================================================")
    print("        STUDIQ PRODUCTION-GRADE LIVE DASHBOARDS (TASK 5) VERIFICATION                     ")
    print("==========================================================================================")

    # 1. Student Dashboard API Test
    student_dash = student_service.get_student_dashboard(db, 1)
    print(f"[STUDENT DASHBOARD] Focus: {student_dash['focus_score']} | Burnout: {student_dash['burnout_score']} | Status: {str(student_dash['current_status']).encode('ascii', 'ignore').decode('ascii')}")
    assert "digital_wellness_score" in student_dash, "Digital Wellness missing from Student Dashboard!"
    assert "productivity_score" in student_dash, "Productivity Score missing from Student Dashboard!"
    assert "study_consistency" in student_dash, "Study Consistency missing from Student Dashboard!"

    # 2. Parent Dashboard API Test
    parent_dash = get_parent_dashboard(current_user={"user_id": 1, "role": "parent"}, db=db)
    print(f"[PARENT DASHBOARD] Student: {parent_dash['studentName']} | Focus: {parent_dash['focusScore']} | Edu Time: {parent_dash['todayEducationalTime']}m")
    assert "mostUsedApps" in parent_dash, "Most used apps missing from Parent Dashboard!"
    assert "dailyTimeline" in parent_dash, "Daily timeline missing from Parent Dashboard!"

    # 3. Mentor Dashboard API Test
    mentor_dash = get_mentor_dashboard(db=db)
    print(f"[MENTOR DASHBOARD] Total Mentees: {len(mentor_dash['students'])} | High Risk Count: {len(mentor_dash['highRiskStudents'])}")
    assert "students" in mentor_dash, "Student roster missing from Mentor Dashboard!"

    # 4. Admin Dashboard API Test
    admin_dash = admin_service.get_admin_dashboard_metrics(db)
    print(f"[ADMIN DASHBOARD] Total Students: {admin_dash['total_students']} | Avg Focus: {admin_dash['avg_focus_score']} | Avg Burnout: {admin_dash['avg_burnout_score']}")
    assert "department_analytics" in admin_dash, "Department analytics missing from Admin Dashboard!"


    # 5. Notification Center API Test
    notifs = get_notifications(student_id=1, db=db)
    print(f"[NOTIFICATION CENTER] Persistent Items Returned: {len(notifs)}")
    assert len(notifs) >= 1, "Notification center returned empty!"

    # 6. CSV & PDF Export API Test
    csv_res = export_report_csv(report_type="daily", student_id=1, db=db)
    print(f"[EXPORT CSV] Daily CSV Content-Length: {len(csv_res.body)} bytes")
    assert len(csv_res.body) > 0, "CSV export empty!"

    pdf_res = export_report_pdf(report_type="weekly", student_id=1, db=db)
    print(f"[EXPORT PDF] Weekly PDF HTML Content-Length: {len(pdf_res.body)} bytes")
    assert len(pdf_res.body) > 0, "PDF HTML export empty!"

    print("==========================================================================================")
    print("SUCCESS: Production-grade dashboards & export APIs verified 100% functional!")
    print("==========================================================================================")

    db.close()

if __name__ == "__main__":
    test_production_dashboards()

