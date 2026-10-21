import os


class Config:
    """Настройки приложения через переменные окружения."""
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "sqlite:////Users/EER/Desktop/090303-ПИа-о24 Елисеева Е.Р./lab_15/restaurant.db",
    )
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024