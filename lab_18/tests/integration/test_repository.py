import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest  # noqa: E402

from src.models.room import Guest, Room  # noqa: E402
from src.repositories.base import DuplicateError, NotFoundError, ValidationError  # noqa: E402
from src.repositories.sqlite import SqliteRepository  # noqa: E402
from src.services.hotel import RoomService  # noqa: E402


@pytest.fixture()
def repository(tmp_path):
    repo = SqliteRepository(str(tmp_path / "hotel_test.db"))
    yield repo
    repo.close()


@pytest.fixture()
def service(repository):
    return RoomService(repository)


def test_integration_full_scenario(repository, service):
    """Интеграционный тест: Service → Repository → SQLite, полный цикл."""
    room = service.create_room("101", 2500.0, 2)
    guest = service.register_guest("Иванов Иван", "ivanov@example.com")

    booking = service.book_room(room.id, guest.id, date(2026, 12, 1), date(2026, 12, 4))

    assert booking.total == 7500.0
    assert service.get_room(room.id).status == "занят"
    assert len(service.bookings_list()) == 1

    service.cancel_booking(booking.id)

    assert service.get_room(room.id).status == "свободен"
    assert service.bookings_list() == []


def test_integration_repository_persistence(repository, service):
    """Интеграционный тест: данные сохраняются в SQLite и читаются обратно."""
    room = service.create_room("201", 6000.0, 3)

    loaded = repository.get_room(room.id)

    assert loaded.number == "201"
    assert loaded.price == 6000.0

    repository.add_guest(Guest(id=0, full_name="Петрова Анна", email="petrova@example.com"))
    guests = repository.list_guests()
    assert len(guests) == 1
    assert guests[0].email == "petrova@example.com"


def test_integration_overlap_enforced_by_service(repository, service):
    room = service.create_room("101", 2500.0, 2)
    guest = service.register_guest("Иванов", "i@example.com")
    service.book_room(room.id, guest.id, date(2026, 12, 1), date(2026, 12, 5))

    with pytest.raises(ValidationError):
        service.book_room(room.id, guest.id, date(2026, 12, 4), date(2026, 12, 8))


def test_integration_duplicate_room(repository):
    service = RoomService(repository)
    service.create_room("101", 2500.0, 2)

    with pytest.raises(DuplicateError):
        service.create_room("101", 2500.0, 2)


def test_integration_delete_missing(repository):
    assert repository.delete_room(999) is False
    assert repository.delete_booking(999) is False