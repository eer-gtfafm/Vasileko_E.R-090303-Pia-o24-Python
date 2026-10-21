from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Room:
    id: Optional[int]
    number: str
    room_type: str
    price_per_night: float
    capacity: int
    status: str = "свободен"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "number": self.number,
            "room_type": self.room_type,
            "price_per_night": self.price_per_night,
            "capacity": self.capacity,
            "status": self.status,
        }


@dataclass
class Guest:
    id: Optional[int]
    full_name: str
    email: str
    phone: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "full_name": self.full_name, "email": self.email, "phone": self.phone}


@dataclass
class Service:
    id: Optional[int]
    name: str
    price: float

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "name": self.name, "price": self.price}


@dataclass
class Booking:
    id: Optional[int]
    room_id: int
    guest_id: int
    check_in: str
    check_out: str
    total_price: float
    status: str = "активно"
    services: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "id": self.id,
            "room_id": self.room_id,
            "guest_id": self.guest_id,
            "check_in": self.check_in,
            "check_out": self.check_out,
            "total_price": self.total_price,
            "status": self.status,
        }
        if self.services:
            data["services"] = self.services
        return data
