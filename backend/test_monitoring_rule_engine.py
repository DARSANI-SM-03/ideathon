import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.database.session import SessionLocal, engine
from app.database.base import Base
from app.models.user import Student
from app.models.monitoring import (
    ActivityLog, WarningLog, ParentAlert, MentorAlert,
    EntertainmentSession
)
from app.ai.warning_engine import warning_engine

def test_monitoring_rule_engine():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    print("==========================================================================================")
    print("        STUDIQ INTELLIGENT MONITORING RULE ENGINE (TASK 3) VERIFICATION                   ")
    print("==========================================================================================")

    # Setup test student
    student = db.query(Student).filter(Student.id == 1).first()
    if not student:
        student = Student(id=1, student_id="STU-2026-001", name="Alex Mercer", department="Computer Science", semester=4, focus_score=85.0, burnout_score=15.0, attendance=92.5, cgpa=3.82)
        db.add(student)
        db.commit()

    # Reset tracker and DB logs for student 1
    db.query(WarningLog).filter(WarningLog.student_id == 1).delete()
    db.query(ParentAlert).filter(ParentAlert.student_id == 1).delete()
    db.query(MentorAlert).filter(MentorAlert.student_id == 1).delete()
    db.commit()

    tracker = warning_engine.get_tracker(1)
    tracker.cumulative_entertainment_secs = 0.0
    tracker.last_warning_threshold_mins = 0
    tracker.warnings_issued = 0
    tracker.ignored_warning_count = 0
    tracker.is_popup_active = False

    # SCENARIO STEP 1: Student watches YouTube for 10 minutes (600 seconds)
    res1 = warning_engine.process_telemetry(db, student_id=1, app_name="chrome.exe", window_title="YouTube Music", website_url="youtube.com", category="Entertainment", duration_secs=600)
    print(f"[STEP 1] 10m YouTube -> Cumulative: {res1['cumulative_entertainment_mins']}m | Popup: {res1['is_popup_active']}")
    assert res1['cumulative_entertainment_mins'] == 10, "Cumulative mins should be 10!"
    assert not res1['is_popup_active'], "10 mins should NOT trigger popup!"

    # SCENARIO STEP 2: Student switches to Netflix for 8 minutes (480 seconds) -> Total = 18 mins
    res2 = warning_engine.process_telemetry(db, student_id=1, app_name="netflix.exe", window_title="Netflix - Movie", website_url="netflix.com", category="Entertainment", duration_secs=480)
    print(f"[STEP 2] +8m Netflix  -> Cumulative: {res2['cumulative_entertainment_mins']}m | Popup: {res2['is_popup_active']} | Message: '{res2['popup_message']}'")
    assert res2['cumulative_entertainment_mins'] == 18, "Cumulative mins should be 18!"
    assert res2['is_popup_active'], "18 cumulative mins MUST trigger 15-minute warning popup!"
    assert res2['warnings_issued'] == 1, "Warnings issued count should be 1!"

    # SCENARIO STEP 3: Student ignores warning
    act_res1 = warning_engine.handle_popup_action(db, student_id=1, action="ignore")
    print(f"[STEP 3] Action: Ignore -> Popup active: {act_res1['is_popup_active']} | Ignored Count: {act_res1['ignored_warning_count']}")
    assert not act_res1['is_popup_active'], "Popup should close after action!"
    assert act_res1['ignored_warning_count'] == 1, "Ignored warning count should be 1!"

    # SCENARIO STEP 4: Entertainment continues for 12 more minutes (720 seconds) -> Total = 30 mins
    res3 = warning_engine.process_telemetry(db, student_id=1, app_name="spotify.exe", window_title="Spotify Free", website_url="spotify.com", category="Entertainment", duration_secs=720)
    print(f"[STEP 4] +12m Spotify -> Cumulative: {res3['cumulative_entertainment_mins']}m | Popup: {res3['is_popup_active']} | Warnings: {res3['warnings_issued']}")
    assert res3['cumulative_entertainment_mins'] == 30, "Cumulative mins should be 30!"
    assert res3['is_popup_active'], "30 cumulative mins MUST trigger 30-minute warning popup!"
    assert res3['warnings_issued'] == 2, "Warnings issued count should be 2!"

    # SCENARIO STEP 5: Fast forward to 75 minutes cumulative (4500 seconds total) -> Parent Alert Threshold
    res4 = warning_engine.process_telemetry(db, student_id=1, app_name="steam.exe", window_title="Steam Game", website_url="", category="Gaming", duration_secs=2700)
    print(f"[STEP 5] +45m Gaming -> Cumulative: {res4['cumulative_entertainment_mins']}m | Warnings: {res4['warnings_issued']}")

    p_alerts = db.query(ParentAlert).filter(ParentAlert.student_id == 1).all()
    print(f"[STEP 6] Parent Alerts in DB: {len(p_alerts)}")
    if p_alerts:
        print(f"         Alert Reason: {p_alerts[0].reason}")

    assert len(p_alerts) >= 1, "Parent alert MUST be generated after cumulative threshold!"

    print("==========================================================================================")
    print("SUCCESS: Intelligent Monitoring Rule Engine verified 100% accurately against all rules!")
    print("==========================================================================================")

    db.close()

if __name__ == "__main__":
    test_monitoring_rule_engine()
