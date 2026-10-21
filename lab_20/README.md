# Лабораторная работа №20 — контейнеризация, CI/CD и эксплуатация

Вариант 5 — «Ресторан»: приложение и база данных в Docker Compose, автоматическая проверка API.

## Приложение

REST API ресторана на Flask + Flask-SQLAlchemy: каталог блюд, CRUD, `/health` (health check), логирование запросов. БД — PostgreSQL в отдельном контейнере (для локальных тестов — SQLite).

## Структура

```
lab_20/
├── app/
│   ├── main.py            # Flask API, /health, логирование, seed
│   ├── database.py        # модель Dish, init_db
│   └── __init__.py
├── tests/test_api.py      # 13 тестов API (health, CRUD, валидация)
├── .github/workflows/ci.yml  # CI: lint + pytest + docker build
├── Dockerfile             # multi-этапный? нет, простой; HEALTHCHECK
├── .dockerignore
├── docker-compose.yml     # app + postgres, volume, healthcheck
├── .env.example
├── .gitignore
└── requirements.txt
```

## Запуск через Docker Compose

```bash
docker compose up --build
# API: http://localhost:8000
# Health: http://localhost:8000/health
docker compose down          # данные БД сохраняются в volume postgres_data
```

## Переменные окружения

- `DATABASE_URL` — строка подключения (в Compose: `postgresql+psycopg://app:app_password@db:5432/restaurant`)
- `PORT` — порт приложения

Пароль БД задаётся через environment в docker-compose.yml, `.env` исключён из Git.

## Тесты и качество

```bash
../venv/bin/python -m pytest -v
../venv/bin/python -m ruff check app tests
```

CI (GitHub Actions) выполняет: checkout → python setup → install → ruff → pytest → docker build → docker compose config.

## Health Check и логирование

- `/health` возвращает `{"status":"healthy"}`, проверяется Docker HEALTHCHECK.
- Все запросы логируются методом + URL + статус + время (logging, не print).