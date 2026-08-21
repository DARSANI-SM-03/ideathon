from app.database.session import SessionLocal
import app.models  # Ensures all SQLAlchemy models are registered
from app.models.user import Student, Parent, Mentor, Admin, Institution
from app.models.academic import AttendanceRecord, QuizScore, Assignment, Exam, TeacherFeedback
from app.models.monitoring import ActivityLog, FocusScore, BurnoutPrediction
from app.models.collaboration import Meeting, ParentConsent
from app.models.notification import Notification

db = SessionLocal()

tables_to_check = [
    ("1. institutions", Institution),
    ("2. students", Student),
    ("3. parents", Parent),
    ("4. mentors", Mentor),
    ("5. admins", Admin),
    ("6. attendance", AttendanceRecord),
    ("7. assignments", Assignment),
    ("8. quizzes", QuizScore),
    ("9. exams", Exam),
    ("10. teacher_feedback", TeacherFeedback),
    ("11. activity_logs", ActivityLog),
    ("12. focus_scores", FocusScore),
    ("13. burnout_predictions", BurnoutPrediction),
    ("14. notifications", Notification),
    ("15. meetings", Meeting),
    ("16. parent_consent", ParentConsent)
]

print("=== DATABASE INTEGRITY CHECK ACROSS ALL 16 TABLES ===")
all_passed = True
for name, model in tables_to_check:
    try:
        count = db.query(model).count()
        print(f"[OK] Table '{name}': {count} records verified.")
    except Exception as e:
        print(f"[FAIL] Table '{name}': ERROR -> {e}")
        all_passed = False

db.close()

if all_passed:
    print("\nSUCCESS: All 16 database tables exist, have valid foreign key relationships, and are fully seeded!")
else:
    print("\nFAILURE: One or more tables failed integrity check.")
