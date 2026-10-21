import json
import time
from typing import Any, Dict, List, Optional

from app.mongodb import MongoRepository
from app.redis_client import RedisStore


class NotFoundError(Exception):
    """Номер не найден в MongoDB."""


class DuplicateError(Exception):
    """Номер с таким номером комнаты уже существует."""


class ValidationError(Exception):
    """Некорректные входные данные."""


class HotelService:
    """Бизнес-логика: CRUD через MongoDB, cache-aside через Redis."""

    def __init__(self, mongo: MongoRepository, redis_store: RedisStore):
        self._mongo = mongo
        self._redis = redis_store

    # --- CRUD ---
    def add_room(self, data: Dict[str, Any]) -> dict:
        number = str(data.get("number", "")).strip()
        if not number:
            raise ValidationError("Номер комнаты не может быть пустым")
        if self._mongo.get_by_number(number) is not None:
            raise DuplicateError(f"Номер {number} уже существует")
        price = float(data.get("price", 0))
        if price <= 0:
            raise ValidationError("Цена должна быть положительной")
        room_type = str(data.get("room_type", "")).strip()
        if room_type not in ("стандартный", "люкс", "семейный"):
            raise ValidationError("Недопустимый тип номера")
        doc = {
            "number": number,
            "room_type": room_type,
            "floor": int(data.get("floor", 1)),
            "price": price,
            "features": data.get("features", {"area": 20, "capacity": 2, "beds": 1}),
            "amenities": list(data.get("amenities", [])),
            "status": data.get("status", "свободен"),
        }
        self._mongo.create(doc)
        self._sync_free_set()
        return doc

    # Cache-aside: сначала Redis, при промахе — MongoDB, затем запись в кэш
    def get_room(self, number: str) -> dict:
        cached = self._redis.get_room_cached(number)
        if cached is not None:
            return json.loads(cached)

        doc = self._mongo.get_by_number(number)
        if doc is None:
            raise NotFoundError(f"Номер {number} не найден")
        payload = self._clean(doc)
        self._redis.set_room_cache(number, json.dumps(payload, ensure_ascii=False))
        self._redis.increment_reads(number)
        return payload

    @staticmethod
    def _clean(doc: dict) -> dict:
        """Возвращает документ без ObjectId — пригодный для JSON-сериализации."""
        return {key: value for key, value in doc.items() if key != "_id"}

    def list_rooms(self) -> List[dict]:
        return self._mongo.list_all()

    def update_room(self, number: str, fields: Dict[str, Any]) -> dict:
        if self._mongo.get_by_number(number) is None:
            raise NotFoundError(f"Номер {number} не найден")
        if "price" in fields and float(fields["price"]) <= 0:
            raise ValidationError("Цена должна быть положительной")
        self._mongo.update(number, fields)
        # инвалидация кэша: следующий запрос прочитает свежие данные из MongoDB
        self._redis.invalidate_room(number)
        self._sync_free_set()
        return self._mongo.get_by_number(number)

    def delete_room(self, number: str) -> None:
        if not self._mongo.delete(number):
            raise NotFoundError(f"Номер {number} не найден")
        self._redis.invalidate_room(number)
        self._sync_free_set()

    def set_status(self, number: str, status: str) -> dict:
        allowed = ("свободен", "занят", "на обслуживании")
        if status not in allowed:
            raise ValidationError(f"Недопустимый статус: {', '.join(allowed)}")
        return self.update_room(number, {"status": status})

    # --- сложные запросы ---
    def search(self, room_type: Optional[str] = None, price_max: Optional[float] = None,
               status: Optional[str] = None, capacity: Optional[int] = None) -> List[dict]:
        query: Dict[str, Any] = {}
        if room_type:
            query["room_type"] = room_type
        if status:
            query["status"] = status
        if price_max is not None:
            query["price"] = {"$lte": price_max}
        if capacity is not None:
            query["features.capacity"] = {"$gte": capacity}
        docs = list(self._mongo._collection.find(query).sort("price", 1))
        if docs:
            self._redis.push_search(f"{room_type or 'любой'} / до {price_max or '-'} руб.")
        return docs

    def free_rooms(self) -> List[dict]:
        self._sync_free_set()
        return self._mongo.find_by_status("свободен")

    def by_amenity(self, amenity: str) -> List[dict]:
        return self._mongo.find_by_amenity(amenity)

    # --- агрегация и статистика ---
    def stats(self) -> Dict[str, Any]:
        return {
            "total": self._mongo._collection.count_documents({}),
            "by_type": self._mongo.count_by_type(),
            "avg_price": self._mongo.avg_price_by_type(),
            "free_count": self._redis.free_count(),
        }

    def cache_info(self) -> Dict[str, Any]:
        return {
            "hits": self._redis.hits,
            "misses": self._redis.misses,
            "keys": self._redis.key_sample(),
            "history": self._redis.recent_searches(),
        }

    def clear_cache(self) -> None:
        self._redis.clear()

    def _sync_free_set(self) -> None:
        free = [doc["number"] for doc in self._mongo.find_by_status("свободен")]
        self._redis.set_free(free)

    # --- benchmark: MongoDB (без кэша) vs Redis (кэш) ---
    def benchmark(self, counts=(100, 1000, 10000)) -> List[Dict[str, Any]]:
        numbers = [doc["number"] for doc in self._mongo.list_all()]
        if not numbers:
            raise ValidationError("База пуста — нечего измерять")
        number = numbers[0]
        # прогреть кэш для честного сравнения
        self.get_room(number)
        results = []
        for count in counts:
            start = time.perf_counter()
            for _ in range(count):
                self._mongo.get_by_number(number)
            mongo_total = (time.perf_counter() - start) * 1000

            start = time.perf_counter()
            for _ in range(count):
                self._redis.get_room_cached(number)
            redis_total = (time.perf_counter() - start) * 1000

            results.append({
                "count": count,
                "mongo_total_ms": round(mongo_total, 2),
                "mongo_avg_ms": round(mongo_total / count, 4),
                "redis_total_ms": round(redis_total, 2),
                "redis_avg_ms": round(redis_total / count, 4),
                "speedup": round(mongo_total / redis_total, 1) if redis_total else None,
            })
        return results