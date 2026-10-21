from dataclasses import dataclass
from typing import ClassVar, Optional
from .enums import BookingStatus, EventType, RoomStatus, RoomType, TariffType


# Базовая сущность "номер". Конкретные типы номеров задают свои
# характеристики через ClassVar, поэтому конструктор у всех одинаковый.
@dataclass
class Room:
    id: int
    number: str
    base_price: float
    status: RoomStatus = RoomStatus.FREE

    room_type: ClassVar[RoomType] = RoomType.STANDARD
    capacity: ClassVar[int] = 2
    coefficient: ClassVar[float] = 1.0

    def __post_init__(self):
        if self.base_price <= 0:
            raise ValueError("Базовая цена номера должна быть больше 0")

    @property
    def price_per_night(self) -> float:
        return round(self.base_price * self.coefficient, 2)

    def description(self) -> str:
        return (
            f"№{self.number} ({self.room_type.value}, до {self.capacity} гостей), "
            f"{self.price_per_night:.2f} руб./ночь, статус: {self.status.value}"
        )


@dataclass
class StandardRoom(Room):
    room_type: ClassVar[RoomType] = RoomType.STANDARD
    capacity: ClassVar[int] = 2
    coefficient: ClassVar[float] = 1.0


@dataclass
class SuiteRoom(Room):
    room_type: ClassVar[RoomType] = RoomType.SUITE
    capacity: ClassVar[int] = 2
    coefficient: ClassVar[float] = 2.5


@dataclass
class FamilyRoom(Room):
    room_type: ClassVar[RoomType] = RoomType.FAMILY
    capacity: ClassVar[int] = 4
    coefficient: ClassVar[float] = 1.6


@dataclass
class Booking:
    id: int
    room_id: int
    room_number: str
    guest_name: str
    days: int
    tariff: TariffType
    total_cost: float
    status: BookingStatus = BookingStatus.CREATED

    def description(self) -> str:
        return (
            f"№{self.id}: гость {self.guest_name}, номер {self.room_number}, "
            f"{self.days} дн., {self.tariff.value}, {self.total_cost:.2f} руб., "
            f"статус: {self.status.value}"
        )


# Событие, которое сервис рассылает наблюдателям
@dataclass
class Event:
    type: EventType
    message: str
