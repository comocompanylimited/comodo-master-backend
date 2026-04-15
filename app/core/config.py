import json
import os
from typing import Any, List
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_URL: str = "postgresql://user:password@localhost:5432/comodo_master"

    # Zeabur individual Postgres vars
    POSTGRES_HOST: str = ""
    POSTGRES_PORT: str = "5432"
    POSTGRES_USER: str = ""
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""

    SECRET_KEY: str = "change-this-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080
    ENVIRONMENT: str = "development"

    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    @model_validator(mode="after")
    def assemble_database_url(self):
        # If Zeabur provides individual vars, build DATABASE_URL from them
        if self.POSTGRES_HOST and self.POSTGRES_USER and self.POSTGRES_DB:
            self.DATABASE_URL = (
                f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
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
print(f"DATABASE_URL host: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'unknown'}")
