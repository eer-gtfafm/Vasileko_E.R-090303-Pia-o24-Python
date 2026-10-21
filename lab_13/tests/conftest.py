import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import fakeredis  # noqa: E402
import mongomock  # noqa: E402

from app.mongodb import MongoRepository  # noqa: E402
from app.redis_client import RedisStore  # noqa: E402
from app.service import HotelService  # noqa: E402

SEED = [
    {"number": "101", "room_type": "стандартный", "floor": 1, "price": 2500.0,
     "features": {"area": 18, "capacity": 2, "beds": 1}, "amenities": ["wi-fi", "tv"], "status": "свободен"},
    {"number": "201", "room_type": "люкс", "floor": 2, "price": 6000.0,
     "features": {"area": 38, "capacity": 2, "beds": 1}, "amenities": ["wi-fi", "tv", "джакузи"], "status": "свободен"},
    {"number": "301", "room_type": "семейный", "floor": 3, "price": 4200.0,
     "features": {"area": 45, "capacity": 4, "beds": 2}, "amenities": ["wi-fi", "кухня"], "status": "занят"},
]


@pytest.fixture()
def repo():
    mongo = mongomock.MongoClient()
    repository = MongoRepository(mongo)
    repository._collection.insert_many(SEED)
    repository.ensure_indexes()
    return repository


@pytest.fixture()
def cache():
    return RedisStore(fakeredis.FakeRedis(decode_responses=True))


@pytest.fixture()
def service(repo, cache):
    return HotelService(repo, cache)