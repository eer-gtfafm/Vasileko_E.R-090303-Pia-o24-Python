import sys
from datetime import date
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest  # noqa: E402

from src.models.room import Guest, Room  # noqa: E402
from src.services.hotel import RoomService  # noqa: E402


class TestPatchUsage:
    def test_patch_repository_get_room(self):
        """patch заменяет метод репозитория на время теста."""
        with patch("src.repositories.sqlite.SqliteRepository.get_room") as mocked:
            from src.repositories.sqlite import SqliteRepository
            from src.services.hotel import RoomService

            repo = SqliteRepository(":memory:")
            mocked.return_value = Room(1, "101", 2500.0, 2)

            room = RoomService(repo).get_room(1)

            assert room.number == "101"
            mocked.assert_called_once_with(1)
            repo.close()

    def test_patch_service_create_room(self):
        """patch заменяет метод сервиса переданной функцией."""
        with patch("src.services.hotel.RoomService.create_room") as mocked:
            mocked.side_effect = lambda number, price, capacity: Room(42, number, price, capacity)

            room = RoomService(None).create_room("301", 4200.0, 4)

            assert room.id == 42
            assert room.number == "301"
            mocked.assert_called_once_with("301", 4200.0, 4)


class TestMockAssertions:
    def test_mock_called_with_correct_args(self):
        repository = MockRepositoryWithLog()
        service = RoomService(repository)
        service.get_room(7)

        assert repository.get_room_calls == [7]

    def test_mock_assert_called_once(self):
        repository = MockRepositoryWithLog()
        service = RoomService(repository)

        service.get_room(1)
        repository.assert_get_room_called_once_with(1)


class MockRepositoryWithLog:
    """Простая in-memory имитация репозитория с журналом вызовов."""

    def __init__(self):
        self.get_room_calls = []

    def get_room(self, room_id):
        self.get_room_calls.append(room_id)
        return Room(room_id, "101", 2500.0, 2)

    def get_guest(self, guest_id):
        return Guest(guest_id, "Иванов")

    def list_rooms(self):
        return []

    def list_guests(self):
        return []

    def bookings_for_room(self, room_id):
        return []

    def add_room(self, room):
        room.id = 1
        return room

    def add_guest(self, guest):
        guest.id = 1
        return guest

    def add_booking(self, booking):
        booking.id = 1
        return booking

    def get_booking(self, booking_id):
        return None

    def list_bookings(self):
        return []

    def delete_booking(self, booking_id):
        return True

    def delete_room(self, room_id):
        return False

    def assert_get_room_called_once_with(self, room_id):
        assert self.get_room_calls == [room_id], self.get_room_calls


class TestBookingDateValidation:
    @pytest.mark.parametrize(
        "check_in, check_out, nights",
        [
            (date(2026, 12, 1), date(2026, 12, 2), 1),
            (date(2026, 12, 1), date(2026, 12, 10), 9),
            (date(2026, 1, 31), date(2026, 2, 2), 2),
        ],
    )
    def test_nights_calculation(self, check_in, check_out, nights):
        from src.models.room import Booking, BookingInterval

        booking = Booking(0, 1, 1, BookingInterval(check_in, check_out))

        assert booking.nights == nights

    @pytest.mark.parametrize(
        "check_in, check_out",
        [
            (date(2026, 12, 5), date(2026, 12, 1)),
            (date(2026, 12, 1), date(2026, 12, 1)),
        ],
    )
    def test_invalid_interval(self, check_in, check_out):
        from src.models.room import BookingInterval

        with pytest.raises(ValueError):
            BookingInterval(check_in, check_out)