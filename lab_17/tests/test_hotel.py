import pytest

from services.hotel import BookingError, HotelService, NotFoundError


class TestRoomCrud:
    def test_create_room(self, filled):
        room = filled.create_room("301", 2, 4200.0, 4)

        assert room.number == "301"
        assert room.price == 4200.0
        assert room.capacity == 4
        assert room.status == "свободен"

    def test_get_room(self, filled):
        room = filled.get_room(1)

        assert room.number == "101"

    def test_get_missing_room(self, filled):
        with pytest.raises(NotFoundError):
            filled.get_room(999)

    def test_update_room(self, filled):
        updated = filled.update_room(1, {"price": 2700.0})

        assert updated.price == 2700.0
        assert filled.get_room(1).price == 2700.0

    def test_update_room_invalid_price(self, filled):
        with pytest.raises(BookingError):
            filled.update_room(1, {"price": -100})

    def test_delete_room(self, filled):
        filled.delete_room(1)

        with pytest.raises(NotFoundError):
            filled.get_room(1)

    def test_duplicate_room_number(self, filled):
        with pytest.raises(BookingError):
            filled.create_room("101", 1, 3000.0, 2)

    def test_create_room_invalid_capacity(self, filled):
        with pytest.raises(BookingError):
            filled.create_room("401", 1, 3000.0, 0)


class TestSearchAndFree:
    def test_free_rooms_list(self, filled):
        assert len(filled.free_rooms()) == 2

    def test_free_rooms_capacity_filter(self, filled):
        rooms = filled.free_rooms(capacity=3)

        assert [r.number for r in rooms] == ["201"]

    def test_search_by_number(self, filled):
        rooms = filled.search_rooms("101")

        assert [r.number for r in rooms] == ["101"]

    def test_search_by_type_name(self, filled):
        rooms = filled.search_rooms("люкс")

        assert [r.number for r in rooms] == ["201"]

    def test_search_no_results(self, filled):
        assert filled.search_rooms("zzz") == []


class TestBooking:
    def test_create_booking(self, filled):
        booking = filled.create_booking(111, 1, "2026-12-01", "2026-12-04")

        assert booking.nights == 3
        assert booking.total == 7500.0
        assert filled.get_room(1).status == "занят"
        assert len(filled.free_rooms()) == 1

    def test_booking_bad_dates(self, filled):
        with pytest.raises(BookingError):
            filled.create_booking(111, 1, "2026-12-05", "2026-12-01")

    def test_booking_invalid_date_format(self, filled):
        with pytest.raises(BookingError):
            filled.create_booking(111, 1, "05.12.2026", "01.12.2026")

    def test_booking_busy_room(self, filled):
        filled.create_booking(111, 1, "2026-12-01", "2026-12-04")

        with pytest.raises(BookingError):
            filled.create_booking(222, 1, "2026-12-05", "2026-12-07")

    def test_history(self, filled):
        filled.create_booking(111, 1, "2026-12-01", "2026-12-04")
        filled.create_booking(111, 2, "2026-12-01", "2026-12-03")

        assert len(filled.history(111)) == 2

    def test_cancel_booking(self, filled):
        booking = filled.create_booking(111, 1, "2026-12-01", "2026-12-04")
        filled.cancel_booking(111, booking.id)

        assert filled.get_room(1).status == "свободен"
        assert len(filled.history(111)) == 0

    def test_cancel_foreign_booking(self, filled):
        booking = filled.create_booking(111, 1, "2026-12-01", "2026-12-04")

        with pytest.raises(BookingError):
            filled.cancel_booking(222, booking.id)


class TestClients:
    def test_get_or_create_client(self, filled):
        client = filled.get_or_create_client(123, "Иванов Иван")

        assert client.full_name == "Иванов Иван"
        assert filled.get_or_create_client(123, "Иванов Иван").id == client.id

    def test_statistics(self, filled):
        filled.create_booking(111, 1, "2026-12-01", "2026-12-04")
        stats = filled.statistics()

        assert stats["rooms"] == 2
        assert stats["bookings"] == 1