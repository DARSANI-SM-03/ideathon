import os

class Settings:
    PROJECT_NAME: str = "StudIQ - AI-Powered Digital Academic Intelligence Platform"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    def __init__(self):
        self.ENV = os.getenv("STUDIQ_ENV", os.getenv("ENV", "development")).lower()
        secret = os.getenv("SECRET_KEY")
        if self.ENV == "production" and not secret:
            raise RuntimeError("CRITICAL SECURITY FAILURE: SECRET_KEY environment variable MUST be explicitly set in production!")
        self.SECRET_KEY = secret or "studiq_dev_only_secret_key_change_in_production_12345"
        raw_db_url = os.getenv("STUDIQ_DATABASE_URL") or os.getenv("DATABASE_URL") or "sqlite:///./studiq.db"
        if raw_db_url.startswith("postgres://"):
            raw_db_url = raw_db_url.replace("postgres://", "postgresql://", 1)
        self.DATABASE_URL = raw_db_url
        self.FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
        self.CORS_ORIGINS = os.getenv("ALLOWED_ORIGINS") or os.getenv("CORS_ORIGINS") or f"{self.FRONTEND_URL},http://localhost:5173,http://localhost:3000,http://127.0.0.1:3000"

settings = Settings()
