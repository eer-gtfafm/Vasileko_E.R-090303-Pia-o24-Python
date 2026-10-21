from typing import Any, Dict, List

from exceptions import RoomNotFoundError
from models import Room, RoomStatus
from repository import RoomRepository
from schemas import SORT_FIELDS, parse_room_payload


# Бизнес-логика работы с номерами. Сервис не знает ни про HTTP,
# ни про Flask: он получает данные и возвращает объекты Room.
class RoomService:
    def __init__(self, repository: RoomRepository):
        self._repository = repository

    # Список номеров с фильтрацией и сортировкой (query-параметры)
    def list_rooms(self, filters: Dict[str, Any]) -> List[Room]:
        rooms = self._repository.get_all()

        if "room_type" in filters:
            rooms = [room for room in rooms if room.room_type == filters["room_type"]]
        if "status" in filters:
            rooms = [room for room in rooms if room.status == filters["status"]]
        if "min_price" in filters:
            rooms = [room for room in rooms if room.price_per_night >= filters["min_price"]]
        if "max_price" in filters:
            rooms = [room for room in rooms if room.price_per_night <= filters["max_price"]]

        sort = filters.get("sort")
        if sort:
            field = SORT_FIELDS[sort]
            rooms.sort(key=lambda room: getattr(room, field), reverse=filters.get("order") == "desc")

        return rooms

    def get_room(self, room_id: int) -> Room:
        room = self._repository.get_by_id(room_id)
        if room is None:
            raise RoomNotFoundError(room_id)
        return room

    def create_room(self, payload: Any) -> Room:
        data = parse_room_payload(payload)
        room = Room(
            id=self._repository.next_id(),
            number=data["number"],
            room_type=data["room_type"],
            price_per_night=data["price_per_night"],
            capacity=data["capacity"],
            status=data.get("status", RoomStatus.FREE),
        )
        return self._repository.create(room)

    # PUT: полная замена ресурса, все основные поля обязательны
    def replace_room(self, room_id: int, payload: Any) -> Room:
        current = self.get_room(room_id)
        data = parse_room_payload(payload)
        room = Room(
            id=current.id,
            number=data["number"],
            room_type=data["room_type"],
            price_per_night=data["price_per_night"],
            capacity=data["capacity"],
            status=data.get("status", current.status),
        )
        return self._repository.update(room)

    # PATCH: частичное изменение, достаточно одного поля
    def patch_room(self, room_id: int, payload: Any) -> Room:
        room = self.get_room(room_id)
        changes = parse_room_payload(payload, partial=True)
        for field, value in changes.items():
            setattr(room, field, value)
        return self._repository.update(room)

    def delete_room(self, room_id: int) -> None:
        if not self._repository.delete(room_id):
            raise RoomNotFoundError(room_id)

    # Специализированная операция варианта: свободные номера
    def get_available_rooms(self, filters: Dict[str, Any]) -> List[Room]:
        filters = dict(filters)
        filters["status"] = RoomStatus.FREE
        return self.list_rooms(filters)
