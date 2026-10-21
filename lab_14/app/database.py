import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


from collections.abc import Iterator

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:////Users/EER/Desktop/090303-ПИа-о24 Елисеева Е.Р./lab_14/hotel.db",
)


class Base(DeclarativeBase):
    pass


engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Iterator[Session]:
    """Dependency Injection: сессия SQLAlchemy на время одного запроса."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()