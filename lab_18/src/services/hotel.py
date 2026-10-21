from datetime import date
from typing import List, Optional

from src.models.room import Booking, BookingInterval, Guest, Room
from src.repositories.base import DuplicateError, NotFoundError, ValidationError


class RoomService:
    """Бизнес-логика гостиницы: CRUD, бронирование, поиск, валидация."""

    def __init__(self, repository):
        self._repository = repository

    # ---------- номера ----------
    def create_room(self, number: str, price: float, capacity: int) -> Room:
        if not number.strip():
            raise ValidationError("Номер комнаты не может быть пустым")
        if price <= 0:
            raise ValidationError("Цена должна быть положительной")
        if capacity <= 0:
            raise ValidationError("Вместимость должна быть больше нуля")
        room = Room(id=0, number=number.strip(), price=price, capacity=capacity)
        return self._repository.add_room(room)

    def get_room(self, room_id: int) -> Room:
        room = self._repository.get_room(room_id)
        if room is None:
            raise NotFoundError(f"Номер с ID {room_id} не найден")
        return room

    def list_rooms(self) -> List[Room]:
        return self._repository.list_rooms()

    def delete_room(self, room_id: int) -> None:
        if not self._repository.delete_room(room_id):
            raise NotFoundError(f"Номер с ID {room_id} не найден")

    def find_free_rooms(self, capacity: Optional[int] = None) -> List[Room]:
        """Поиск свободных номеров, при необходимости — по вместимости."""
        rooms = [r for r in self._repository.list_rooms() if r.status == Room.STATUS_FREE]
        if capacity is not None:
            if capacity <= 0:
                raise ValidationError("Вместимость должна быть больше нуля")
            rooms = [r for r in rooms if r.capacity >= capacity]
        return rooms

    # ---------- гости ----------
    def register_guest(self, full_name: str, email: str = "") -> Guest:
        if not full_name.strip():
            raise ValidationError("Имя гостя не может быть пустым")
        return self._repository.add_guest(Guest(id=0, full_name=full_name, email=email))

    def get_guest(self, guest_id: int) -> Guest:
        guest = self._repository.get_guest(guest_id)
        if guest is None:
            raise NotFoundError(f"Гость с ID {guest_id} не найден")
        return guest

    # ---------- бронирование ----------
    def book_room(self, room_id: int, guest_id: int,
                  check_in: date, check_out: date) -> Booking:
        room = self.get_room(room_id)
        guest = self.get_guest(guest_id)
        try:
            interval = BookingInterval(check_in, check_out)
        except ValueError as error:
            raise ValidationError(str(error))

        for booking in self._repository.bookings_for_room(room_id):
            if booking.interval.overlaps(interval):
                raise ValidationError(
                    f"Номер {room.number} уже занят на этот период"
                )

        booking = Booking(id=0, room_id=room_id, guest_id=guest_id, interval=interval)
        booking.recompute(room.price)
        self._repository.add_booking(booking)

        room.status = Room.STATUS_BOOKED
        self._repository.update_room_status(room.id, Room.STATUS_BOOKED)
        return booking

    def cancel_booking(self, booking_id: int) -> Booking:
        booking = self._repository.get_booking(booking_id)
        if booking is None:
            raise NotFoundError(f"Бронирование с ID {booking_id} не найдено")
        room = self.get_room(booking.room_id)
        self._repository.delete_booking(booking_id)
        # если других активных бронирований нет — номер снова свободен
        if not self._repository.bookings_for_room(room.id):
            room.status = Room.STATUS_FREE
            self._repository.update_room_status(room.id, Room.STATUS_FREE)
        return booking

    def get_booking(self, booking_id: int) -> Booking:
        booking = self._repository.get_booking(booking_id)
        if booking is None:
            raise NotFoundError(f"Бронирование с ID {booking_id} не найдено")
        return booking

    def bookings_list(self) -> List[Booking]:
        return self._repository.list_bookings()