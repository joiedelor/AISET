"""
AISET Configuration Settings
DO-178C Traceability: REQ-CONFIG-002
Purpose: Centralized configuration management using Pydantic

This module provides type-safe configuration management for the entire application.
All settings are validated at startup to ensure system integrity.
"""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """
    Application settings with DO-178C compliance features.

    Traceability:
    - REQ-CONFIG-002: Configuration management
    - REQ-SEC-001: Security configuration
    - REQ-AUDIT-001: Audit trail configuration
    """

    # Database Settings
    database_url: str = Field(..., env="DATABASE_URL")
    db_echo: bool = Field(False, env="DB_ECHO")

    # AI Service Settings
    anthropic_api_key: str = Field("", env="ANTHROPIC_API_KEY")
    anthropic_model: str = Field("claude-3-sonnet-20240229", env="ANTHROPIC_MODEL")
    lm_studio_url: str = Field("http://localhost:1234/v1", env="LM_STUDIO_URL")
    lm_studio_model: str = Field("mistral-7b-instruct", env="LM_STUDIO_MODEL")
    ai_service: str = Field("claude", env="AI_SERVICE")

    # Security Settings
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = Field("HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # Application Settings
    app_name: str = Field("AISET", env="APP_NAME")
    app_version: str = Field("0.1.0", env="APP_VERSION")
    debug: bool = Field(False, env="DEBUG")
    log_level: str = Field("INFO", env="LOG_LEVEL")

    # CORS Settings
    allowed_origins: str = Field(
        "http://localhost:5173,http://localhost:3000",
        env="ALLOWED_ORIGINS"
    )

    # Export Settings
    export_templates_dir: str = Field("./templates", env="EXPORT_TEMPLATES_DIR")
    export_output_dir: str = Field("./exports", env="EXPORT_OUTPUT_DIR")

    # DO-178C Compliance Settings
    enable_audit_trail: bool = Field(True, env="ENABLE_AUDIT_TRAIL")
    require_approval_workflow: bool = Field(True, env="REQUIRE_APPROVAL_WORKFLOW")
    traceability_strict_mode: bool = Field(True, env="TRACEABILITY_STRICT_MODE")

    @property
    def cors_origins(self) -> List[str]:
        """Get parsed CORS origins as a list."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    @field_validator("ai_service")
    @classmethod
    def validate_ai_service(cls, v):
        """Ensure AI service is valid."""
        if v not in ["claude", "lmstudio"]:
            raise ValueError("ai_service must be 'claude' or 'lmstudio'")
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )


# Global settings instance
settings = Settings()
