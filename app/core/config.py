# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    BOT_TOKEN: str
    APP_URL: str
    DATABASE_URL: str

    class Config:
        env_file = ".env"

settings = Settings()