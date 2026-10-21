import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import Database  # noqa: E402
from services.hotel import BookingError, HotelService, NotFoundError  # noqa: E402


@pytest.fixture()
def service():
    database = Database(f"sqlite:///{tempfile.mkdtemp()}/test_bot.db")
    database.create_tables()
    yield HotelService(database.session())
    database.engine.dispose()


@pytest.fixture()
def filled(service):
    service.create_room_type("Стандартный")
    service.create_room_type("Люкс")
    service.create_room("101", 1, 2500.0, 2)
    service.create_room("201", 2, 6000.0, 3)
    return service


def get_free_ids(service):
    return [r.id for r in service.free_rooms()]