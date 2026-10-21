from dataclasses import dataclass
from enum import Enum
from typing import Optional
from exceptions import RoomNotAvailableError
from protocols import Reportable

# Перечисление 
class RoomStatus(Enum):
    FREE = "свободен"
    OCCUPIED = "занят"
    BOOKED = "забронирован"
    MAINTENANCE = "на обслуживании"

# Базовый класс 
@dataclass
class BaseEntity:
    id: int

# Специализированный класс 1: Гость
@dataclass
class Guest(BaseEntity):
    name: str
    passport: str

# Специализированный класс 2: Номер 
@dataclass
class Room(BaseEntity):
    number: str
    price_per_night: float
    status: RoomStatus = RoomStatus.FREE

    # Реализация протокола Reportable (структурная типизация)
    def get_report_data(self) -> str:
        return f"Номер {self.number}, Цена: {self.price_per_night} руб., Статус: {self.status.value}"

    # Дополнительная операция (расчёт стоимости проживания)
    def calculate_cost(self, days: int) -> float:
        if days <= 0:
            raise ValueError("Количество дней должно быть больше 0")
        return self.price_per_night * days

# Специализированный класс 3: Бронирование
@dataclass
class Booking(BaseEntity):
    guest_id: int
    room_id: int
    days: int
    total_cost: float

    def get_report_data(self) -> str:
        return f"Бронирование ID {self.id}: Гость {self.guest_id}, Номер {self.room_id}, {self.days} дн., Стоимость: {self.total_cost} руб."