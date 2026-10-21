from typing import Any, List, Tuple


def create_redis_client(host: str = "127.0.0.1", port: int = 6379, timeout: float = 0.4):
    """Пытается подключиться к настоящему Redis; при недоступности
    использует fakeredis — эмуляцию Redis в памяти процесса."""
    try:
        import redis

        client = redis.Redis(host=host, port=port, socket_connect_timeout=timeout,
                             decode_responses=True)
        client.ping()
        return client, "redis"
    except Exception:
        import fakeredis

        return fakeredis.FakeRedis(decode_responses=True), "fakeredis"


class RedisStore:
    """Работа с Redis: минимум 3 типа данных (String, Hash, List, Set)."""

    CACHE_TTL = 60  # секунд; минимум по заданию — 30

    def __init__(self, client: Any):
        self._client = client
        self.hits = 0
        self.misses = 0

    # --- String: кэш номера (cache-aside) ---
    @staticmethod
    def room_key(number: str) -> str:
        return f"room:{number}"

    def get_room_cached(self, number: str):
        raw = self._client.get(self.room_key(number))
        if raw is None:
            self.misses += 1
            return None
        self.hits += 1
        return raw

    def set_room_cache(self, number: str, text: str, ttl: int = CACHE_TTL) -> None:
        self._client.set(self.room_key(number), text, ex=ttl)

    def invalidate_room(self, number: str) -> None:
        self._client.delete(self.room_key(number))

    def cache_ttl(self, number: str) -> int:
        return int(self._client.ttl(self.room_key(number)))

    # --- List: результаты последних поисков (история) ---
    def push_search(self, query: str, limit: int = 5) -> None:
        self._client.lpush("search:history", query)
        self._client.ltrim("search:history", 0, limit - 1)

    def recent_searches(self) -> List[str]:
        return self._client.lrange("search:history", 0, -1)

    # --- Set: свободные номера ---
    def add_free(self, numbers: List[str]) -> None:
        self._client.sadd("rooms:free", *numbers)

    def set_free(self, numbers: List[str]) -> None:
        self._client.delete("rooms:free")
        if numbers:
            self._client.sadd("rooms:free", *numbers)

    def free_count(self) -> int:
        return int(self._client.scard("rooms:free"))

    def is_free(self, number: str) -> bool:
        return bool(self._client.sismember("rooms:free", number))

    # --- Hash: счётчики/статистика ---
    def stats(self) -> dict:
        return self._client.hgetall("stats")

    def increment_reads(self, number: str) -> None:
        self._client.hincrby("stats", f"reads:{number}", 1)

    def set_counter(self, name: str, value: int) -> None:
        self._client.set(f"counter:{name}", value, ex=self.CACHE_TTL)

    def get_counter(self, name: str) -> int:
        raw = self._client.get(f"counter:{name}")
        return int(raw) if raw is not None else 0

    def clear(self) -> None:
        for key in self._client.keys("room:*"):
            self._client.delete(key)
        self._client.delete("rooms:free")
        self._client.delete("search:history")
        self._client.delete("stats")
        self.hits = 0
        self.misses = 0

    def key_sample(self) -> List[Tuple[str, str]]:
        sample = []
        for key in list(self._client.keys())[:8]:
            kind = self._client.type(key)
            sample.append((key, kind))
        return sample