import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.client import CircuitBreaker, ServiceClient

app = FastAPI(title="Order Service")


class OrderCreate(BaseModel):
    dish_id: int
    client_name: str


class Order(BaseModel):
    id: int
    dish_id: int
    dish_name: str
    client_name: str
    total: float
    status: str = "created"
    created_at: str


def _connect() -> sqlite3.Connection:
    db_path = Path(__file__).parent / "orders.db"
    connection = sqlite3.connect(db_path)
    connection.execute(
        "CREATE TABLE IF NOT EXISTS orders ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "dish_id INTEGER NOT NULL,"
        "client_name TEXT NOT NULL,"
        "total REAL NOT NULL,"
        "status TEXT NOT NULL,"
        "created_at TEXT NOT NULL)"
    )
    return connection


menu_client = ServiceClient("http://127.0.0.1:8001", retries=3, backoff=0.1)
# набор получателей события OrderCreated (асинхронное взаимодействие)
delivery_service = ServiceClient("http://127.0.0.1:8003", retries=1)

delivered_events: list[str] = []


@app.get("/health")
def health() -> dict:
    return {"status": "healthy"}


@app.get("/orders")
def list_orders() -> list[Order]:
    connection = _connect()
    rows = connection.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()
    connection.close()
    return [Order(id=row[0], dish_id=row[1], client_name=row[2], total=row[3],
                  status=row[4], created_at=row[5], dish_name="?") for row in rows]


@app.get("/orders/{order_id}")
def get_order(order_id: int) -> Order:
    connection = _connect()
    row = connection.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    connection.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return Order(id=row[0], dish_id=row[1], client_name=row[2], total=row[3],
                 status=row[4], created_at=row[5], dish_name="?")


@app.get("/create")
def create_order_get(dish_id: int, client_name: str = "client") -> Order:
    """GET-обёртка для gwateway-агрегации (имитация POST через gateway)."""
    return create_order(OrderCreate(dish_id=dish_id, client_name=client_name))


@app.post("/orders", status_code=201)
def create_order(payload: OrderCreate) -> Order:
    # синхронное взаимодействие: проверить блюдо в menu-service
    try:
        dish = menu_client.get(f"/dishes/{payload.dish_id}")
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"Menu service unavailable: {error}")

    connection = _connect()
    cursor = connection.execute(
        "INSERT INTO orders (dish_id, client_name, total, status, created_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (payload.dish_id, payload.client_name, dish["price"], "created",
         datetime.now().isoformat(timespec="seconds")),
    )
    connection.commit()
    order_id = cursor.lastrowid
    row = connection.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    connection.close()

    order = Order(id=order_id, dish_id=payload.dish_id, dish_name=dish["name"],
                  client_name=payload.client_name, total=dish["price"],
                  status=row[4], created_at=row[5])

    # асинхронное событие OrderCreated -> delivery-service
    try:
        delivery_service.get(
            f"/events?type=OrderCreated&order_id={order.id}&dish={dish['name']}"
        )
        delivered_events.append(f"OrderCreated:{order.id}")
    except Exception:
        pass  # недоступность получателя не отменяет заказ

    return order


@app.get("/events")
def events() -> list[str]:
    return delivered_events


@app.get("/debug/menu-breaker")
def menu_breaker_state() -> dict:
    return {
        "state": menu_client.breaker_state(),
        "failures": menu_client.breaker.failures,
    }