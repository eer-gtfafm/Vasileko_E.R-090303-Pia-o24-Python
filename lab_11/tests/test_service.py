import sqlite3

import pytest

from exceptions import RoomNotAvailableError, ValidationError
from models import Booking
from repository import BookingRepository


def test_cache_aside(room_service, cache):
    first = room_service.get_room(1)
    second = room_service.get_room(1)

    assert first == second
    assert cache.misses == 1
    assert cache.hits == 1
    cached_ttl = cache.ttl(1)
    assert 0 < cached_ttl <= 60


def test_cache_invalidated_on_patch(room_service, cache):
    room_service.get_room(1)
    assert cache.misses == 1

    room_service.patch_room(1, {"price_per_night": 2600.0})
    assert cache.ttl(1) in (-2, -1, 0) or cache.get(1) is None

    updated = room_service.get_room(1)
    assert updated["price_per_night"] == 2600.0
    assert cache.misses == 2


def test_create_booking_transaction(booking_service, db):
    booking = booking_service.create_booking({
        "room_id": 1,
        "guest_id": 1,
        "check_in": "2026-12-01",
        "check_out": "2026-12-03",
        "services": [{"service_id": 1, "quantity": 2}],
    })

    assert booking["total_price"] == 5000.0 + 1000.0
    assert len(booking["services"]) == 1

    room = db.query_one("SELECT status FROM rooms WHERE id = 1")
    assert room["status"] == "занят"


def test_booking_unavailable_room(booking_service):
    with pytest.raises(RoomNotAvailableError):
        booking_service.create_booking({
            "room_id": 2,
            "guest_id": 1,
            "check_in": "2026-12-01",
            "check_out": "2026-12-03",
            "services": [],
        })


def test_booking_validation(booking_service):
    with pytest.raises(ValidationError):
        booking_service.create_booking({
            "room_id": 1,
            "guest_id": 1,
            "check_in": "2026-12-05",
            "check_out": "2026-12-01",
            "services": [],
        })


def test_transaction_rollback(db):
    repository = BookingRepository(db)
    booking = Booking(None, 1, 1, "2026-12-01", "2026-12-03", 5000.0)

    with pytest.raises(sqlite3.IntegrityError):
        repository.create(booking, [{"service_id": 9999, "quantity": 1}])

    assert db.query_one("SELECT COUNT(*) AS count FROM bookings")["count"] == 6
    assert db.query_one("SELECT COUNT(*) AS count FROM booking_services")["count"] == 8
    assert db.query_one("SELECT status FROM rooms WHERE id = 1")["status"] == "свободен"


def test_room_validation(room_service):
    with pytest.raises(ValidationError):
        room_service.create_room({"number": "101", "room_type": "люкс",
                                  "price_per_night": 5000, "capacity": 2})
