import json
import os
from typing import Any, List
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_URL: str = "postgresql://user:password@localhost:5432/comodo_master"

    # Zeabur exposes these — note POSTGRES_USERNAME not POSTGRES_USER
    POSTGRES_URI: str = ""
    POSTGRES_HOST: str = ""
    POSTGRES_PORT: str = "5432"
    POSTGRES_USERNAME: str = ""
    POSTGRES_USER: str = ""        # fallback alias
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""
    POSTGRES_DATABASE: str = ""    # alternate Zeabur name

    SECRET_KEY: str = "change-this-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080
    ENVIRONMENT: str = "development"

    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    @model_validator(mode="after")
    def assemble_database_url(self):
        # 1. Use POSTGRES_URI if Zeabur provides it directly
        if self.POSTGRES_URI:
            self.DATABASE_URL = self.POSTGRES_URI
            return self
        # 2. Build from individual vars (Zeabur uses POSTGRES_USERNAME)
        user = self.POSTGRES_USERNAME or self.POSTGRES_USER
        db = self.POSTGRES_DB or self.POSTGRES_DATABASE
        if self.POSTGRES_HOST and user and db:
            self.DATABASE_URL = (
                f"postgresql://{user}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{db}"
            )
        return self

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> List[str]:
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, ValueError):
                return [i.strip() for i in v.split(",")]
        return v


settings = Settings()
print(f"[DB] connecting to: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}")
