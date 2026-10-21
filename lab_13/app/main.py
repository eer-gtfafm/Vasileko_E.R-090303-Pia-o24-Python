import json
import sys
from typing import Any, Dict, List

from app.mongodb import create_mongo_client, MongoRepository
from app.redis_client import create_redis_client, RedisStore
from app.service import DuplicateError, HotelService, NotFoundError, ValidationError


SEED_ROOMS: List[Dict[str, Any]] = [
    {"number": "101", "room_type": "стандартный", "floor": 1, "price": 2500.0,
     "features": {"area": 18, "capacity": 2, "beds": 1}, "amenities": ["wi-fi", "tv"], "status": "свободен"},
    {"number": "102", "room_type": "стандартный", "floor": 1, "price": 2700.0,
     "features": {"area": 20, "capacity": 2, "beds": 1}, "amenities": ["wi-fi", "tv", "кондиционер"], "status": "занят"},
    {"number": "103", "room_type": "стандартный", "floor": 1, "price": 2400.0,
     "features": {"area": 17, "capacity": 1, "beds": 1}, "amenities": ["wi-fi"], "status": "свободен"},
    {"number": "201", "room_type": "люкс", "floor": 2, "price": 6000.0,
     "features": {"area": 38, "capacity": 2, "beds": 1}, "amenities": ["wi-fi", "tv", "кондиционер", "мини-бар"], "status": "свободен"},
    {"number": "202", "room_type": "люкс", "floor": 2, "price": 6500.0,
     "features": {"area": 42, "capacity": 3, "beds": 2}, "amenities": ["wi-fi", "tv", "кондиционер", "мини-бар", "джакузи"], "status": "занят"},
    {"number": "203", "room_type": "люкс", "floor": 2, "price": 6200.0,
     "features": {"area": 40, "capacity": 2, "beds": 1}, "amenities": ["wi-fi", "tv", "кондиционер", "мини-бар"], "status": "свободен"},
    {"number": "301", "room_type": "семейный", "floor": 3, "price": 4200.0,
     "features": {"area": 45, "capacity": 4, "beds": 2}, "amenities": ["wi-fi", "tv", "кухня"], "status": "свободен"},
    {"number": "302", "room_type": "семейный", "floor": 3, "price": 4400.0,
     "features": {"area": 48, "capacity": 4, "beds": 2}, "amenities": ["wi-fi", "tv", "кухня", "кондиционер"], "status": "свободен"},
    {"number": "303", "room_type": "семейный", "floor": 3, "price": 4100.0,
     "features": {"area": 44, "capacity": 3, "beds": 2}, "amenities": ["wi-fi", "кухня"], "status": "на обслуживании"},
    {"number": "304", "room_type": "семейный", "floor": 3, "price": 4500.0,
     "features": {"area": 50, "capacity": 5, "beds": 3}, "amenities": ["wi-fi", "tv", "кухня", "кондиционер"], "status": "свободен"},
    {"number": "401", "room_type": "стандартный", "floor": 4, "price": 2800.0,
     "features": {"area": 19, "capacity": 2, "beds": 1}, "amenities": ["wi-fi", "tv"], "status": "свободен"},
    {"number": "402", "room_type": "стандартный", "floor": 4, "price": 2900.0,
     "features": {"area": 21, "capacity": 2, "beds": 1}, "amenities": ["wi-fi", "tv"], "status": "свободен"},
    {"number": "403", "room_type": "стандартный", "floor": 4, "price": 3100.0,
     "features": {"area": 22, "capacity": 2, "beds": 1}, "amenities": ["wi-fi", "tv", "кондиционер"], "status": "занят"},
    {"number": "501", "room_type": "люкс", "floor": 5, "price": 7000.0,
     "features": {"area": 50, "capacity": 2, "beds": 1}, "amenities": ["wi-fi", "tv", "кондиционер", "мини-бар", "сауна"], "status": "свободен"},
    {"number": "502", "room_type": "люкс", "floor": 5, "price": 7500.0,
     "features": {"area": 55, "capacity": 2, "beds": 2}, "amenities": ["wi-fi", "tv", "кондиционер", "мини-бар", "сауна"], "status": "свободен"},
    {"number": "503", "room_type": "люкс", "floor": 5, "price": 6800.0,
     "features": {"area": 48, "capacity": 2, "beds": 1}, "amenities": ["wi-fi", "tv", "кондиционер", "мини-бар"], "status": "на обслуживании"},
    {"number": "601", "room_type": "семейный", "floor": 6, "price": 4600.0,
     "features": {"area": 52, "capacity": 4, "beds": 2}, "amenities": ["wi-fi", "tv", "кухня", "кондиционер"], "status": "свободен"},
    {"number": "602", "room_type": "семейный", "floor": 6, "price": 4800.0,
     "features": {"area": 55, "capacity": 5, "beds": 3}, "amenities": ["wi-fi", "tv", "кухня"], "status": "занят"},
    {"number": "603", "room_type": "семейный", "floor": 6, "price": 4700.0,
     "features": {"area": 53, "capacity": 4, "beds": 2}, "amenities": ["wi-fi", "tv", "кухня", "кондиционер"], "status": "свободен"},
    {"number": "604", "room_type": "семейный", "floor": 6, "price": 5000.0,
     "features": {"area": 58, "capacity": 6, "beds": 3}, "amenities": ["wi-fi", "tv", "кухня", "кондиционер", "балкон"], "status": "свободен"},
]


