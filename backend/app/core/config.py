from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
import json

class Settings(BaseSettings):
    APP_NAME: str = "Tiffin Marketplace API"
    ENV: str = "development"
    SECRET_KEY: str = "change_me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/tiffin_marketplace"
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8501"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_origins(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

settings = Settings()
