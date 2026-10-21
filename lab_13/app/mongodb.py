from typing import Any, Dict, List, Optional

DB_NAME = "hotel_db"
COLLECTION = "rooms"


def create_mongo_client(uri: str = "mongodb://127.0.0.1:27017/", timeout: float = 0.4):
    """Пытается подключиться к настоящему MongoDB; при недоступности
    использует mongomock — эмуляцию MongoDB в памяти процесса."""
    try:
        from pymongo import MongoClient

        client = MongoClient(uri, serverSelectionTimeoutMS=int(timeout * 1000))
        client.admin.command("ping")
        return client, "mongomock" if uri.startswith("mongomock") or "mongomock" in uri else "pymongo"
    except Exception:
        import mongomock

        return mongomock.MongoClient(), "mongomock"


class MongoRepository:
    """Доступ к документам номеров: CRUD, сложные запросы, агрегация, индексы."""

    def __init__(self, client, db: str = DB_NAME, collection: str = COLLECTION):
        self._collection = client[db][collection]

    def seed(self, rooms: List[Dict[str, Any]]) -> None:
        if self._collection.count_documents({}) == 0:
            self._collection.insert_many(rooms)

    def ensure_indexes(self) -> List[str]:
        return [
            self._collection.create_index("number", unique=True),
            self._collection.create_index([("room_type", 1), ("price", 1)]),
        ]

    # --- CRUD ---
    def create(self, room: Dict[str, Any]) -> str:
        result = self._collection.insert_one(room)
        return str(result.inserted_id)

    def get_by_number(self, number: str) -> Optional[dict]:
        return self._collection.find_one({"number": number})

    def list_all(self) -> List[dict]:
        return list(self._collection.find().sort("number", 1))

    def update(self, number: str, fields: Dict[str, Any]) -> Optional[dict]:
        self._collection.update_one({"number": number}, {"$set": fields})
        return self.get_by_number(number)

    def delete(self, number: str) -> bool:
        result = self._collection.delete_one({"number": number})
        return result.deleted_count > 0

    # --- фильтрация ---
    def find_by_status(self, status: str) -> List[dict]:
        return list(self._collection.find({"status": status}).sort("price", 1))

    def find_free_by_type(self, room_type: str) -> List[dict]:
        return list(self._collection.find({"status": "свободен", "room_type": room_type}))

    def find_cheaper_than(self, price: float) -> List[dict]:
        return list(self._collection.find({"price": {"$lt": price}}).sort("price", 1))

    def find_by_floor_range(self, floor_min: int, floor_max: int) -> List[dict]:
        return list(self._collection.find(
            {"floor": {"$gte": floor_min, "$lte": floor_max}}
        ).sort("floor", 1))

    def find_by_feature(self, feature: str, value: Any) -> List[dict]:
        """Запрос по вложенному полю (features.*)."""
        return list(self._collection.find({f"features.{feature}": value}))

    def find_by_amenity(self, amenity: str) -> List[dict]:
        """Запрос по элементу массива amenities."""
        return list(self._collection.find({"amenities": amenity}))

    def find_capacity_at_least(self, capacity: int) -> List[dict]:
        return list(self._collection.find({"features.capacity": {"$gte": capacity}}))

    def top_expensive(self, limit: int = 3) -> List[dict]:
        return list(self._collection.find().sort("price", -1).limit(limit))

    # --- агрегация ---
    def count_by_type(self) -> List[dict]:
        return list(self._collection.aggregate([
            {"$group": {"_id": "$room_type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]))

    def avg_price_by_type(self) -> List[dict]:
        return list(self._collection.aggregate([
            {"$group": {"_id": "$room_type", "avg": {"$avg": "$price"}, "min": {"$min": "$price"}}},
            {"$sort": {"_id": 1}},
        ]))