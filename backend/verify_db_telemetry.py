from app.database.session import SessionLocal
from app.models.monitoring import ActivityLog

db = SessionLocal()

recent_logs = db.query(ActivityLog).order_by(ActivityLog.id.desc()).limit(10).all()

print("=== RECENT TELEMETRY LOGS STORED IN DATABASE ===")
for log in recent_logs:
    print(f"ID #{log.id} | Student: {log.student_id} | App: '{log.application_name}' | Title: '{log.window_title}' | Category: {log.category} | Time: {log.timestamp}")

db.close()
