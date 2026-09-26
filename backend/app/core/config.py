from pathlib import Path
from typing import List
from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    PROJECT_NAME: str = "Cardiopulmonary Monitoring and Early Risk Detection System"
    API_V1_STR: str = "/api/v1"
    APP_ENV: str = "development"
    DATABASE_URL: str = Field(..., description="PostgreSQL asyncpg URL; configure through environment/.env")
    AUTO_START_SIMULATOR: bool = True
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]

    # Telemetry and Ingestion
    DEFAULT_PATIENT_ID: str = "PATIENT-001"
    DEFAULT_DEVICE_ID: str = "SIM-DEV-01"
    
    # Clinical Warning Thresholds (NEWS2 & Cardiopulmonary Early Warning)
    HR_LOW_CRITICAL: float = 40.0
    HR_LOW_WARNING: float = 50.0
    HR_HIGH_WARNING: float = 100.0
    HR_HIGH_CRITICAL: float = 130.0
    
    SPO2_CRITICAL: float = 90.0
    SPO2_WARNING: float = 94.0
    
    RR_LOW_CRITICAL: float = 8.0
    RR_LOW_WARNING: float = 11.0
    RR_HIGH_WARNING: float = 21.0
    RR_HIGH_CRITICAL: float = 25.0

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    @field_validator("DATABASE_URL")
    @classmethod
    def require_postgresql(cls, value: str) -> str:
        if not value.startswith("postgresql+asyncpg://"):
            raise ValueError("DATABASE_URL must use PostgreSQL with the asyncpg driver; SQLite fallback is disabled")
        return value

    @field_validator("APP_ENV")
    @classmethod
    def validate_app_env(cls, value: str) -> str:
        if value not in {"development", "production", "test"}:
            raise ValueError("APP_ENV must be development, production, or test")
        return value

    @model_validator(mode="after")
    def validate_production_origins(self):
        if self.APP_ENV == "production":
            if not self.CORS_ORIGINS or any("localhost" in origin or "127.0.0.1" in origin or origin == "*" for origin in self.CORS_ORIGINS):
                raise ValueError("Production requires explicit deployed frontend origins in CORS_ORIGINS")
        return self

settings = Settings()
