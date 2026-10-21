import itertools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

_next_order = itertools.count(start=100)


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_health(client):
    assert client.get("/health").json() == {"status": "healthy"}


def test_accept_order_created_event(client):
    """Интеграционный тест: приём события OrderCreated создаёт доставку."""
    order_id = next(_next_order)
    response = client.get(
        "/events", params={"type": "OrderCreated", "order_id": order_id, "dish": "Борщ"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "accepted"
    assert body["order_id"] == order_id


def test_duplicate_event_rejected(client):
    order_id = next(_next_order)
    client.get("/events", params={"type": "OrderCreated", "order_id": order_id, "dish": "Паста"})
    response = client.get(
        "/events", params={"type": "OrderCreated", "order_id": order_id, "dish": "Паста"}
    )

    assert response.status_code == 409


def test_list_deliveries(client):
    order_id = next(_next_order)
    client.get("/events", params={"type": "OrderCreated", "order_id": order_id, "dish": "Стейк"})
    deliveries = client.get("/deliveries").json()

    assert any(d["order_id"] == order_id for d in deliveries)
    assert deliveries[0]["status"] == "accepted"