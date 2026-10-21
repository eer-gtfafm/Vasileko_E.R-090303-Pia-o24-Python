"""Подключение к базе данных (SQLAlchemy)."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from restaurant.config.settings import get_settings
from restaurant.models.entities import Base

settings = get_settings()

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def create_all() -> None:
    Base.metadata.create_all(bind=engine)


def drop_all() -> None:
    Base.metadata.drop_all(bind=engine)
