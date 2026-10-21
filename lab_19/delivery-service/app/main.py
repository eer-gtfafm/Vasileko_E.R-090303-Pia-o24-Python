import sqlite3
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Delivery Service")


class Delivery(BaseModel):
    id: int
    order_id: int
    dish: str
    status: str
    created_at: str


def _connect() -> sqlite3.Connection:
    db_path = Path(__file__).parent / "deliveries.db"
    connection = sqlite3.connect(db_path)
    connection.execute(
        "CREATE TABLE IF NOT EXISTS deliveries ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "order_id INTEGER NOT NULL UNIQUE,"
        "dish TEXT NOT NULL,"
        "status TEXT NOT NULL,"
        "created_at TEXT NOT NULL)"
    )
    return connection


@app.get("/health")
def health() -> dict:
    return {"status": "healthy"}


@app.get("/events")
def accept_event(type: str, order_id: int, dish: str = "") -> dict:
    """Подписчик: получает событие OrderCreated и создаёт доставку."""
    connection = _connect()
    try:
        connection.execute(
            "INSERT INTO deliveries (order_id, dish, status, created_at) "
            "VALUES (?, ?, ?, ?)",
            (order_id, dish, "accepted", datetime.now().isoformat(timespec="seconds")),
        )
        connection.commit()
    except sqlite3.IntegrityError:
        connection.close()
        raise HTTPException(status_code=409, detail="Delivery already exists")
    connection.close()
    return {"status": "accepted", "event": type, "order_id": order_id}


@app.get("/deliveries")
def list_deliveries() -> list[Delivery]:
    connection = _connect()
    rows = connection.execute("SELECT * FROM deliveries ORDER BY id DESC").fetchall()
    connection.close()
    return [Delivery(id=r[0], order_id=r[1], dish=r[2], status=r[3], created_at=r[4])
            for r in rows]