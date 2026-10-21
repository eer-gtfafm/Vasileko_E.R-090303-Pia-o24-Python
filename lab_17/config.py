import os

from pydantic_settings import BaseSettings, SettingsConfigDict

from pydantic import Field


class Settings(BaseSettings):
    """Конфигурация бота: токен и строка БД задаются через переменные окружения."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    BOT_TOKEN: str = Field(..., description="Токен Telegram-бота")
    DATABASE_URL: str = "sqlite:///hotel_bot.db"

    @property
    def bot_token(self) -> str:
        return self.BOT_TOKEN

    @property
    def database_url(self) -> str:
        return self.DATABASE_URL


def get_settings() -> Settings:
    return Settings()