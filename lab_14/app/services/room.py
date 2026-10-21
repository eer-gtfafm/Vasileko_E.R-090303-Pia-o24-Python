import json
import os
from typing import Any, Dict, List, Optional, Tuple

from app.repositories.room import RoomNotFoundError, RoomRepository


def create_cache_client():
    """Redis для кэширования; при недоступности — fakeredis."""
    try:
        import redis

        client = redis.Redis(
            host=os.getenv("REDIS_HOST", "127.0.0.1"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            socket_connect_timeout=0.3,
            decode_responses=True,
        )
        client.ping()
        return client, "redis"
    except Exception:
        import fakeredis

        return fakeredis.FakeRedis(decode_responses=True), "fakeredis"


CACHE_TTL = 60  # секунд


class RoomCache:
    """Cache-Aside для чтения номера по id."""

    def __init__(self, client, ttl: int = CACHE_TTL):
        self._client = client
        self._ttl = ttl
        self.hits = 0
        self.misses = 0

    @staticmethod
    def key(room_id: int) -> str:
        return f"room:{room_id}"

    def get(self, room_id: int) -> Optional[dict]:
        raw = self._client.get(self.key(room_id))
        if raw is None:
            self.misses += 1
            return None
        self.hits += 1
        return json.loads(raw)

    def set(self, room_id: int, data: dict) -> None:
        self._client.set(self.key(room_id), json.dumps(data, ensure_ascii=False), ex=self._ttl)

    def invalidate(self, room_id: int) -> None:
        self._client.delete(self.key(room_id))

    def ttl(self, room_id: int) -> int:
        return int(self._client.ttl(self.key(room_id)))

    def flush(self) -> None:
        for key in self._client.keys("room:*"):
            self._client.delete(key)
        self.hits = 0
        self.misses = 0

    def stats(self) -> dict:
        return {"hits": self.hits, "misses": self.misses} if self._client is not None else {}


class RoomService:
    """Бизнес-логика: валидация, CRUD, фильтрация, кэширование."""

    def __init__(self, repository: RoomRepository, cache: Optional[RoomCache] = None):
        self._repository = repository
        self._cache = cache

    def list_rooms(self, room_type=None, min_price=None, max_price=None, available=None,
                   sort="price", order="asc", skip=0, limit=20) -> Tuple[List[dict], int]:
        rooms, total = self._repository.list(
            room_type=room_type, min_price=min_price, max_price=max_price,
            available=available, sort=sort, order=order, skip=skip, limit=limit,
        )
        return [self._to_dict(room) for room in rooms], total

    # GET /rooms/{id} — cache-aside
    def get_room(self, room_id: int) -> dict:
        if self._cache is not None:
            cached = self._cache.get(room_id)
            if cached is not None:
                return cached

        room = self._repository.get(room_id)
        if room is None:
            raise RoomNotFoundError(room_id)
        data = self._to_dict(room)

        if self._cache is not None:
            self._cache.set(room_id, data)
        return data

    def search_rooms(self, query: str, limit: int = 20) -> List[dict]:
        return [self._to_dict(room) for room in self._repository.search(query, limit=limit)]

    def create_room(self, payload: Dict[str, Any]) -> dict:
        if self._repository.get_by_number(payload["number"]) is not None:
            raise ValueError(f"Номер {payload['number']} уже существует")
        room = self._repository.create(
            number=payload["number"], room_type=payload["room_type"], floor=payload["floor"],
            capacity=payload["capacity"], price=payload["price"],
            available=payload.get("available", True), amenities=payload.get("amenities", []),
        )
        return self._to_dict(room)

    def replace_room(self, room_id: int, payload: Dict[str, Any]) -> dict:
        if self._repository.get(room_id) is None:
            raise RoomNotFoundError(room_id)
        fields = {
            "number": payload["number"], "room_type": payload["room_type"],
            "floor": payload["floor"], "capacity": payload["capacity"],
            "price": payload["price"], "available": payload.get("available", True),
            "amenities": ",".join(payload.get("amenities", [])),
        }
        room = self._repository.update(room_id, fields)
        self._invalidate(room_id)
        return self._to_dict(room)

    def patch_room(self, room_id: int, payload: Dict[str, Any]) -> dict:
        if self._repository.get(room_id) is None:
            raise RoomNotFoundError(room_id)
        fields: Dict[str, Any] = {}
        if "number" in payload:
            fields["number"] = payload["number"]
        if "room_type" in payload:
            fields["room_type"] = payload["room_type"]
        if "floor" in payload:
            fields["floor"] = payload["floor"]
        if "capacity" in payload:
            fields["capacity"] = payload["capacity"]
        if "price" in payload:
            fields["price"] = payload["price"]
        if "available" in payload:
            fields["available"] = payload["available"]
        if "amenities" in payload:
            fields["amenities"] = ",".join(payload["amenities"])
        room = self._repository.update(room_id, fields)
        self._invalidate(room_id)
        return self._to_dict(room)

    def delete_room(self, room_id: int) -> None:
        if not self._repository.delete(room_id):
            raise RoomNotFoundError(room_id)
        self._invalidate(room_id)

    def statistics(self) -> dict:
        return self._repository.statistics()

    def _invalidate(self, room_id: int) -> None:
        if self._cache is not None:
            self._cache.invalidate(room_id)

    @staticmethod
    def _to_dict(room) -> dict:
        return {
            "id": room.id,
            "number": room.number,
            "room_type": room.room_type,
            "floor": room.floor,
            "capacity": room.capacity,
            "price": room.price,
            "available": room.available,
            "amenities": room.amenities.split(",") if room.amenities else [],
        }