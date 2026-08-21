import os

def resolve_backend_url() -> str:
    raw_url = os.getenv("STUDIQ_BACKEND_URL", "http://localhost:8000")
    clean = raw_url.strip().rstrip("/")
    if clean.endswith("/api/v1/monitoring/update"):
        return clean
    elif clean.endswith("/api/v1"):
        return f"{clean}/monitoring/update"
    else:
        return f"{clean}/api/v1/monitoring/update"

class AgentConfig:
    # StudIQ FastAPI Backend URL
    BACKEND_URL: str = resolve_backend_url()
    HEARTBEAT_URL: str = os.getenv("STUDIQ_HEARTBEAT_URL", BACKEND_URL.replace("/update", "/heartbeat"))

    # Polling & Telemetry Frequency
    POLL_INTERVAL_SECONDS: int = 5

    # Student Identification
    STUDENT_ID: int = int(os.getenv("STUDIQ_STUDENT_ID", "1"))
    STUDENT_CODE: str = os.getenv("STUDIQ_STUDENT_CODE", "STU-2026-001")

    # Privacy Protection Lists (STRICTLY PROHIBITED ACCESS)
    PROHIBITED_SCOPE = [
        "Gallery",
        "Photos",
        "Passwords",
        "Bank Applications",
        "Private Files",
        "Messages",
        "Clipboard"
    ]
