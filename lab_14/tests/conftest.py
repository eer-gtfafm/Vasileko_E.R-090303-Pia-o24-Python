import os
import sys
import tempfile

import fakeredis
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["DATABASE_URL"] = f"sqlite:///{tempfile.mkdtemp()}/test_hotel.db"

from app.database import Base, SessionLocal, engine  # noqa: E402
from app.services.room import RoomCache, RoomService  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def create_schema():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client():
    from app.main import app

    app.state.cache_client = fakeredis.FakeRedis(decode_responses=True)
    from app.routers.rooms import get_service

    def override():
        db = SessionLocal()
        cache = RoomCache(app.state.cache_client)
        from app.repositories.room import RoomRepository

        yield RoomService(RoomRepository(db), cache)

    app.dependency_overrides[get_service] = override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def sample_room() -> dict:
    return {
        "number": "705",
        "room_type": "люкс",
        "floor": 7,
        "capacity": 2,
        "price": 8000.0,
        "available": True,
        "amenities": ["wi-fi", "мини-бар"],
    }