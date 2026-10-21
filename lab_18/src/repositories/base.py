from datetime import date
from typing import List, Optional

from src.models.room import Booking, BookingInterval, Guest, Room


class NotFoundError(Exception):
    """Объект не найден."""


class DuplicateError(Exception):
    """Попытка создать дубликат."""


class ValidationError(Exception):
    """Некорректные входные данные."""


class Repository:
    """Хранилище данных отеля (in-memory; интерфейс для SQLite-реализации)."""

    def __init__(self):
        self._rooms: dict[int, Room] = {}
        self._guests: dict[int, Guest] = {}
        self._bookings: dict[int, Booking] = {}
        self._next_room = 1
        self._next_guest = 1
        self._next_booking = 1

    # ---------- номера ----------
    def add_room(self, room: Room) -> Room:
        for existing in self._rooms.values():
            if existing.number == room.number:
                raise DuplicateError(f"Номер {room.number} уже существует")
        room.id = self._next_room
        self._next_room += 1
        self._rooms[room.id] = room
        return room

    def get_room(self, room_id: int) -> Optional[Room]:
        return self._rooms.get(room_id)

    def list_rooms(self) -> List[Room]:
        return list(self._rooms.values())

    def delete_room(self, room_id: int) -> bool:
        if room_id not in self._rooms:
            return False
        del self._rooms[room_id]
        return True

    def update_room_status(self, room_id: int, status: str) -> None:
        room = self._rooms.get(room_id)
        if room is not None:
            room.status = status

    # ---------- гости ----------
    def add_guest(self, guest: Guest) -> Guest:
        for existing in self._guests.values():
            if existing.email and existing.email == guest.email:
                raise DuplicateError(f"Гость с email {guest.email} уже существует")
        guest.id = self._next_guest
        self._next_guest += 1
        self._guests[guest.id] = guest
        return guest

    def get_guest(self, guest_id: int) -> Optional[Guest]:
        return self._guests.get(guest_id)

    def list_guests(self) -> List[Guest]:
        return list(self._guests.values())

    # ---------- бронирования ----------
    def add_booking(self, booking: Booking) -> Booking:
        booking.id = self._next_booking
        self._next_booking += 1
        self._bookings[booking.id] = booking
        return booking

    def get_booking(self, booking_id: int) -> Optional[Booking]:
        return self._bookings.get(booking_id)

    def list_bookings(self) -> List[Booking]:
        return list(self._bookings.values())

    def bookings_for_room(self, room_id: int) -> List[Booking]:
        return [b for b in self._bookings.values() if b.room_id == room_id]

    def delete_booking(self, booking_id: int) -> bool:
        if booking_id not in self._bookings:
            return False
        del self._bookings[booking_id]
        return True