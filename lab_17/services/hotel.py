from typing import List, Optional

from database.models import Booking, Client, Room, RoomType
from database.repository import (
    BookingRepository,
    ClientRepository,
    NotFoundError,
    RoomRepository,
    RoomTypeRepository,
)


class BookingError(Exception):
    """Бизнес-ошибка: невозможная операция бронирования."""


class HotelService:
    """Бизнес-логика бота: поиск, бронирование, отмена, CRUD номеров."""

    def __init__(self, session,
                 rooms: Optional[RoomRepository] = None,
                 clients: Optional[ClientRepository] = None,
                 room_types: Optional[RoomTypeRepository] = None,
                 bookings: Optional[BookingRepository] = None):
        self._rooms = rooms or RoomRepository(session)
        self._clients = clients or ClientRepository(session)
        self._room_types = room_types or RoomTypeRepository(session)
        self._bookings = bookings or BookingRepository(session)

    # ---- клиенты ----
    def get_or_create_client(self, telegram_id: int, full_name: str) -> Client:
        return self._clients.get_or_create(telegram_id, full_name)

    # ---- номера ----
    def list_rooms(self) -> List[Room]:
        return self._rooms.list_all()

    def free_rooms(self, capacity: Optional[int] = None) -> List[Room]:
        return self._rooms.free_rooms(capacity)

    def search_rooms(self, query: str) -> List[Room]:
        return self._rooms.search(query)

    def get_room(self, room_id: int) -> Room:
        room = self._rooms.get(room_id)
        if room is None:
            raise NotFoundError(f"Номер с ID {room_id} не найден")
        return room

    def create_room(self, number: str, room_type_id: int, price: float,
                    capacity: int) -> Room:
        if price <= 0:
            raise BookingError("Цена должна быть положительной")
        if capacity <= 0:
            raise BookingError("Вместимость должна быть больше нуля")
        for room in self._rooms.list_all():
            if room.number.lower() == number.strip().lower():
                raise BookingError(f"Номер {number} уже существует")
        return self._rooms.create(number.strip(), room_type_id, price, capacity)

    def update_room(self, room_id: int, fields: dict) -> Room:
        if "price" in fields and fields["price"] is not None and fields["price"] <= 0:
            raise BookingError("Цена должна быть положительной")
        room = self._rooms.update(room_id, fields)
        if room is None:
            raise NotFoundError(f"Номер с ID {room_id} не найден")
        return room

    def delete_room(self, room_id: int) -> None:
        if not self._rooms.delete(room_id):
            raise NotFoundError(f"Номер с ID {room_id} не найден")

    # ---- бронирования ----
    def create_booking(self, telegram_id: int, room_id: int, check_in: str,
                       check_out: str) -> Booking:
        client = self.get_or_create_client(telegram_id, "Клиент")
        room = self.get_room(room_id)
        if room.status != Room.STATUS_FREE:
            raise BookingError(f"Номер {room.number} уже занят")
        try:
            from datetime import date
            start = date.fromisoformat(check_in)
            end = date.fromisoformat(check_out)
            nights = (end - start).days
        except ValueError:
            raise BookingError("Даты должны быть в формате ГГГГ-ММ-ДД")
        if nights <= 0:
            raise BookingError("Дата выезда должна быть позже даты заезда")
        total = round(room.price * nights, 2)
        booking = self._bookings.create(
            client.id, room.id, check_in, check_out, nights, total
        )
        self._rooms.set_status(room.id, Room.STATUS_BOOKED)
        return booking

    def cancel_booking(self, telegram_id: int, booking_id: int) -> Booking:
        booking = self._bookings.get(booking_id)
        if booking is None:
            raise NotFoundError(f"Бронирование с ID {booking_id} не найдено")
        client = self._clients.get_by_telegram(telegram_id)
        if client is None or booking.client_id != client.id:
            raise BookingError("Вы можете отменить только своё бронирование")
        self._rooms.set_status(booking.room_id, Room.STATUS_FREE)
        self._bookings.delete(booking_id)
        return booking

    def history(self, telegram_id: int) -> List[Booking]:
        client = self._clients.get_by_telegram(telegram_id)
        if client is None:
            return []
        return self._bookings.list_by_client(client.id)

    # ---- типы номеров ----
    def room_types(self) -> List[RoomType]:
        return self._room_types.list_all()

    def create_room_type(self, name: str) -> RoomType:
        room_type = RoomType(name=name.strip())
        session = self._room_types._session
        session.add(room_type)
        session.commit()
        return room_type

    def get_room_type(self, room_type_id: int) -> RoomType:
        room_type = self._room_types.get(room_type_id)
        if room_type is None:
            raise NotFoundError(f"Тип номера с ID {room_type_id} не найден")
        return room_type

    # ---- статистика для админа ----
    def statistics(self) -> dict:
        return {
            "rooms": len(self._rooms.list_all()),
            "clients": len(self._clients.list_all()),
            "bookings": len(self._bookings.list_by_client(0)) if False else
                sum(len(self._bookings.list_by_client(c.id)) for c in self._clients.list_all()),
        }