# Лабораторная работа №18 — тестирование Python-приложений (pytest, unittest.mock)

Вариант 5 — «Гостиница»: система бронирования номеров.

## Уровни приложения

Interface (main.py) → Service (RoomService) → Repository (SQLite/in-memory) → SQLite.

## Структура

```
lab_18/
├── src/
│   ├── models/room.py          # Room, Guest, Booking, BookingInterval
│   ├── repositories/base.py    # Repository (in-memory) + исключения
│   ├── repositories/sqlite.py  # SqliteRepository (интеграционные тесты)
│   └── services/hotel.py       # RoomService — бизнес-логика
├── tests/
│   ├── unit/test_service.py    # unit-тесты сервиса (Mock-репозиторий), параметризация
│   ├── unit/test_mock.py       # Mock/patch, проверка вызовов
│   └── integration/test_repository.py  # интеграционные тесты Service→Repository→SQLite
├── main.py                     # консольный интерфейс
├── pytest.ini
└── requirements.txt
```

## Запуск

```bash
../venv/bin/python -m pytest tests -v
../venv/bin/python -m pytest tests --cov=src --cov-report=term-missing   # покрытие
../venv/bin/python main.py       # консольное приложение
```

35 тестов: ≥10 unit, ≥5 с Mock/patch, ≥3 параметризованных, 5 интеграционных.
