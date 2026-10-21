# Лабораторная работа №15 — веб-приложение на Flask

Вариант 5 — предметная область «Ресторан» (Dish, Category, Order).

## Технологии

Flask, Jinja2, Flask-SQLAlchemy (SQLAlchemy ORM), SQLite (по умолчанию) / PostgreSQL, pytest.

## Структура проекта

```
lab_15/
├── app/
│   ├── __init__.py            # Application Factory create_app, seed данных
│   ├── config.py              # настройки через переменные окружения
│   ├── routes/
│   │   ├── web.py             # HTML-интерфейс (Jinja2)
│   │   └── api.py             # REST API (JSON)
│   ├── models/models.py       # Category, Dish, Order (N:M через order_items)
│   ├── repositories/repositories.py  # доступ к данным
│   ├── services/services.py   # бизнес-логика и ошибки
│   ├── templates/             # base, index, list, detail, create, edit, orders, 404
│   └── static/css/style.css
├── tests/test_app.py          # 26 тестов
├── requirements.txt
└── README.md
```

## Запуск

```bash
cd lab_15
../venv/bin/python -m app            # сервер на http://127.0.0.1:5000
```

## Переменные окружения

- `DATABASE_URL` — строка подключения (по умолчанию SQLite `restaurant.db`; PostgreSQL: `postgresql+psycopg://user:pass@localhost:5432/restaurant`)
- `SECRET_KEY` — секретный ключ приложения

## Страницы

- `/` — главная (статистика)
- `/dishes` — меню с поиском, фильтрацией, сортировкой
- `/dishes/<id>` — карточка блюда
- `/dishes/create` — создание блюда
- `/dishes/<id>/edit` — редактирование
- `/dishes/<id>/delete` (POST) — удаление
- `/orders` и `/orders/create` — заказы

## REST API

```bash
curl -s http://127.0.0.1:5000/api/dishes
curl -s http://127.0.0.1:5000/api/dishes/1
curl -s -X POST http://127.0.0.1:5000/api/dishes -H "Content-Type: application/json" \
  -d '{"name":"Бульон","description":"","price":250,"calories":80,"available":true,"category_id":1}'
curl -s -X PUT http://127.0.0.1:5000/api/dishes/1 -H "Content-Type: application/json" -d '{"price":400}'
curl -s -X DELETE http://127.0.0.1:5000/api/dishes/1
```

## Тесты

```bash
../venv/bin/python -m pytest tests -v
```