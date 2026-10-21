import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client


class TestGatewayRouting:
    @patch("app.main.menu")
    def test_proxy_dishes(self, mock_menu, client):
        mock_menu.get.return_value = [{"id": 1, "name": "Борщ", "price": 350.0}]

        response = client.get("/dishes")

        assert response.status_code == 200
        assert response.json()[0]["name"] == "Борщ"

    @patch("app.main.menu.get")
    def test_proxy_dishes_unavailable(self, mock_get, client):
        mock_get.side_effect = Exception("down")

        response = client.get("/dishes")

        assert response.status_code == 502

    def test_root(self, client):
        assert client.get("/").json()["service"] == "API Gateway"


class TestGatewayHealth:
    @patch("app.main.menu.get", return_value={"status": "healthy"})
    @patch("app.main.orders.get", return_value={"status": "healthy"})
    @patch("app.main.delivery.get", return_value={"status": "healthy"})
    def test_health_all_ok(self, mock_d, mock_o, mock_m, client):
        response = client.get("/health")

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "healthy"
        assert all(v == "ok" for v in body["services"].values())

    @patch("app.main.menu.get", side_effect=Exception("down"))
    @patch("app.main.orders.get", return_value={"status": "healthy"})
    @patch("app.main.delivery.get", return_value={"status": "healthy"})
    def test_health_degraded(self, mock_d, mock_o, mock_m, client):
        response = client.get("/health")

        body = response.json()
        assert body["status"] == "degraded"
        assert body["services"]["menu"] == "unavailable"


class TestGatewayOrder:
    @patch("app.main.orders")
    def test_create_order_via_gateway(self, mock_orders, client):
        mock_orders.get.return_value = {
            "id": 1, "dish_id": 1, "dish_name": "Борщ",
            "client_name": "Иван", "total": 350.0, "status": "created",
        }

        response = client.post("/order", json={"dish_id": 1, "client_name": "Иван"})

        assert response.status_code == 200
        assert response.json()["total"] == 350.0