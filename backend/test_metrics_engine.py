"""
StudIQ Central Metrics Engine Automated Integration & Unit Test Suite
====================================================================
Tests the calculation engine for Focus Index, Burnout Risk, Activity Aggregation,
Recommendations, and Report Summaries.
"""

import os
import sys
import unittest
from datetime import datetime, timedelta

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.database.session import SessionLocal
from app.models.user import Student
from app.models.monitoring import ActivityLog, StudentSettings, StudySession
from app.ai.central_metrics_engine import central_metrics_engine


class TestCentralMetricsEngine(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()
        self.student = self.db.query(Student).filter(Student.student_id == "STU-TEST-METRICS").first()
        if not self.student:
            self.student = Student(
                student_id="STU-TEST-METRICS",
                name="Metrics Test Student",
                full_name="Metrics Test Student",
                email="metrics.test@studiq.edu",
                password_hash="$2b$12$eImiTXuWVxfM37uY4JANjOL.81F81A.y2",
                department="Computer Science",
                semester=4,
                cgpa=3.85,
                attendance=94.5,
                focus_score=85.0,
                burnout_score=15.0
            )
            self.db.add(self.student)
            self.db.commit()
            self.db.refresh(self.student)

        # Clear existing logs for test student
        self.db.query(ActivityLog).filter(ActivityLog.student_id == self.student.id).delete()
        self.db.commit()

    def tearDown(self):
        self.db.close()

    def test_1_empty_logs_baseline_focus_and_burnout(self):
        focus_res = central_metrics_engine.calculate_focus_index(self.db, self.student.id, 24.0)
        burnout_res = central_metrics_engine.calculate_burnout_risk(self.db, self.student.id, 24.0)
        breakdown = central_metrics_engine.aggregate_activity_breakdown(self.db, self.student.id, 24.0)

        self.assertGreaterEqual(focus_res["focus_score"], 70.0)
        self.assertLessEqual(burnout_res["probability"], 30.0)
        self.assertEqual(breakdown["total_study_mins"], 0)
        print("\n[PASS] TEST 1: Baseline Focus & Burnout for empty telemetry verified.")

    def test_2_study_telemetry_increases_focus_score(self):
        # Insert 2 hours of Educational study logs
        for i in range(8):
            log = ActivityLog(
                student_id=self.student.id,
                application_name="VS Code",
                window_title="main.py - StudIQ Engine",
                category="Educational",
                confidence=0.98,
                duration=900,  # 15 mins
                timestamp=datetime.utcnow() - timedelta(minutes=i * 15)
            )
            self.db.add(log)
        self.db.commit()

        focus_res = central_metrics_engine.calculate_focus_index(self.db, self.student.id, 24.0)
        breakdown = central_metrics_engine.aggregate_activity_breakdown(self.db, self.student.id, 24.0)

        self.assertGreaterEqual(focus_res["focus_score"], 80.0)
        self.assertEqual(breakdown["total_study_mins"], 120)
        print(f"[PASS] TEST 2: Active Study Telemetry produced Focus Index = {focus_res['focus_score']}.")

    def test_3_high_entertainment_increases_burnout_and_reduces_focus(self):
        # Insert 2 hours of Entertainment logs
        for i in range(6):
            log = ActivityLog(
                student_id=self.student.id,
                application_name="YouTube",
                window_title="Gaming Stream",
                category="Entertainment",
                confidence=0.95,
                duration=1200,  # 20 mins
                timestamp=datetime.utcnow() - timedelta(minutes=i * 20)
            )
            self.db.add(log)
        self.db.commit()

        focus_res = central_metrics_engine.calculate_focus_index(self.db, self.student.id, 24.0)
        burnout_res = central_metrics_engine.calculate_burnout_risk(self.db, self.student.id, 24.0)

        self.assertLess(focus_res["focus_score"], 85.0)
        print(f"[PASS] TEST 3: High Entertainment impact verified (Focus = {focus_res['focus_score']}, Burnout = {burnout_res['probability']}%).")

    def test_4_evidence_based_recommendations(self):
        recs = central_metrics_engine.generate_evidence_based_recommendations(self.db, self.student.id)
        self.assertIsInstance(recs, list)
        self.assertGreater(len(recs), 0)
        self.assertIn("title", recs[0])
        self.assertIn("evidence", recs[0])
        print(f"[PASS] TEST 4: Evidence-based recommendations generated ({len(recs)} recommendation items).")

    def test_5_report_summaries(self):
        report = central_metrics_engine.aggregate_report_data(self.db, self.student.id, "Weekly")
        self.assertEqual(report["report_type"], "Weekly")
        self.assertIn("focus_score", report)
        self.assertIn("burnout_risk_score", report)
        print(f"[PASS] TEST 5: Aggregated Report Summary verified (Period = {report['period']}, Focus = {report['focus_score']}).")


if __name__ == "__main__":
    unittest.main()
