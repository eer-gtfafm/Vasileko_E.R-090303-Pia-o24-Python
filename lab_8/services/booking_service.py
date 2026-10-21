from typing import List
from interfaces.observer import Observer
from interfaces.pricing import PricingStrategy
from interfaces.repository import Repository
from models.entities import Booking, Event, Room
from models.enums import BookingStatus, EventType, RoomStatus, TariffType


# Бизнес-логика бронирования. Не зависит от UI, от способа хранения
# (Repository) и от конкретного алгоритма расчёта цены (Strategy).
class BookingService:
    def __init__(self, room_repo: Repository, booking_repo: Repository, strategy: PricingStrategy):
        self._room_repo = room_repo
        self._booking_repo = booking_repo
        self._strategy = strategy
        self._observers: List[Observer] = []

    # --- Observer: подписка на события ---
    def attach(self, observer: Observer) -> None:
        self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def _notify(self, event_type: EventType, message: str) -> None:
        event = Event(type=event_type, message=message)
        for observer in self._observers:
            observer.update(event)

    # --- Strategy: тариф меняется без изменения сервиса ---
    def set_strategy(self, strategy: PricingStrategy) -> None:
        self._strategy = strategy

    @property
    def tariff(self) -> TariffType:
        return self._strategy.tariff

    # --- Операции ---
    def calculate_price(self, room_id: int, days: int) -> float:
        room = self._get_room(room_id)
        self._validate_days(days)
        return self._strategy.calculate(room, days)

    def book(self, room_id: int, guest_name: str, days: int) -> Booking:
        room = self._get_room(room_id)
        self._validate_days(days)

        if room.status != RoomStatus.FREE:
            raise ValueError(f"Номер {room.number} недоступен (статус: {room.status.value})")

        total_cost = self._strategy.calculate(room, days)

        room.status = RoomStatus.BOOKED
        self._room_repo.update(room)

        booking = Booking(
            id=self._next_booking_id(),
            room_id=room.id,
            room_number=room.number,
            guest_name=guest_name,
            days=days,
            tariff=self._strategy.tariff,
            total_cost=total_cost,
        )
        self._booking_repo.add(booking)

        self._notify(
            EventType.BOOKING_CREATED,
            f"Гость {guest_name} забронировал номер {room.number} на {days} дн. "
            f"({self._strategy.tariff.value}), стоимость {total_cost:.2f} руб.",
        )
        return booking

    def cancel(self, booking_id: int) -> None:
        booking = self._get_booking(booking_id)
        if booking.status != BookingStatus.CREATED:
            raise ValueError(
                f"Нельзя отменить бронирование №{booking.id} (статус: {booking.status.value})"
            )

        room = self._get_room(booking.room_id)
        room.status = RoomStatus.FREE
        self._room_repo.update(room)

        booking.status = BookingStatus.CANCELLED
        self._booking_repo.update(booking)

        self._notify(
            EventType.BOOKING_CANCELLED,
            f"Бронирование №{booking.id} гостя {booking.guest_name} отменено, номер {room.number} свободен.",
        )

    def check_in(self, booking_id: int) -> None:
        booking = self._get_booking(booking_id)
        if booking.status != BookingStatus.CREATED:
            raise ValueError(
                f"Нельзя заселиться по бронированию №{booking.id} (статус: {booking.status.value})"
            )

        room = self._get_room(booking.room_id)
        room.status = RoomStatus.OCCUPIED
        self._room_repo.update(room)

        booking.status = BookingStatus.ACTIVE
        self._booking_repo.update(booking)

        self._notify(
            EventType.CHECK_IN,
            f"Гость {booking.guest_name} заселён в номер {room.number}.",
        )

    def check_out(self, booking_id: int) -> None:
        booking = self._get_booking(booking_id)
        if booking.status != BookingStatus.ACTIVE:
            raise ValueError(
                f"Нельзя выселиться по бронированию №{booking.id} (статус: {booking.status.value})"
            )

        room = self._get_room(booking.room_id)
        room.status = RoomStatus.FREE
        self._room_repo.update(room)

        booking.status = BookingStatus.COMPLETED
        self._booking_repo.update(booking)

        self._notify(
            EventType.CHECK_OUT,
            f"Гость {booking.guest_name} выселен из номера {room.number}, номер свободен.",
        )

    # --- Вспомогательные методы ---
    def add_room(self, room: Room) -> None:
        self._room_repo.add(room)

    def get_rooms(self) -> List[Room]:
        return self._room_repo.get_all()

    def get_bookings(self) -> List[Booking]:
        return self._booking_repo.get_all()

    def _get_room(self, room_id: int) -> Room:
        room = self._room_repo.get(room_id)
        if room is None:
            raise ValueError(f"Номер с ID {room_id} не найден")
        return room

    def _get_booking(self, booking_id: int) -> Booking:
        booking = self._booking_repo.get(booking_id)
        if booking is None:
            raise ValueError(f"Бронирование с ID {booking_id} не найдено")
        return booking

    @staticmethod
    def _validate_days(days: int) -> None:
        if days <= 0:
            raise ValueError("Количество дней должно быть больше 0")

    def _next_booking_id(self) -> int:
        bookings = self._booking_repo.get_all()
        return max((booking.id for booking in bookings), default=0) + 1
