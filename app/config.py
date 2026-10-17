import os
from typing import Optional
from pydantic_settings import BaseSettings

IS_VERCEL = bool(os.getenv("VERCEL"))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Excel Assistant"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-ai-excel-assistant-jwt-key-change-in-prod-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # SQL Database:
    # On Vercel serverless, /tmp is writable; locally and on Render, ./ai_excel.db or PostgreSQL
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:////tmp/ai_excel.db" if IS_VERCEL else "sqlite:///./ai_excel.db"
    )
    
    # LLM Settings
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", None)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", None)
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "auto")  # 'gemini', 'openai', or 'auto'
    
    # Directories
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "/tmp/uploads" if IS_VERCEL else os.path.join(BASE_DIR, "app", "uploads"))
    CHARTS_DIR: str = os.getenv("CHARTS_DIR", "/tmp/charts" if IS_VERCEL else os.path.join(BASE_DIR, "app", "static", "charts"))
    
    # Email / OTP Settings
    EMAIL_DEV_MODE: bool = True  # Logs OTP to console and returns in response for easy testing
    SMTP_HOST: Optional[str] = os.getenv("SMTP_HOST", None)
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER", None)
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD", None)
    FROM_EMAIL: str = os.getenv("FROM_EMAIL", "noreply@aiexcelassistant.local")
    
    model_config = {"env_file": ".env", "extra": "allow"}

settings = Settings()

try:
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.CHARTS_DIR, exist_ok=True)
except Exception:
    pass
