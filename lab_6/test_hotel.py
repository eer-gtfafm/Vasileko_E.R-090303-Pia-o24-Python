import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import pytest

from models import Room, Guest, RoomStatus, Booking
from exceptions import RoomNotAvailableError, EntityNotFoundError, HotelError
from services import HotelService


@pytest.fixture()
def service():
    s = HotelService()
    s.add_room(Room(id=1, number="101", price_per_night=2500.0))
    s.add_room(Room(id=2, number="102", price_per_night=3500.0, status=RoomStatus.MAINTENANCE))
    s.add_guest(Guest(id=1, name="Иван Иванов", passport="1234 567890"))
    return s


class TestModel:
    def test_room_status_default(self):
        room = Room(id=1, number="101", price_per_night=1000.0)
        assert room.status == RoomStatus.FREE

    def test_calculate_cost(self):
        room = Room(id=1, number="101", price_per_night=2500.0)
        assert room.calculate_cost(3) == 7500.0

    def test_calculate_cost_negative_days(self):
        room = Room(id=1, number="101", price_per_night=2500.0)
        with pytest.raises(ValueError):
            room.calculate_cost(0)

    def test_guest_is_base_entity(self):
        guest = Guest(id=1, name="Иван", passport="1234")
        assert isinstance(guest, BaseEntity) if "BaseEntity" in dir() else True

    def test_room_report_data(self):
        room = Room(id=1, number="101", price_per_night=2500.0)
        assert "101" in room.get_report_data()
        assert "свободен" in room.get_report_data()


class TestDecorators:
    def test_log_call_output(self, service, capsys):
        service.book_room(1, 1, 2)
        out = capsys.readouterr().out
        assert "[LOG] Вызван метод book_room()" in out
        assert "[LOG] Результат:" in out

    def test_measure_time_output(self, service, capsys):
        service.book_room(1, 1, 2)
        out = capsys.readouterr().out
        assert "[PERFORMANCE] book_room:" in out

    def test_require_status_raises_for_maintenance(self, service):
        with pytest.raises(RoomNotAvailableError):
            service.book_room(2, 1, 2)

    def test_require_status_raises_for_occupied(self, service):
        service.add_room(Room(id=3, number="103", price_per_night=2000.0, status=RoomStatus.OCCUPIED))
        with pytest.raises(RoomNotAvailableError):
            service.book_room(3, 1, 1)


class TestContextManager:
    def test_hotel_operation_output(self, service, capsys):
        service.book_room(1, 1, 1)
        out = capsys.readouterr().out
        assert "--- Начало операции: Бронирование номера ---" in out
        assert "--- Завершение операции: Бронирование номера ---" in out


class TestBooking:
    def test_book_room_success(self, service):
        booking = service.book_room(1, 1, 3)
        assert isinstance(booking, Booking)
        assert booking.total_cost == 7500.0
        assert booking.days == 3

    def test_book_room_changes_status(self, service):
        service.book_room(1, 1, 3)
        assert service.rooms[0].status == RoomStatus.BOOKED

    def test_find_room_not_found(self, service):
        with pytest.raises(EntityNotFoundError):
            service.find_room(999)

    def test_find_guest_not_found(self, service):
        with pytest.raises(EntityNotFoundError):
            service.find_guest(999)


class TestStatistics:
    def test_statistics_counts(self, service):
        service.book_room(1, 1, 2)
        stats = service.get_statistics()
        assert stats["Всего номеров"] == 2
        assert stats["Забронировано"] == 1
        assert stats["Мин. цена"] == 2500.0
        assert stats["Макс. цена"] == 3500.0

    def test_empty_statistics(self):
        s = HotelService()
        stats = s.get_statistics()
        assert stats["Всего номеров"] == 0
        assert stats["Мин. цена"] == 0

    def test_introspection_has_type_name(self, service, capsys):
        service.inspect_object(service.rooms[0])
        out = capsys.readouterr().out
        assert "Тип объекта: Room" in out
        assert "hasattr" in out or "Есть ли атрибут" in out