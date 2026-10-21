from typing import Dict, List, Type
from models.entities import FamilyRoom, Room, StandardRoom, SuiteRoom
from models.enums import RoomType


# Factory: единственное место, где по типу создаётся нужный класс номера.
# Клиентский код (UI, тесты) не знает конкретных классов.
class RoomFactory:
    _ROOMS: Dict[RoomType, Type[Room]] = {
        RoomType.STANDARD: StandardRoom,
        RoomType.SUITE: SuiteRoom,
        RoomType.FAMILY: FamilyRoom,
    }

    @staticmethod
    def create(room_type: RoomType, room_id: int, number: str, base_price: float) -> Room:
        room_class = RoomFactory._ROOMS.get(room_type)
        if room_class is None:
            raise ValueError(f"Неизвестный тип номера: {room_type}")
        return room_class(id=room_id, number=number, base_price=base_price)

    @staticmethod
    def types() -> List[RoomType]:
        return list(RoomFactory._ROOMS.keys())
