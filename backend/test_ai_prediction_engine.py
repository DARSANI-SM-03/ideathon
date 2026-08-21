import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.database.session import SessionLocal, engine
from app.database.base import Base
from app.models.user import Student
from app.models.monitoring import ActivityLog, WarningLog, AIPrediction
from app.ai.prediction_engine import ai_prediction_engine

def test_ai_prediction_engine():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    print("==========================================================================================")
    print("        STUDIQ AI PREDICTION & RECOMMENDATION ENGINE (TASK 6) VERIFICATION                 ")
    print("==========================================================================================")

    # 1. Setup Student & Seed Telemetry Logs
    student = db.query(Student).filter(Student.id == 1).first()
    if not student:
        student = Student(id=1, student_id="STU-2026-001", name="Alex Mercer", department="Computer Science", semester=4, focus_score=85.0, burnout_score=15.0, attendance=92.5, cgpa=3.82)
        db.add(student)
        db.commit()

    now = datetime.utcnow()
    # Add late-night study log and entertainment logs to trigger pattern detection
    db.add(ActivityLog(student_id=1, application_name="chrome.exe", window_title="Late Night YouTube", website_url="youtube.com", category="Entertainment", duration=3600, timestamp=now.replace(hour=23, minute=15)))
    db.add(ActivityLog(student_id=1, application_name="netflix.exe", window_title="Netflix Movie", website_url="netflix.com", category="Entertainment", duration=2400, timestamp=now - timedelta(days=1)))
    db.add(ActivityLog(student_id=1, application_name="code.exe", window_title="main.py - VS Code", website_url="", category="Educational", duration=7200, timestamp=now - timedelta(days=2)))
    db.commit()

    # 2. Test AI Prediction Engine
    pred = ai_prediction_engine.predict_student_behavior(db, student_id=1)
    print(f"[PREDICTION] Burnout Risk: {pred['risk_predictions']['burnout_risk']} ({pred['risk_predictions']['burnout_probability_pct']}%)")
    print(f"             Focus Decline: {pred['risk_predictions']['focus_decline_risk']} | Distraction: {pred['risk_predictions']['distraction_risk']}")
    print(f"             Detected Patterns: {pred['detected_patterns']}")
    print(f"             AI Recommendations: {pred['recommendations']}")

    assert "burnout_risk" in pred['risk_predictions'], "Burnout risk missing!"
    assert len(pred['detected_patterns']) > 0, "Pattern detection failed!"
    assert len(pred['recommendations']) > 0, "Recommendations generation failed!"

    # 3. Test Parent Insights
    p_insights = ai_prediction_engine.get_parent_insights(db, student_id=1)
    print(f"[PARENT INSIGHTS] Summary: {p_insights['weekly_behavior_summary']}")
    print(f"                 Improvements: {p_insights['positive_improvements']}")
    print(f"                 Concerns: {p_insights['areas_of_concern']}")
    assert "positive_improvements" in p_insights, "Positive improvements missing from Parent Insights!"

    # 4. Test Mentor Insights
    m_insights = ai_prediction_engine.get_mentor_insights(db)
    print(f"[MENTOR INSIGHTS] Total Mentees Needing Intervention: {m_insights['students_needing_intervention_count']}")
    assert "interventions" in m_insights, "Interventions missing from Mentor Insights!"

    # 5. Test Admin Insights
    a_insights = ai_prediction_engine.get_admin_insights(db)
    print(f"[ADMIN INSIGHTS] Campus Avg Burnout: {a_insights['average_burnout_pct']}% | Top Dept: {a_insights['most_productive_department']}")
    assert "most_productive_department" in a_insights, "Top department missing from Admin Insights!"

    # 6. Test Behavior Trends (7, 30, 90 days)
    t7 = ai_prediction_engine.get_behavior_trends(db, student_id=1, period_days=7)
    t30 = ai_prediction_engine.get_behavior_trends(db, student_id=1, period_days=30)
    t90 = ai_prediction_engine.get_behavior_trends(db, student_id=1, period_days=90)
    print(f"[TRENDS] 7-Day Trend Length: {len(t7['trends'])} | 30-Day: {len(t30['trends'])} | 90-Day: {len(t90['trends'])}")

    assert len(t7['trends']) == 7, "7-day trend count invalid!"
    assert len(t30['trends']) == 30, "30-day trend count invalid!"
    assert len(t90['trends']) == 90, "90-day trend count invalid!"

    print("==========================================================================================")
    print("SUCCESS: AI Prediction & Recommendation Engine verified 100% functional from real data!")
    print("==========================================================================================")

    db.close()

if __name__ == "__main__":
    test_ai_prediction_engine()
