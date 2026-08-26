from fastapi import FastAPI  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
from app.config import settings
from app.database.session import engine
from app.database.base import Base
import app.models.monitoring    # Register monitoring models
import app.models.collaboration # Register collaboration models (Meeting, CounselingSession, Message)
from app.routers import (
    auth_router,
    student_router,
    admin_router,
    activity_router,
    academic_router,
    monitoring_router,
    report_router,
    notification_router,
    parent_router,
    mentor_router,
    onboarding_router,
    ai_router
)

from sqlalchemy import text  # type: ignore

# Auto-create tables on startup if not present
Base.metadata.create_all(bind=engine)

# Auto-migrate columns for students table if DB already exists
with engine.connect() as conn:
    cols_to_add = [
        ("status", "VARCHAR DEFAULT 'Pending Approval'"),
        ("monitoring_authorized", "BOOLEAN DEFAULT 0"),
        ("onboarding_completed", "BOOLEAN DEFAULT 0"),
        ("parent_email", "VARCHAR"),
        ("parent_phone", "VARCHAR")
    ]
    for col_name, col_type in cols_to_add:
        try:
            conn.execute(text(f"ALTER TABLE students ADD COLUMN {col_name} {col_type};"))
            conn.commit()
        except Exception:
            pass

    try:
        conn.execute(text("ALTER TABLE behavior_metric_records ADD COLUMN timestamp DATETIME;"))
        conn.commit()
    except Exception:
        pass

    try:
        conn.execute(text("ALTER TABLE activity_logs ADD COLUMN confidence FLOAT DEFAULT 0.95;"))
        conn.commit()
    except Exception:
        pass


app = FastAPI(

    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

from fastapi.responses import JSONResponse  # type: ignore
from fastapi import Request  # type: ignore
from app.config.logger import log_event

import os

# Configurable CORS origins (comma-separated list, e.g. "https://studiq-frontend.vercel.app,http://localhost:3000")
allowed_origins_raw = os.getenv("ALLOWED_ORIGINS", "https://studiq-frontend.onrender.com,http://localhost:5173,http://localhost:3000,http://localhost:8000,*")
allowed_origins = [origin.strip() for origin in allowed_origins_raw.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def global_exception_handling_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as exc:
        import traceback
        tb_str = traceback.format_exc()
        log_event("ERROR", f"Unhandled Server Exception on {request.url.path}: {str(exc)}\n{tb_str}", level="error")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": "An internal server error occurred. Please try again later."}
        )



from app.routers import (
    auth_router, onboarding_router, ai_router, student_router,
    admin_router, parent_router, mentor_router, activity_router,
    academic_router, monitoring_router, report_router, notification_router,
    system_router
)

# Include Routers
app.include_router(auth_router.router, prefix=settings.API_V1_STR)
app.include_router(onboarding_router.router, prefix=settings.API_V1_STR)
app.include_router(ai_router.router, prefix=settings.API_V1_STR)
app.include_router(student_router.router, prefix=settings.API_V1_STR)
app.include_router(admin_router.router, prefix=settings.API_V1_STR)
app.include_router(parent_router.router, prefix=settings.API_V1_STR)
app.include_router(mentor_router.router, prefix=settings.API_V1_STR)
app.include_router(activity_router.router, prefix=settings.API_V1_STR)
app.include_router(academic_router.router, prefix=settings.API_V1_STR)
app.include_router(monitoring_router.router, prefix=settings.API_V1_STR)
app.include_router(report_router.router, prefix=settings.API_V1_STR)
app.include_router(notification_router.router, prefix=settings.API_V1_STR)
app.include_router(system_router.router, prefix=settings.API_V1_STR)




@app.get("/health")
@app.get(f"{settings.API_V1_STR}/health")
def health_check():
    """Unauthenticated lightweight health check for cloud load balancers."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION
    }

@app.get("/")
def root():
    return {
        "message": "Welcome to StudIQ - AI-Powered Digital Academic Intelligence Platform API",
        "version": settings.PROJECT_VERSION,
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn  # type: ignore
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
