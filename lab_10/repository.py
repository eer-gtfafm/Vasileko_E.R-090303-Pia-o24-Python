from threading import RLock
from typing import Dict, List, Optional

from models import Room


# Хранилище номеров в памяти процесса. Flask может обслуживать
# несколько запросов одновременно, поэтому операции защищены блокировкой.
class RoomRepository:
    def __init__(self):
        self._rooms: Dict[int, Room] = {}
        self._lock = RLock()

    def get_all(self) -> List[Room]:
        with self._lock:
            return list(self._rooms.values())

    def get_by_id(self, room_id: int) -> Optional[Room]:
        with self._lock:
            return self._rooms.get(room_id)

    def create(self, room: Room) -> Room:
        with self._lock:
            if room.id in self._rooms:
                raise ValueError(f"Номер с ID {room.id} уже существует")
            self._rooms[room.id] = room
            return room

    def update(self, room: Room) -> Room:
        with self._lock:
            if room.id not in self._rooms:
                raise ValueError(f"Номер с ID {room.id} не найден")
            self._rooms[room.id] = room
            return room

    def delete(self, room_id: int) -> bool:
        with self._lock:
            return self._rooms.pop(room_id, None) is not None

    def next_id(self) -> int:
        with self._lock:
            return max(self._rooms, default=0) + 1
