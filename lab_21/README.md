# Restaurant API — итоговый проект (ЛР №21, вариант 5)

Полноценная система «Ресторан»: REST API с авторизацией, полным циклом заказа и доставкой.
Итоговый проект по лабораторной работе №21.

## Назначение

Приложение решает задачу автоматизации работы ресторана: регистрация клиентов,
ведение каталога блюд, оформление заказов с бизнес-правилами и управление доставкой.
Пользователи — клиенты ресторана (USER) и администратор (ADMIN).

## Функциональность

- Регистрация и вход (JWT), роли USER / ADMIN
- CRUD каталога блюд (администрирование)
- Создание заказа с проверкой бизнес-правил
- Управление доставкой заказа
- Каталог: фильтрация, сортировка по цене
- Валидация входных данных (Pydantic + бизнес-правила)
- Централизованная обработка ошибок (JSON `{"error": ..., "message": ...}`)

## Архитектура

```
Client
  ↓ HTTP/JSON + JWT
API слой (FastAPI) — auth, dishes, orders, deliveries
  ↓ Pydantic-схемы
Сервисный слой — AuthService, DishService, OrderService, DeliveryService
  ↓ бизнес-правила
Repository слой — CustomerRepository, DishRepository, OrderRepository, DeliveryRepository
  ↓ SQLAlchemy ORM
PostgreSQL (в Docker) / SQLite (для тестов и локальной разработки)
```

Сущности БД (5): `customers`, `dishes`, `orders`, `order_items`, `deliveries`.

## Стек технологий

Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2, PostgreSQL, PyJWT, bcrypt,
pytest, pytest-cov, ruff, Docker, Docker Compose, GitHub Actions.

## Требования

- Python 3.11+
- Docker и Docker Compose (для контейнерного запуска)

## Установка (локально)

```bash
git clone <repository>
cd lab_21
python -m venv .venv && source .venv/bin/activate
cp .env.example .env
pip install -r requirements.txt
PYTHONPATH=src uvicorn restaurant.main:app --reload
```

По умолчанию используется SQLite (`./restaurant.db`). Чтобы использовать PostgreSQL,
задайте `DATABASE_URL`.

## Запуск

```bash
uvicorn restaurant.main:app --host 0.0.0.0 --port 8000
# Документация API: http://localhost:8000/docs
# Swagger/OpenAPI:  http://localhost:8000/openapi.json
# Health check:     http://localhost:8000/health
```

## Запуск тестов

```bash
PYTHONPATH=src pytest tests -v
PYTHONPATH=src pytest tests --cov=src --cov-report=term-missing
PYTHONPATH=src ruff check src tests
```

## Docker

```bash
docker compose up --build
# API: http://localhost:8000
docker compose down          # данные БД сохраняются в volume postgres_data
```

## API (основные операции)

| Метод | Путь | Назначение | Роль |
|-------|------|-----------|------|
| POST | /auth/register | регистрация | открытый |
| POST | /auth/login | вход, выдача JWT | открытый |
| GET | /dishes | список блюд (сортировка ?sort=asc/desc) | открытый |
| POST | /dishes | создать блюдо | ADMIN |
| PUT | /dishes/{id} | изменить блюдо | ADMIN |
| DELETE | /dishes/{id} | удалить блюдо | ADMIN |
| POST | /orders | создать заказ | USER |
| GET | /orders | мои заказы | USER |
| POST | /orders/{id}/cancel | отменить заказ | USER |
| POST | /deliveries/orders/{id} | создать доставку | USER |
| PATCH | /deliveries/{id}?status_new=… | статус доставки | USER |

## Переменные окружения

| Переменная | Значение по умолчанию |
|-----------|----------------------|
| DATABASE_URL | `sqlite:///./restaurant.db` |
| SECRET_KEY | `change-me-in-production` |
| JWT_ALGORITHM | `HS256` |
| ACCESS_TOKEN_EXPIRE_MINUTES | `60` |

Секреты (`SECRET_KEY`, пароль БД) не хранятся в Git: используется `.env` (в `.gitignore`),
шаблон — `.env.example`.

## CI

GitHub Actions (`.github/workflows/ci.yml`), запускается при push и pull_request:
checkout → Python 3.12 → install → ruff → pytest c покрытием (fail-under 70%) → docker build → docker compose config.
Также выполняется `--cov-fail-under=70`.

## Ограничения проекта

- События доставки и уведомления имитируются синхронными HTTP-вызовами (Message Broker не используется — уровень A).
- Аутентификация — один JWT-секрет; refresh-токены не реализованы.
- Docker-запуск требует установленного Docker (на машине разработки тесты выполняются на SQLite).