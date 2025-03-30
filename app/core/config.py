import os
from pathlib import Path
from pydantic import AnyHttpUrl, PostgresDsn, field_validator
from pydantic_settings import BaseSettings
from typing import List, Optional, Union


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    POSTGRES_SERVER: str
    POSTGRES_PORT: str = "5432"
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: Optional[PostgresDsn] = None

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], values) -> any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.data.get("POSTGRES_USER"),
            password=values.data.get("POSTGRES_PASSWORD"),
            host=values.data.get("POSTGRES_SERVER"),
            port=int(values.data.get("POSTGRES_PORT")),
            path=f"{values.data.get('POSTGRES_DB') or ''}",
        )

    YANDEX_CLIENT_ID: str
    YANDEX_CLIENT_SECRET: str
    YANDEX_REDIRECT_URI: AnyHttpUrl

    FIRST_SUPERUSER_YANDEX_ID: str

    UPLOADS_DIR: str = "./uploads"

    @field_validator("UPLOADS_DIR", mode="after")
    @classmethod
    def create_uploads_dir(cls, v: str) -> str:
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return str(path.resolve()) # Return absolute path

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# --- Yandex OAuth URLs ---
YANDEX_AUTH_URL = "https://oauth.yandex.ru/authorize"
YANDEX_TOKEN_URL = "https://oauth.yandex.ru/token"
YANDEX_USERINFO_URL = "https://login.yandex.ru/info"