from dataclasses import dataclass, field
from datetime import date
from typing import List


@dataclass
class Guest:
    """Гость отеля."""

    id: int
    full_name: str
    email: str = ""

    def __post_init__(self):
        self.full_name = self.full_name.strip()
        if not self.full_name:
            raise ValueError("Имя гостя не может быть пустым")
        self.email = self.email.strip()


@dataclass
class Room:
    """Гостиничный номер."""

    STATUS_FREE = "свободен"
    STATUS_BOOKED = "занят"

    id: int
    number: str
    price: float
    capacity: int
    status: str = STATUS_FREE

    def __post_init__(self):
        self.number = self.number.strip()
        if self.price <= 0:
            raise ValueError("Цена должна быть положительной")
        if self.capacity <= 0:
            raise ValueError("Вместимость должна быть больше нуля")


@dataclass
class BookingInterval:
    """Период бронирования с проверкой пересечений."""

    check_in: date
    check_out: date

    def __post_init__(self):
        if self.check_out <= self.check_in:
            raise ValueError("Дата выезда должна быть позже даты заезда")

    def overlaps(self, other: "BookingInterval") -> bool:
        return self.check_in < other.check_out and other.check_in < self.check_out


@dataclass
class Booking:
    """Бронирование номера гостем."""

    id: int
    room_id: int
    guest_id: int
    interval: BookingInterval
    nights: int = field(init=False)
    total: float = field(init=False)

    def __post_init__(self):
        self.nights = (self.interval.check_out - self.interval.check_in).days
        self.total = 0  # заполняется сервисом по цене номера

    def recompute(self, price_per_night: float) -> None:
        if price_per_night <= 0:
            raise ValueError("Цена номера должна быть положительной")
        self.total = round(self.nights * price_per_night, 2)