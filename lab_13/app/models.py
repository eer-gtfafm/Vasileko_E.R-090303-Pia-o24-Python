from typing import Any, Dict


class Room:
    """Гостиничный номер как документ MongoDB."""

    REQUIRED = ("number", "room_type", "floor", "price", "status")

    def __init__(self, number: str, room_type: str, floor: int, price: float,
                 features: Dict[str, Any], amenities: list, status: str = "свободен"):
        self.number = number
        self.room_type = room_type
        self.floor = floor
        self.price = price
        self.features = features          # вложенный объект: площадь, места, кровати
        self.amenities = amenities        # массив удобств
        self.status = status              # статус: свободен / занят / на обслуживании

    def to_doc(self) -> dict:
        return {
            "number": self.number,
            "room_type": self.room_type,
            "floor": self.floor,
            "price": self.price,
            "features": dict(self.features),
            "amenities": list(self.amenities),
            "status": self.status,
        }

    @classmethod
    def from_doc(cls, doc: dict) -> "Room":
        return cls(
            number=doc["number"],
            room_type=doc["room_type"],
            floor=doc["floor"],
            price=doc["price"],
            features=doc.get("features", {}),
            amenities=doc.get("amenities", []),
            status=doc.get("status", "свободен"),
        )

    def __repr__(self) -> str:
        return f"Room({self.number!r}, {self.room_type!r}, {self.price})"