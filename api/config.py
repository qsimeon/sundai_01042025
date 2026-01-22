from pathlib import Path

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables"""

    # API Configuration
    api_title: str = "Sundai Bot API"
    api_version: str = "1.0.0"
    api_key: str = "dev-key-change-in-production"

    # Database
    database_path: str = "/opt/sundai-bot/database/sundai.db"

    # API Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 2

    # External Services
    mastodon_api_url: str = "https://techhub.social"
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    openai_api_key: str = ""
    replicate_api_token: str = ""

    # Logging
    log_level: str = "INFO"
    log_dir: str = "/opt/sundai-bot/logs"

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )

    def get_log_path(self) -> Path:
        """Get path to API log file"""
        log_dir = Path(self.log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir / "api.log"

    def get_db_path(self) -> Path:
        """Get path to database file"""
        db_path = Path(self.database_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return db_path


settings = Settings()
