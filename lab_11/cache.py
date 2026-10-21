import json
from typing import Any, Optional, Tuple

CACHE_TTL = 60
KEY_PREFIX = "room"


# Подключение к Redis. Если Redis-сервер недоступен, используется
# fakeredis — полная эмуляция Redis API в памяти процесса.
def create_cache_client(timeout: float = 0.3) -> Tuple[Any, str]:
    try:
        import redis

        client = redis.Redis(
            host="127.0.0.1", port=6379, socket_connect_timeout=timeout, decode_responses=True
        )
        client.ping()
        return client, "redis"
    except Exception:
        import fakeredis

        return fakeredis.FakeRedis(decode_responses=True), "fakeredis"


# Cache-aside: сначала проверяем кэш, при промахе читаем БД и кладём в кэш.
class RoomCache:
    def __init__(self, client: Any, ttl: int = CACHE_TTL):
        self._client = client
        self._ttl = ttl
        self.hits = 0
        self.misses = 0

    @staticmethod
    def key(room_id: int) -> str:
        return f"{KEY_PREFIX}:{room_id}"

    def get(self, room_id: int) -> Optional[dict]:
        raw = self._client.get(self.key(room_id))
        if raw is None:
            self.misses += 1
            return None
        self.hits += 1
        return json.loads(raw)

    def set(self, room_id: int, room: dict) -> None:
        self._client.set(self.key(room_id), json.dumps(room, ensure_ascii=False), ex=self._ttl)

    def invalidate(self, room_id: int) -> None:
        self._client.delete(self.key(room_id))

    def ttl(self, room_id: int) -> int:
        return int(self._client.ttl(self.key(room_id)))

    def flush(self) -> None:
        for key in self._client.keys(f"{KEY_PREFIX}:*"):
            self._client.delete(key)
        self.hits = 0
        self.misses = 0
