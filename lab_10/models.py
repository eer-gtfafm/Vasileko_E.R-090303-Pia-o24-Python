from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict


class RoomType(Enum):
    STANDARD = "стандартный"
    SUITE = "люкс"
    FAMILY = "семейный"


class RoomStatus(Enum):
    FREE = "свободен"
    OCCUPIED = "занят"
    MAINTENANCE = "на обслуживании"


# Ресурс REST API — гостиничный номер.
# Идентификатор и пять дополнительных полей.
@dataclass
class Room:
    id: int
    number: str
    room_type: RoomType
    price_per_night: float
    capacity: int
    status: RoomStatus

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "number": self.number,
            "room_type": self.room_type.value,
            "price_per_night": self.price_per_night,
            "capacity": self.capacity,
            "status": self.status.value,
        }
