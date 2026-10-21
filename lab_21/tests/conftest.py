"""Фикстуры: тестовая in-memory БД, клиент TestClient, токены пользователя и администратора."""

import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["DATABASE_URL"] = f"sqlite:///{tempfile.mkdtemp()}/test.db"

from restaurant.api.dependencies import get_db  # noqa: E402
from restaurant.main import app  # noqa: E402
from restaurant.models.entities import Base, Customer  # noqa: E402
from restaurant.schemas.schemas import DishCreate  # noqa: E402
from restaurant.services.security import hash_password  # noqa: E402
from restaurant.services.services import DishService  # noqa: E402

USER_EMAIL = "user@example.com"
USER_PASSWORD = "secret123"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    testing_session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = testing_session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture()
def client(db_session):
    def override_db():
        yield db_session

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def admin(db_session) -> Customer:
    admin = Customer(
        email=ADMIN_EMAIL,
        name="Администратор",
        hashed_password=hash_password(ADMIN_PASSWORD),
        role="ADMIN",
    )
    db_session.add(admin)
    db_session.commit()
    return admin


def seed_dishes(db) -> None:
    service = DishService(db)
    for payload in [
        DishCreate(name="Борщ", price=350.0, description="Классический борщ"),
        DishCreate(name="Стейк", price=890.0, description="Говядина на гриле"),
        DishCreate(name="Паста", price=450.0, description="Паста карбонара"),
    ]:
        service.create(payload)


def register_and_login(client, email: str, password: str) -> str:
    client.post("/auth/register", json={"email": email, "name": "Тест", "password": password})
    resp = client.post("/auth/login", json={"email": email, "password": password})
    return resp.json()["access_token"]


@pytest.fixture()
def user_token(client) -> str:
    return register_and_login(client, USER_EMAIL, USER_PASSWORD)


@pytest.fixture()
def admin_token(client, admin) -> str:
    resp = client.post("/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    return resp.json()["access_token"]


def auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}
