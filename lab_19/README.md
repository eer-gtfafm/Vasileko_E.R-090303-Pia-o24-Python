# Лабораторная работа №19 — микросервисная архитектура

Вариант 5 — «Ресторан». Три микросервиса: menu-service, order-service, delivery-service + API Gateway.

## Архитектура

```
Client
  ▼
API Gateway (порт 8080)
  ▼
┌────────────┬────────────┬────────────┐
menu-service  order-service  delivery-service
(8001, меню)  (8002, заказы) (8003, доставка)
```

- **menu-service** — каталог блюд; собственная БД (SQLite `dishes.db`).
- **order-service** — создание заказов; синхронно проверяет блюдо через menu-service (с Retry и Circuit Breaker); выдаёт событие OrderCreated в delivery-service; собственная БД `orders.db`.
- **delivery-service** — подписчик события OrderCreated; создаёт доставку; собственная БД `deliveries.db`.
- **gateway** — единая точка входа: маршрутизация /dishes, /orders, /deliveries, /order; агрегированный health-check с состояниями сервисов.

## Паттерны

- API Gateway — единая точка входа.
- Database per Service — у каждого сервиса своя БД.
- Retry — повтор временных HTTP-ошибок (503/504, таймауты) с ограниченным числом попыток и задержкой.
- Circuit Breaker — CLOSED → OPEN → HALF-OPEN; при недоступности сервиса запросы прекращаются, после паузы допускается пробный запрос.
- Асинхронное событие OrderCreated → delivery-service (имитация брокера через событийный endpoint).

## Запуск (Docker Compose)

Без установленного Docker сервисы запускаются локально:

```bash
cd menu-service && ../venv/bin/python -m uvicorn app.main:app --port 8001 &
cd order-service && ../venv/bin/python -m uvicorn app.main:app --port 8002 &
cd delivery-service && ../venv/bin/python -m uvicorn app.main:app --port 8003 &
cd gateway && ../venv/bin/python -m uvicorn app.main:app --port 8080 &
```

Gateway: http://127.0.0.1:8080 — примеры:

```bash
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/dishes
curl -X POST http://127.0.0.1:8080/order -H "Content-Type: application/json" \
  -d '{"dish_id":1,"client_name":"Иван"}'
```

## Тесты

```bash
cd lab_19
for s in menu-service order-service delivery-service gateway; do
  (cd $s && ../venv/bin/python -m pytest tests -q)
done
```

Минимум на сервис: unit-тесты, интеграционные (TestClient), взаимодействие между сервисами, обработка недоступности сервиса (Retry/Circuit Breaker).