def print_rooms(rooms: List[dict]) -> None:
    if not rooms:
        print("Номеров нет.")
        return
    print(f"{'Номер':<6} {'Тип':<12} {'Этаж':>4} {'Цена':>9} {'Мест':>4}  Статус")
    for r in rooms:
        features = r.get("features", {})
        print(f"{r['number']:<6} {r['room_type']:<12} {r.get('floor', 0):>4} "
              f"{r['price']:>9.2f} {features.get('capacity', 0):>4}  {r.get('status', '')}")


def read_room() -> dict:
    data = {
        "number": input("Номер комнаты: ").strip(),
        "room_type": input("Тип (стандартный/люкс/семейный): ").strip(),
        "price": float(input("Цена за ночь: ").strip()),
    }
    floor = input("Этаж (Enter — 1): ").strip()
    data["floor"] = int(floor) if floor else 1
    features_raw = input("Площадь (м²): ").strip()
    data["features"] = {
        "area": float(features_raw) if features_raw else 20.0,
        "capacity": 2,
        "beds": 1,
    }
    amenities = input("Удобства через запятую (wi-fi, tv, ...): ").strip()
    data["amenities"] = [a.strip() for a in amenities.split(",") if a.strip()]
    return data


def main() -> None:
    mongo_client, mongo_backend = create_mongo_client()
    redis_client, redis_backend = create_redis_client()
    repo = MongoRepository(mongo_client)
    cache = RedisStore(redis_client)
    service = HotelService(repo, cache)

    repo.ensure_indexes()
    repo.seed(SEED_ROOMS)
    service._sync_free_set()

    print(f"MongoDB: {mongo_backend} | Redis: {redis_backend}")
    print(f"Документов в MongoDB: {repo._collection.count_documents({})}")

    while True:
        print("\n=========== ОТЕЛЬ (MongoDB + Redis) ===========")
        print("1. Добавить номер")
        print("2. Найти номер (кэш Redis)")
        print("3. Список номеров")
        print("4. Поиск по условиям")
        print("5. Изменить номер")
        print("6. Удалить номер")
        print("7. Статистика (агрегация)")
        print("8. Состояние кэша")
        print("9. Очистить кэш")
        print("10. Тест производительности (benchmark)")
        print("0. Выход")
        choice = input("Выберите действие: ").strip()

        try:
            if choice == "0":
                print("Работа завершена.")
                break
            elif choice == "1":
                room = read_room()
                created = service.add_room(room)
                print(f"Добавлен номер {created['number']}")
            elif choice == "2":
                number = input("Номер комнаты: ").strip()
                doc = service.get_room(number)
                print(json.dumps(doc, ensure_ascii=False, indent=1))
                print(f"Кэш: hits={cache.hits}, misses={cache.misses}, TTL={cache.cache_ttl(number)}с")
            elif choice == "3":
                print_rooms(service.list_rooms())
            elif choice == "4":
                room_type = input("Тип (Enter — любой): ").strip() or None
                price_raw = input("Максимальная цена (Enter — любая): ").strip()
                capacity_raw = input("Минимальная вместимость (Enter — любая): ").strip()
                results = service.search(
                    room_type=room_type,
                    price_max=float(price_raw) if price_raw else None,
                    capacity=int(capacity_raw) if capacity_raw else None,
                )
                print_rooms(results)
            elif choice == "5":
                number = input("Номер комнаты: ").strip()
                field = input("Что изменить (price/status/room_type): ").strip()
                value = input("Новое значение: ").strip()
                payload = {field: float(value) if field == "price" else value}
                updated = service.update_room(number, payload)
                print(f"Обновлён: {updated['number']}, {field}={payload[field]}")
                print("Кэш инвалидирован (следующий запрос прочитает MongoDB).")
            elif choice == "6":
                number = input("Номер комнаты: ").strip()
                service.delete_room(number)
                print(f"Номер {number} удалён, кэш инвалидирован.")
            elif choice == "7":
                print(json.dumps(service.stats(), ensure_ascii=False, indent=1))
            elif choice == "8":
                print(json.dumps(service.cache_info(), ensure_ascii=False, indent=1))
            elif choice == "9":
                service.clear_cache()
                print("Кэш очищен.")
            elif choice == "10":
                for row in service.benchmark():
                    print(f"{row['count']:>6} запросов | MongoDB: {row['mongo_total_ms']:>9.2f} мс "
                          f"(ср. {row['mongo_avg_ms']:.4f}) | Redis: {row['redis_total_ms']:>9.2f} мс "
                          f"(ср. {row['redis_avg_ms']:.4f}) | ускорение x{row['speedup']}")
            else:
                print("Неизвестный пункт меню.")
        except (NotFoundError, DuplicateError, ValidationError) as error:
            print("Ошибка:", error)
        except ValueError:
            print("Ошибка: введите корректное число")
        except KeyboardInterrupt:
            print("\nКлиент остановлен.")
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)