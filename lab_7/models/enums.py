from enum import Enum

class RoomStatus(Enum):
    FREE = "свободен"
    OCCUPIED = "занят"
    BOOKED = "забронирован"
    MAINTENANCE = "на обслуживании"