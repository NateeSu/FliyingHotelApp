from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    # Application
    APP_NAME: str = "FlyingHotelApp"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # Security
    SECRET_KEY: str
    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # Telegram
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_ADMIN_GROUP_ID: Optional[str] = None
    TELEGRAM_RECEPTION_GROUP_ID: Optional[str] = None
    TELEGRAM_HOUSEKEEPING_GROUP_ID: Optional[str] = None
    TELEGRAM_MAINTENANCE_GROUP_ID: Optional[str] = None

    # Upload
    MAX_UPLOAD_SIZE: int = 5242880  # 5MB
    UPLOAD_DIR: str = "/app/uploads"

    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:80",
    ]

    # Timezone
    TZ: str = "Asia/Bangkok"

    # Room Settings (defaults, can be changed in system_settings)
    DEFAULT_TEMPORARY_STAY_HOURS: int = 3
    DEFAULT_CHECKIN_TIME: str = "13:00"
    DEFAULT_CHECKOUT_TIME: str = "12:00"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
