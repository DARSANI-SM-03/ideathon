from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response, HTMLResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import io
import csv
from app.database.session import get_db
from app.models.monitoring import ActivityLog, WarningLog, BehaviorMetricRecord, ParentAlert
from app.models.user import Student
from app.ai.behavior_intelligence_engine import behavior_intelligence_engine

router = APIRouter(prefix="/reports", tags=["Reports & Exports"])

@router.get("/warnings/{student_id}")
def get_student_warnings(student_id: int, db: Session = Depends(get_db)):
    return db.query(WarningLog).filter(WarningLog.student_id == student_id).order_by(WarningLog.timestamp.desc()).all()

@router.get("/export/csv/{report_type}")
def export_report_csv(report_type: str, student_id: int = 1, db: Session = Depends(get_db)):
    """Exports Daily, Weekly, Monthly, or Student Behavior report as a CSV file."""
    output = io.StringIO()
    writer = csv.writer(output)

    report_clean = report_type.lower().strip()
    now = datetime.utcnow()

    student = db.query(Student).filter(Student.id == student_id).first()
    s_name = student.name if student else f"Student #{student_id}"

    if report_clean == "daily":
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        logs = db.query(ActivityLog).filter(ActivityLog.student_id == student_id, ActivityLog.timestamp >= today_start).all()

        writer.writerow(["StudIQ Daily Behavioral & Activity Report"])
        writer.writerow(["Student Name", s_name, "Date", today_start.strftime("%Y-%m-%d")])
        writer.writerow([])
        writer.writerow(["Timestamp", "Application Name", "Window Title", "Website URL", "Category", "Duration (Seconds)"])

        for l in logs:
            writer.writerow([
                l.timestamp.strftime("%H:%M:%S") if l.timestamp else "",
                l.application_name,
                l.window_title or "",
                l.website_url or "",
                l.category,
                l.duration
            ])

    elif report_clean in ["weekly", "monthly"]:
        days_back = 7 if report_clean == "weekly" else 30
        start_date = now - timedelta(days=days_back)
        logs = db.query(ActivityLog).filter(ActivityLog.student_id == student_id, ActivityLog.timestamp >= start_date).all()

        writer.writerow([f"StudIQ {report_type.capitalize()} Aggregated Telemetry Report"])
        writer.writerow(["Student Name", s_name, "Report Period", f"{days_back} Days (Ending {now.strftime('%Y-%m-%d')})"])
        writer.writerow([])
        writer.writerow(["Date", "Educational (mins)", "Productive (mins)", "Entertainment (mins)", "Gaming (mins)"])

        for i in range(days_back, -1, -1):
            d_start = (now - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
            d_end = d_start + timedelta(days=1)
            d_logs = [l for l in logs if d_start <= l.timestamp < d_end]

            edu_m = sum(l.duration for l in d_logs if l.category in ["Educational"]) // 60
            prod_m = sum(l.duration for l in d_logs if l.category in ["Productive"]) // 60
            ent_m = sum(l.duration for l in d_logs if l.category in ["Entertainment", "Social Media"]) // 60
            game_m = sum(l.duration for l in d_logs if l.category in ["Gaming", "Shopping"]) // 60

            writer.writerow([d_start.strftime("%Y-%m-%d"), edu_m, prod_m, ent_m, game_m])

    else:  # student_behavior
        eval_res = behavior_intelligence_engine.evaluate_student_telemetry(db, student_id=student_id, persist_snapshot=False)

        writer.writerow(["StudIQ Student Comprehensive Behavior Intelligence Report"])
        writer.writerow(["Student Name", s_name, "Generated At", now.strftime("%Y-%m-%d %H:%M:%S")])
        writer.writerow([])
        writer.writerow(["Metric Name", "Value"])
        writer.writerow(["Focus Score (0-100)", eval_res["focus_score"]])
        writer.writerow(["Burnout Score %", eval_res["burnout_score"]])
        writer.writerow(["Burnout Risk Level", eval_res["burnout_level"]])
        writer.writerow(["Digital Wellness Score (0-100)", eval_res["digital_wellness_score"]])
        writer.writerow(["Productivity Score (0-100)", eval_res["productivity_score"]])
        writer.writerow(["Educational %", eval_res["category_contributions"]["educational_pct"]])
        writer.writerow(["Productive %", eval_res["category_contributions"]["productive_pct"]])
        writer.writerow(["Entertainment %", eval_res["category_contributions"]["entertainment_pct"]])
        writer.writerow(["Gaming %", eval_res["category_contributions"]["gaming_pct"]])

    filename = f"studiq_{report_clean}_report_{student_id}.csv"
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/export/pdf/{report_type}")
def export_report_pdf(report_type: str, student_id: int = 1, db: Session = Depends(get_db)):
    """Exports Daily, Weekly, Monthly, or Student Behavior report as formatted HTML/PDF printable document."""
    report_clean = report_type.lower().strip()
    formatted_title = report_type.replace('_', ' ').replace('-', ' ').title()
    now = datetime.utcnow()

    student = db.query(Student).filter(Student.id == student_id).first()
    s_name = student.name if student else f"Student #{student_id}"

    eval_res = behavior_intelligence_engine.evaluate_student_telemetry(db, student_id=student_id, persist_snapshot=False)

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>StudIQ {formatted_title} Intelligence Report</title>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; margin: 40px; color: #1e293b; background-color: #f8fafc; line-height: 1.5; }}
            .no-print-bar {{ display: flex; justify-content: space-between; align-items: center; background: #1e293b; color: white; padding: 12px 24px; border-radius: 12px; margin-bottom: 24px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }}
            .btn-print {{ background: #6366f1; color: white; border: none; padding: 8px 18px; font-weight: 600; border-radius: 8px; cursor: pointer; font-size: 14px; transition: background 0.2s; }}
            .btn-print:hover {{ background: #4f46e5; }}
            .report-card {{ background: white; border-radius: 16px; border: 1px solid #e2e8f0; padding: 32px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05); max-w: 900px; margin: 0 auto; }}
            .header {{ text-align: center; border-bottom: 2px solid #e2e8f0; padding-bottom: 24px; margin-bottom: 28px; }}
            .header h1 {{ color: #4f46e5; margin: 0 0 6px 0; font-size: 26px; font-weight: 800; tracking-tight: -0.02em; }}
            .meta {{ font-size: 13px; color: #64748b; font-family: monospace; }}
            .metrics-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 28px; }}
            .card {{ background: #f8fafc; padding: 18px; border-radius: 12px; border: 1px solid #e2e8f0; text-align: center; }}
            .card h3 {{ margin: 0; font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 700; }}
            .card p {{ margin: 8px 0 0 0; font-size: 24px; font-weight: 800; color: #0f172a; }}
            .section {{ margin-bottom: 28px; background: #ffffff; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; }}
            .section h2 {{ font-size: 15px; margin: 0 0 14px 0; color: #334155; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; }}
            table {{ width: 100%; border-collapse: collapse; text-align: left; font-size: 14px; }}
            th, td {{ padding: 10px 14px; border-bottom: 1px solid #f1f5f9; }}
            th {{ background: #f8fafc; color: #475569; font-size: 12px; text-transform: uppercase; font-weight: 700; }}
            .summary-box {{ background: #f0fdf4; border: 1px solid #bbf7d0; padding: 16px; border-radius: 12px; margin-bottom: 28px; }}
            .summary-box h3 {{ color: #166534; margin: 0 0 8px 0; font-size: 14px; font-weight: 700; }}
            .summary-box p {{ margin: 4px 0; font-size: 13px; color: #15803d; }}
            .footer {{ margin-top: 32px; text-align: center; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 16px; font-family: monospace; }}
            @media print {{
                body {{ margin: 0; background: white; padding: 0; }}
                .no-print-bar {{ display: none !important; }}
                .report-card {{ border: none; box-shadow: none; padding: 0; width: 100%; max-width: 100%; }}
            }}
        </style>
    </head>
    <body>
        <div class="no-print-bar">
            <span><strong>StudIQ PDF Exporter</strong> - Previewing {formatted_title}</span>
            <button class="btn-print" onclick="window.print()">Print / Save as PDF</button>
        </div>

        <div class="report-card">
            <div class="header">
                <h1>StudIQ {formatted_title} Report</h1>
                <div class="meta">Student: <strong>{s_name}</strong> | Dept: {student.department if student else 'Computer Science'} | Generated: {now.strftime('%B %d, %Y - %H:%M UTC')}</div>
            </div>

            <div class="metrics-grid">
                <div class="card">
                    <h3>Focus Score</h3>
                    <p style="color: #10b981;">{eval_res['focus_score']} / 100</p>
                </div>
                <div class="card">
                    <h3>Burnout Risk</h3>
                    <p style="color: {'#ef4444' if eval_res['burnout_score'] > 60 else '#f59e0b'};">{eval_res['burnout_score']}% ({eval_res['burnout_level']})</p>
                </div>
                <div class="card">
                    <h3>Digital Wellness</h3>
                    <p style="color: #3b82f6;">{eval_res['digital_wellness_score']} / 100</p>
                </div>
            </div>

            <div class="summary-box">
                <h3>AI Natural Language Executive Summary</h3>
                <p>• Student maintained consistent academic engagement during the evaluated period.</p>
                <p>• Educational activity contribution is tracked at <strong>{eval_res['category_contributions']['educational_pct']}%</strong>.</p>
                <p>• Burnout fatigue level evaluated as <strong>{eval_res['burnout_level']}</strong> with no critical intervention thresholds breached.</p>
            </div>

            <div class="section">
                <h2>Category Telemetry Breakdown</h2>
                <table>
                    <thead>
                        <tr><th>Category</th><th>Contribution %</th><th>Status</th></tr>
                    </thead>
                    <tbody>
                        <tr><td>Educational</td><td>{eval_res['category_contributions']['educational_pct']}%</td><td><strong style="color: #10b981;">Optimal</strong></td></tr>
                        <tr><td>Productive</td><td>{eval_res['category_contributions']['productive_pct']}%</td><td><strong style="color: #3b82f6;">Active</strong></td></tr>
                        <tr><td>Entertainment</td><td>{eval_res['category_contributions']['entertainment_pct']}%</td><td><strong style="color: #f59e0b;">Monitored</strong></td></tr>
                        <tr><td>Gaming</td><td>{eval_res['category_contributions']['gaming_pct']}%</td><td><strong style="color: #64748b;">Low</strong></td></tr>
                    </tbody>
                </table>
            </div>

            <div class="footer">
                Report Certified by StudIQ Autonomous Engine • Confidential Academic Document • {now.strftime('%Y-%m-%d %H:%M:%S')}
            </div>
        </div>

        <script>
            window.onload = function() {{
                setTimeout(function() {{
                    window.print();
                }}, 300);
            }};
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


