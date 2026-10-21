# Лабораторная работа №12 — SQLAlchemy ORM

Вариант 5 — предметная область «Ресторан».

## Структура проекта

```
lab_12/
├── app/
│   ├── models/
│   │   └── entities.py      # Customer, Dish, Order, OrderItem
│   ├── repositories/
│   │   ├── repositories.py        # CustomerRepository, DishRepository
│   │   └── order_repository.py    # OrderRepository (заказы и позиции)
│   ├── services/
│   │   └── services.py      # CustomerService, DishService, OrderService
│   ├── database.py          # Engine, Session, создание таблиц
│   └── main.py              # консольный интерфейс
├── tests/
│   ├── conftest.py
│   └── test_services.py
├── requirements.txt
└── README.md
```

## Запуск

```bash
../venv/bin/python -m app.main            # SQLite: restaurant.db
../venv/bin/python -m app.main postgresql+psycopg://user:pass@localhost:5432/restaurant
../venv/bin/python -m pytest -v            # тесты
```

## Сущности

- **Customer** — клиент ресторана (уникальный телефон).
- **Dish** — блюдо меню (уникальное название, категория, цена).
- **Order** — заказ клиента (статус, комментарий).
- **OrderItem** — позиция заказа: связь N:M между Order и Dish (промежуточная таблица).

Связи: Customer 1:N Order, Order N:M Dish (через order_items).

## Транзакция

`OrderService.create_order()` атомарно проверяет блюда и клиента, создаёт заказ,
добавляет позиции и вычисляет стоимость; при ошибке сессия откатывается.