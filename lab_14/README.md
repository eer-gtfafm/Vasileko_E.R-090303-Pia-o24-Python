# Лабораторная работа №14 — REST API на FastAPI

Вариант 5 — предметная область «Отель» (сущность Room).

## Технологии

FastAPI, Pydantic, SQLAlchemy 2.x (SQLite/PostgreSQL), Redis (cache-aside, TTL), uvicorn, pytest.

## Структура проекта

```
lab_14/
├── app/
│   ├── main.py                # приложение, middleware-логирование, seed
│   ├── database.py            # Engine, Session, Dependency Injection get_db
│   ├── models/room.py         # ORM-модель Room
│   ├── schemas/room.py        # Pydantic: RoomCreate, RoomUpdate, RoomResponse…
│   ├── repositories/room.py   # CRUD, фильтрация, сортировка, пагинация, статистика
│   ├── services/room.py       # бизнес-логика, cache-aside RoomCache
│   └── routers/rooms.py       # HTTP endpoints /rooms
├── tests/test_api.py          # 22 теста API
├── requirements.txt
└── README.md
```

## Запуск

```bash
cd lab_14
../venv/bin/python -m uvicorn app.main:app --reload --port 8000
# или:
../venv/bin/python -m app.main
```

Swagger UI: http://127.0.0.1:8000/docs
ReDoc: http://127.0.0.1:8000/redoc

## Переменные окружения

- `DATABASE_URL` — строка подключения (по умолчанию SQLite `hotel.db`; для PostgreSQL `postgresql+psycopg://user:pass@localhost:5432/hotel`)
- `REDIS_HOST`, `REDIS_PORT` — параметры Redis; при недоступности используется fakeredis

## Примеры запросов

```bash
curl -s "http://127.0.0.1:8000/rooms?room_type=люкс&sort=price&order=desc&limit=5"
curl -s -X POST "http://127.0.0.1:8000/rooms" -H "Content-Type: application/json" \
  -d '{"number":"705","room_type":"люкс","floor":7,"capacity":2,"price":8000,"available":true,"amenities":["wi-fi","мини-бар"]}'
curl -s -X PATCH "http://127.0.0.1:8000/rooms/1" -H "Content-Type: application/json" -d '{"price":8500}'
curl -s "http://127.0.0.1:8000/rooms/search?q=201"
curl -s "http://127.0.0.1:8000/rooms/statistics"
```

## Тесты

```bash
../venv/bin/python -m pytest tests -v
```