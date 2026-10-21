import sqlite3
from datetime import date
from typing import Any, Dict, List, Optional

from cache import RoomCache
from exceptions import (
    BookingError,
    GuestNotFoundError,
    RoomInUseError,
    RoomNotAvailableError,
    RoomNotFoundError,
    ValidationError,
)
from models import Booking, Room
from repository import BookingRepository, GuestRepository, RoomRepository, ServiceRepository
from schemas import parse_booking_payload, parse_room_payload


class RoomService:
    def __init__(self, repository: RoomRepository, cache: Optional[RoomCache] = None):
        self._repository = repository
        self._cache = cache

    def list_rooms(self, filters: Dict[str, Any]) -> List[dict]:
        return self._repository.list(filters)

    # Cache-aside для чтения одного номера
    def get_room(self, room_id: int) -> dict:
        if self._cache is not None:
            cached = self._cache.get(room_id)
            if cached is not None:
                return cached

        room = self._repository.get(room_id)
        if room is None:
            raise RoomNotFoundError(room_id)

        if self._cache is not None:
            self._cache.set(room_id, room)
        return room

    def create_room(self, payload: Any) -> dict:
        data = parse_room_payload(payload)
        if self._repository.get_by_number(data["number"]) is not None:
            raise ValidationError(f"Номер {data['number']} уже существует")
        room = Room(
            id=None,
            number=data["number"],
            room_type=data["room_type"],
            price_per_night=data["price_per_night"],
            capacity=data["capacity"],
            status=data.get("status", "свободен"),
        )
        return self._repository.create(room)

    def replace_room(self, room_id: int, payload: Any) -> dict:
        self.get_room(room_id)
        data = parse_room_payload(payload)
        room = self._repository.update(room_id, data)
        self._invalidate(room_id)
        return room

    def patch_room(self, room_id: int, payload: Any) -> dict:
        self.get_room(room_id)
        data = parse_room_payload(payload, partial=True)
        room = self._repository.update(room_id, data)
        self._invalidate(room_id)
        return room

    def delete_room(self, room_id: int) -> None:
        try:
            deleted = self._repository.delete(room_id)
        except sqlite3.IntegrityError:
            raise RoomInUseError(room_id)
        if not deleted:
            raise RoomNotFoundError(room_id)
        self._invalidate(room_id)

    def available_rooms(self, capacity: Optional[int] = None,
                        date_from: Optional[str] = None, date_to: Optional[str] = None) -> List[dict]:
        return self._repository.available(capacity=capacity, date_from=date_from, date_to=date_to)

    def _invalidate(self, room_id: int) -> None:
        if self._cache is not None:
            self._cache.invalidate(room_id)


class BookingService:
    def __init__(self, room_repository: RoomRepository, guest_repository: GuestRepository,
                 service_repository: ServiceRepository, booking_repository: BookingRepository,
                 cache: Optional[RoomCache] = None):
        self._rooms = room_repository
        self._guests = guest_repository
        self._services = service_repository
        self._bookings = booking_repository
        self._cache = cache

    def list_bookings(self) -> List[dict]:
        return self._bookings.list()

    def get_booking(self, booking_id: int) -> dict:
        booking = self._bookings.get(booking_id)
        if booking is None:
            raise BookingError(f"Бронирование с ID {booking_id} не найдено")
        return booking

    # Бизнес-операция, требующая транзакции:
    # бронирование + услуги + смена статуса номера.
    def create_booking(self, payload: Any) -> dict:
        data = parse_booking_payload(payload)

        room = self._rooms.get(data["room_id"])
        if room is None:
            raise RoomNotFoundError(data["room_id"])
        if room["status"] != "свободен":
            raise RoomNotAvailableError(room["number"])

        if self._guests.get(data["guest_id"]) is None:
            raise GuestNotFoundError(data["guest_id"])

        nights = self._nights(data["check_in"], data["check_out"])
        services_total = 0.0
        for item in data["services"]:
            service = self._services.get(item["service_id"])
            if service is None:
                raise ValidationError(f"Услуга с ID {item['service_id']} не найдена")
            services_total += service["price"] * item["quantity"]

        booking = Booking(
            id=None,
            room_id=data["room_id"],
            guest_id=data["guest_id"],
            check_in=data["check_in"],
            check_out=data["check_out"],
            total_price=round(room["price_per_night"] * nights + services_total, 2),
        )
        created = self._bookings.create(booking, data["services"])

        if self._cache is not None:
            self._cache.invalidate(data["room_id"])
        return created

    @staticmethod
    def _nights(check_in: str, check_out: str) -> int:
        start = date.fromisoformat(check_in)
        end = date.fromisoformat(check_out)
        nights = (end - start).days
        if nights <= 0:
            raise ValidationError("Дата выезда должна быть позже даты заезда")
        return nights
