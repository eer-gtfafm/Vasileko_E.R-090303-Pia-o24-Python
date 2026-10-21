import pytest

from app.service import DuplicateError, NotFoundError, ValidationError


SEED_COUNT = 3


class TestMongoCrud:
    def test_create_document(self, service):
        doc = {
            "number": "501", "room_type": "люкс", "floor": 5, "price": 7000.0,
            "features": {"area": 50, "capacity": 2, "beds": 1},
            "amenities": ["wi-fi", "сауна"], "status": "свободен",
        }
        created = service.add_room(doc)

        assert created["number"] == "501"
        assert service.get_room("501")["price"] == 7000.0

    def test_duplicate_number(self, service):
        with pytest.raises(DuplicateError):
            service.add_room({"number": "101", "room_type": "стандартный", "price": 1000})

    def test_invalid_price(self, service):
        with pytest.raises(ValidationError):
            service.add_room({"number": "999", "room_type": "стандартный", "price": -5})

    def test_get_document(self, service):
        doc = service.get_room("101")

        assert doc["number"] == "101"
        assert doc["room_type"] == "стандартный"
        assert doc["features"]["capacity"] == 2

    def test_get_missing_document(self, service):
        with pytest.raises(NotFoundError):
            service.get_room("999")

    def test_update_document(self, service):
        updated = service.update_room("101", {"price": 3000.0})

        assert updated["price"] == 3000.0
        assert service.get_room("101")["price"] == 3000.0

    def test_delete_document(self, service):
        service.delete_room("101")

        with pytest.raises(NotFoundError):
            service.get_room("101")


class TestMongoQueries:
    def test_filter_by_status(self, service):
        free = service.free_rooms()

        assert len(free) == 2  # 101 и 201 свободны
        assert all(room["status"] == "свободен" for room in free)

    def test_filter_by_inner_field(self, repo):
        docs = repo.find_by_feature("capacity", 4)

        assert [d["number"] for d in docs] == ["301"]

    def test_filter_by_array_element(self, repo):
        docs = repo.find_by_amenity("джакузи")

        assert [d["number"] for d in docs] == ["201"]

    def test_limit_and_sort(self, service):
        docs = service.list_rooms()
        top = repo_top(service._mongo)

        assert len(docs) == SEED_COUNT
        assert top == ["201", "301", "101"]  # по убыванию цены, limit 3

    def test_aggregation_count_by_type(self, repo):
        result = {r["_id"]: r["count"] for r in repo.count_by_type()}

        assert result == {"стандартный": 1, "люкс": 1, "семейный": 1}

    def test_aggregation_avg_price(self, repo):
        result = {r["_id"]: r["avg"] for r in repo.avg_price_by_type()}

        assert result["люкс"] == 6000.0
        assert result["семейный"] == 4200.0


def repo_top(repository):
    return [d["number"] for d in repository._collection.find().sort("price", -1).limit(3)]


class TestRedisCache:
    def test_string_set_get(self, cache):
        cache.set_room_cache("101", '{"number": "101"}')
        assert cache.get_room_cached("101") == '{"number": "101"}'

    def test_set_with_ttl(self, cache):
        cache.set_room_cache("101", "x", ttl=30)
        assert 0 < cache.cache_ttl("101") <= 30

    def test_list_push(self, cache):
        cache.push_search("люкс")
        cache.push_search("семейный")

        assert cache.recent_searches() == ["семейный", "люкс"]

    def test_set_free_rooms(self, cache):
        cache.set_free(["101", "201"])

        assert cache.free_count() == 2
        assert cache.is_free("101") is True
        assert cache.is_free("301") is False

    def test_hash_counter(self, cache):
        cache.increment_reads("101")
        cache.increment_reads("101")

        assert cache.get_counter("reads:101") or cache.stats().get("reads:101") == "2"


class TestCacheAside:
    def test_first_request_miss_then_hit(self, service, cache):
        service.get_room("101")
        assert cache.misses == 1 and cache.hits == 0

        service.get_room("101")
        assert cache.hits == 1 and cache.misses == 1

    def test_cache_invalidated_on_update(self, service, cache):
        service.get_room("101")          # промах, кэш заполнен
        service.update_room("101", {"price": 3100.0})  # инвалидация

        assert cache.cache_ttl("101") == -2  # ключ удалён из кэша

        doc = service.get_room("101")    # снова из MongoDB
        assert doc["price"] == 3100.0
        assert cache.misses == 2

    def test_benchmark_shape(self, service):
        rows = service.benchmark(counts=(100,))

        assert len(rows) == 1
        assert rows[0]["count"] == 100
        assert rows[0]["redis_avg_ms"] >= 0
        assert "speedup" in rows[0]