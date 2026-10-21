import pytest

from models import Room
from repository import BookingRepository, RoomRepository


@pytest.fixture()
def rooms(db):
    return RoomRepository(db)


def test_create_and_get_room(rooms, db):
    created = rooms.create(Room(None, "401", "стандартный", 3000.0, 2))

    assert created["id"] == 11
    assert rooms.get(11)["number"] == "401"
    assert rooms.get_by_number("401")["id"] == 11


def test_update_and_delete_room(rooms, db):
    created = rooms.create(Room(None, "401", "стандартный", 3000.0, 2))
    rooms.update(created["id"], {"price_per_night": 2600.0})
    assert rooms.get(created["id"])["price_per_night"] == 2600.0

    assert rooms.delete(created["id"]) is True
    assert rooms.get(created["id"]) is None
    assert rooms.delete(created["id"]) is False


def test_available_query(rooms, db):
    available = rooms.available(capacity=4)

    numbers = [room["number"] for room in available]
    assert numbers == ["301", "304"]
    assert all(room["status"] == "свободен" for room in available)


def test_available_with_dates(rooms, db):
    busy = rooms.available(date_from="2026-10-01", date_to="2026-10-03")
    numbers = [room["number"] for room in busy]

    assert "102" not in numbers
    assert "101" in numbers


def test_bookings_with_join(db):
    bookings = BookingRepository(db).list()

    assert len(bookings) == 6
    assert bookings[0]["room_number"] == "102"
    assert bookings[0]["guest_name"] == "Иванов Иван Иванович"
