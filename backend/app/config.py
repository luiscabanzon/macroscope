from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "MacroScope API"
    app_version: str = "0.1.0"
    debug: bool = False

    # Database
    db_path: str = "macroscope.db"

    # Cache TTL configuration
    ttl_historical_days: int = 30
    ttl_recent_hours: int = 24
    ttl_high_freq_hours: int = 1

    # Public Demo Mode: when True, blocks upstream network fetches and serves purely from SQLite cache
    read_only_cache: bool = False

    # CORS
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]


settings = Settings()
