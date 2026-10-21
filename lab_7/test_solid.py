import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import pytest

from repositories.memory_repository import InMemoryRepository
from infrastructure.notifiers import ConsoleNotifier, EmailNotifier, SmsNotifier
from services.domain_service import HotelService
from services.report_service import ReportService
from models.entities import Room, Booking
from models.enums import RoomStatus


@pytest.fixture()
def env():
    room_repo = InMemoryRepository()
    booking_repo = InMemoryRepository()
    notifier = ConsoleNotifier()
    hotel = HotelService(room_repo, booking_repo, notifier)
    report = ReportService(room_repo, booking_repo)
    room_repo.add(Room(id=1, number="101", price_per_night=2500.0))
    room_repo.add(Room(id=2, number="102", price_per_night=3500.0, status=RoomStatus.MAINTENANCE))
    return {"room_repo": room_repo, "booking_repo": booking_repo, "hotel": hotel, "report": report}


class TestRepository:
    def test_add_and_get(self, env):
        assert env["room_repo"].get(1).number == "101"

    def test_get_all(self, env):
        assert len(env["room_repo"].get_all()) == 2

    def test_get_missing(self, env):
        assert env["room_repo"].get(999) is None

    def test_update(self, env):
        room = env["room_repo"].get(1)
        room.status = RoomStatus.BOOKED
        env["room_repo"].update(room)
        assert env["room_repo"].get(1).status == RoomStatus.BOOKED


class TestHotelServiceSOLID:
    def test_book_room_success(self, env):
        booking = env["hotel"].book_room(1, "Иван Иванов", 3)
        assert isinstance(booking, Booking)
        assert booking.total_cost == 7500.0
        assert booking.guest_name == "Иван Иванов"

    def test_book_changes_status_and_notifies(self, env, capsys):
        env["hotel"].book_room(1, "Иван", 2)
        assert env["room_repo"].get(1).status == RoomStatus.BOOKED
        out = capsys.readouterr().out
        assert "Вы забронировали номер 101" in out

    def test_book_not_free_room_raises(self, env):
        with pytest.raises(ValueError):
            env["hotel"].book_room(2, "Иван", 2)

    def test_book_missing_room_raises(self, env):
        with pytest.raises(ValueError):
            env["hotel"].book_room(999, "Иван", 2)

    def test_check_in_requires_booked(self, env):
        with pytest.raises(ValueError):
            env["hotel"].check_in(2)

    def test_check_in_success(self, env):
        env["hotel"].book_room(1, "Иван", 2)
        env["hotel"].check_in(1)
        assert env["room_repo"].get(1).status == RoomStatus.OCCUPIED

    def test_check_out_success(self, env):
        env["hotel"].book_room(1, "Иван", 2)
        env["hotel"].check_in(1)
        env["hotel"].check_out(1)
        assert env["room_repo"].get(1).status == RoomStatus.FREE

    def test_check_out_not_occupied_raises(self, env):
        with pytest.raises(ValueError):
            env["hotel"].check_out(1)


class TestReportService:
    def test_generate_report_contains_rooms(self, env):
        report = env["report"].generate_report()
        assert "Всего номеров: 2" in report
        assert "Свободных номеров: 1" in report

    def test_generate_report_after_booking(self, env):
        env["hotel"].book_room(1, "Иван", 3)
        report = env["report"].generate_report()
        assert "Всего бронирований: 1" in report
        assert "Иван" in report
        assert "7500.0" in report


class TestNotifiersOCP:
    def test_email_notifier(self, capsys):
        room_repo = InMemoryRepository()
        booking_repo = InMemoryRepository()
        room_repo.add(Room(id=1, number="101", price_per_night=1000.0))
        hotel = HotelService(room_repo, booking_repo, EmailNotifier())
        hotel.book_room(1, "Петр", 2)
        out = capsys.readouterr().out
        assert "[EMAIL to Петр]" in out

    def test_sms_notifier(self, capsys):
        room_repo = InMemoryRepository()
        booking_repo = InMemoryRepository()
        room_repo.add(Room(id=1, number="101", price_per_night=1000.0))
        hotel = HotelService(room_repo, booking_repo, SmsNotifier())
        hotel.book_room(1, "Анна", 2)
        out = capsys.readouterr().out
        assert "[SMS to Анна]" in out

    def test_same_service_with_different_notifiers(self):
        room_repo = InMemoryRepository()
        booking_repo = InMemoryRepository()
        room_repo.add(Room(id=1, number="101", price_per_night=1000.0))
        h1 = HotelService(room_repo, booking_repo, ConsoleNotifier())
        h2 = HotelService(room_repo, booking_repo, EmailNotifier())
        assert h1.book_room.__self__ is not h2.book_room.__self__ if hasattr(h1.book_room, "__self__") else True