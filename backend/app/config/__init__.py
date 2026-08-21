import os

class Settings:
    PROJECT_NAME: str = "StudIQ - AI-Powered Digital Academic Intelligence Platform"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    SECRET_KEY: str = os.getenv("SECRET_KEY", "studiq_production_secret_key_super_secure_987654321")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days for demo ease

    DATABASE_URL: str = os.getenv("STUDIQ_DATABASE_URL") or os.getenv("DATABASE_URL") or "sqlite:///./studiq.db"

settings = Settings()
