import sys
from datetime import date
from pathlib import Path
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest  # noqa: E402

from src.models.room import Room, Guest, BookingInterval, Booking  # noqa: E402
from src.repositories.base import DuplicateError, NotFoundError, ValidationError  # noqa: E402
from src.services.hotel import RoomService  # noqa: E402


@pytest.fixture()
def mock_repository():
    return Mock()


@pytest.fixture()
def service(mock_repository):
    return RoomService(mock_repository)


class TestCreateRoom:
    def test_create_room_valid(self, service):
        mock_repository = service._repository
        mock_repository.add_room.side_effect = lambda room: room

        room = service.create_room("101", 2500.0, 2)

        assert room.number == "101"
        assert room.price == 2500.0
        assert room.capacity == 2
        mock_repository.add_room.assert_called_once()

    def test_create_room_empty_number(self, service):
        with pytest.raises(ValidationError):
            service.create_room("", 2500.0, 2)

    @pytest.mark.parametrize("price", [0, -10, -2500])
    def test_create_room_non_positive_price(self, service, price):
        with pytest.raises(ValidationError):
            service.create_room("101", price, 2)

    @pytest.mark.parametrize("capacity", [0, -1, -100])
    def test_create_room_non_positive_capacity(self, service, capacity):
        with pytest.raises(ValidationError):
            service.create_room("101", 2500.0, capacity)

    def test_create_room_duplicate(self, service):
        mock_repository = service._repository
        mock_repository.add_room.side_effect = DuplicateError("уже существует")

        with pytest.raises(DuplicateError):
            service.create_room("101", 2500.0, 2)


class TestFindFreeRooms:
    def test_find_free_rooms(self, service):
        rooms = [Room(1, "101", 2500.0, 2, "свободен"), Room(2, "201", 6000.0, 3, "занят")]
        service._repository.list_rooms.return_value = rooms

        free = service.find_free_rooms()

        assert [r.number for r in free] == ["101"]

    def test_find_free_rooms_with_capacity(self, service):
        rooms = [Room(1, "101", 2500.0, 2), Room(2, "201", 6000.0, 4)]
        service._repository.list_rooms.return_value = rooms

        free = service.find_free_rooms(capacity=4)

        assert [r.number for r in free] == ["201"]

    @pytest.mark.parametrize("capacity", [0, -5])
    def test_find_free_rooms_invalid_capacity(self, service, capacity):
        service._repository.list_rooms.return_value = []
        with pytest.raises(ValidationError):
            service.find_free_rooms(capacity=capacity)


class TestGetRoom:
    def test_get_room(self, service):
        service._repository.get_room.return_value = Room(1, "101", 2500.0, 2)

        room = service.get_room(1)

        assert room.number == "101"
        service._repository.get_room.assert_called_once_with(1)

    def test_get_missing_room(self, service):
        service._repository.get_room.return_value = None

        with pytest.raises(NotFoundError):
            service.get_room(99)


class TestBooking:
    def test_book_room_recomputes_total(self, service):
        service._repository.get_room.return_value = Room(1, "101", 2500.0, 2)
        service._repository.get_guest.return_value = Guest(1, "Иванов")
        service._repository.bookings_for_room.return_value = []
        service._repository.add_booking.side_effect = lambda b: b

        booking = service.book_room(1, 1, date(2026, 12, 1), date(2026, 12, 4))

        assert booking.nights == 3
        assert booking.total == 7500.0

    def test_book_room_overlapping_rejected(self, service):
        existing = Booking(
            1, 1, 1,
            BookingInterval(date(2026, 12, 1), date(2026, 12, 5)),
        )
        service._repository.get_room.return_value = Room(1, "101", 2500.0, 2)
        service._repository.get_guest.return_value = Guest(1, "Иванов")
        service._repository.bookings_for_room.return_value = [existing]

        with pytest.raises(ValidationError, match="уже занят"):
            service.book_room(1, 1, date(2026, 12, 4), date(2026, 12, 7))

    def test_book_room_bad_interval(self, service):
        service._repository.get_room.return_value = Room(1, "101", 2500.0, 2)
        service._repository.get_guest.return_value = Guest(1, "Иванов")
        service._repository.bookings_for_room.return_value = []

        with pytest.raises(ValidationError):
            service.book_room(1, 1, date(2026, 12, 5), date(2026, 12, 1))

    def test_book_room_missing_room(self, service):
        service._repository.get_room.return_value = None

        with pytest.raises(NotFoundError):
            service.book_room(99, 1, date(2026, 12, 1), date(2026, 12, 2))

    def test_cancel_booking_frees_room(self, service):
        old_booking = Booking(
            5, 1, 1,
            BookingInterval(date(2026, 12, 1), date(2026, 12, 4)),
        )
        old_booking.recompute(2500.0)
        service._repository.get_booking.return_value = old_booking
        service._repository.get_room.return_value = Room(1, "101", 2500.0, 2)
        service._repository.bookings_for_room.return_value = []

        cancelled = service.cancel_booking(5)

        assert cancelled.id == 5
        service._repository.delete_booking.assert_called_once_with(5)

    def test_cancel_missing_booking(self, service):
        service._repository.get_booking.return_value = None

        with pytest.raises(NotFoundError):
            service.cancel_booking(99)