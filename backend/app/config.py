"""
Application configuration using pydantic-settings.
"""
from typing import List, Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Environment
    environment: str = "dev"

    # Database (snapdb - includes vector embeddings in snap_vec_ebd table)
    database_url: str = "postgresql+asyncpg://snapuser:snappassword@localhost:5433/snapagentdb"

    # JWT
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # File Upload
    max_file_size_mb: int = 10
    upload_dir: str = "/app/uploads"
    allowed_extensions: List[str] = [".pdf", ".txt", ".md", ".csv", ".docx", ".xls", ".xlsx"]

    # CORS
    cors_origins: str = "http://localhost:3001,http://localhost:5174,http://localhost:5175"

    @field_validator("cors_origins")
    @classmethod
    def parse_cors_origins(cls, v: str) -> List[str]:
        """Parse comma-separated CORS origins."""
        return [origin.strip() for origin in v.split(",")]

    # Server
    backend_host: str = "0.0.0.0"
    backend_port: int = 8001

    # Logging
    log_level: str = "DEBUG"

    # OpenRouter (primary LLM provider)
    openrouter_api_key: Optional[str] = None
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    # OpenAI (for embeddings)
    openai_api_key: Optional[str] = None
    openai_base_url: str = "https://api.openai.com/v1"

    # Encryption key for API keys (Fernet requires 32-byte base64-encoded key)
    # Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    encryption_key: str = "dev-encryption-key-change-in-production-32b="

    # ReAct Agent settings
    react_max_iterations: int = 5
    react_evaluation_threshold: float = 0.7


# Global settings instance
settings = Settings()
