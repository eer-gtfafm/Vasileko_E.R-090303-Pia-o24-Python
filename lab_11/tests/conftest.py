import os
import sys

import fakeredis
import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app  # noqa: E402
from cache import RoomCache  # noqa: E402
from database import Database, init_db  # noqa: E402
from repository import BookingRepository, GuestRepository, RoomRepository, ServiceRepository  # noqa: E402
from service import BookingService, RoomService  # noqa: E402


@pytest.fixture()
def db(tmp_path):
    database = Database(str(tmp_path / "test.db"))
    init_db(database, seed=True)
    yield database
    database.close()


@pytest.fixture()
def cache_client():
    return fakeredis.FakeRedis(decode_responses=True)


@pytest.fixture()
def cache(cache_client):
    return RoomCache(cache_client)


@pytest.fixture()
def room_service(db, cache):
    return RoomService(RoomRepository(db), cache)


@pytest.fixture()
def booking_service(db, cache):
    return BookingService(
        RoomRepository(db),
        GuestRepository(db),
        ServiceRepository(db),
        BookingRepository(db),
        cache,
    )


@pytest.fixture()
def app(tmp_path, cache_client):
    application = create_app(
        db_path=str(tmp_path / "app.db"), seed=True, cache_client=cache_client
    )
    application.config.update(TESTING=True)
    return application


@pytest.fixture()
def client(app):
    return app.test_client()
