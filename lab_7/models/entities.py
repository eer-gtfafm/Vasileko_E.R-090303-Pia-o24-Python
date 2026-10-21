from dataclasses import dataclass
from .enums import RoomStatus

@dataclass
class Room:
    id: int
    number: str
    price_per_night: float
    status: RoomStatus = RoomStatus.FREE

@dataclass
class Guest:
    id: int
    name: str

@dataclass
class Booking:
    id: int
    room_id: int
    guest_name: str
    days: int
    total_cost: float