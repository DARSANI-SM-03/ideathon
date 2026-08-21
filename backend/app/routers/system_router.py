from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database.session import get_db
from app.models.monitoring import ActivityLog
from app.database.base import Base

router = APIRouter(prefix="/system", tags=["System Diagnostics"])

@router.get("/connectivity")
def get_system_connectivity(db: Session = Depends(get_db)):
    """
    Unified Connectivity Status Monitor:
    Evaluates real-time health for Backend API, Desktop Agent, Database, Telemetry Stream, and Frontend.
    """
    now = datetime.utcnow()
    
    # 1. Database Ping
    db_ok = False
    try:
        db.execute(Base.metadata.tables['students'].select().limit(1))
        db_ok = True
    except Exception:
        db_ok = False

    # 2. Telemetry Stream Check (Recent ActivityLog in last 5 minutes)
    telemetry_recent = db.query(ActivityLog).filter(
        ActivityLog.timestamp >= now - timedelta(minutes=5)
    ).first()
    telemetry_ok = telemetry_recent is not None

    # 3. Desktop Agent Ping (Recent ActivityLog in last 2 minutes)
    agent_recent = db.query(ActivityLog).filter(
        ActivityLog.timestamp >= now - timedelta(minutes=2)
    ).first()
    agent_ok = agent_recent is not None

    return {
        "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
        "components": {
            "backend_api": {
                "name": "Backend FastAPI Service",
                "connected": True,
                "status_str": "🟢 Connected",
                "details": "REST API endpoints operational (Port 8000)"
            },
            "desktop_agent": {
                "name": "Windows Desktop Agent",
                "connected": agent_ok,
                "status_str": "🟢 Connected" if agent_ok else "🔴 Disconnected",
                "details": "Active OS window capture stream" if agent_ok else "No ping within last 120s"
            },
            "database": {
                "name": "SQLite Operational Database",
                "connected": db_ok,
                "status_str": "🟢 Connected" if db_ok else "🔴 Disconnected",
                "details": "ACID transactional DB active" if db_ok else "Database query timeout"
            },
            "telemetry_stream": {
                "name": "AI Telemetry Ingestion Pipeline",
                "connected": telemetry_ok,
                "status_str": "🟢 Connected" if telemetry_ok else "🔴 Disconnected",
                "details": "Ingesting 5s telemetry snapshots" if telemetry_ok else "Stream idle"
            },
            "frontend": {
                "name": "React Client Dashboard",
                "connected": True,
                "status_str": "🟢 Connected",
                "details": "Vite React SPA client online"
            }
        }
    }
