import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest  # noqa: E402
import httpx  # noqa: E402

from app.main import app, create_order, menu_client  # noqa: E402
from app.client import CircuitBreaker, CircuitOpenError, ServiceClient  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client


class TestCircuitBreaker:
    def test_closed_initial_state(self):
        breaker = CircuitBreaker()
        assert breaker.state == "CLOSED"
        assert breaker.allow() is True

    def test_open_after_failures(self):
        breaker = CircuitBreaker(failure_threshold=2, open_timeout=60)
        breaker.failure()
        breaker.failure()
        assert breaker.state == "OPEN"
        assert breaker.allow() is False

    def test_half_open_then_closed_on_success(self):
        breaker = CircuitBreaker(failure_threshold=2, open_timeout=0.05)
        breaker.failure()
        breaker.failure()
        assert breaker.state == "OPEN"
        import time
        time.sleep(0.1)
        assert breaker.allow() is True  # HALF-OPEN
        breaker.success()
        assert breaker.state == "CLOSED"

    def test_half_open_failure_returns_open(self):
        breaker = CircuitBreaker(failure_threshold=1, open_timeout=0.05)
        breaker.failure()
        assert breaker.state == "OPEN"
        import time
        time.sleep(0.1)
        assert breaker.allow() is True
        breaker.failure()
        assert breaker.state == "OPEN"


class TestServiceClient:
    def test_retry_then_success(self):
        """Retry: первые две попытки 503, третья успешна."""
        import json

        class FakeResponse:
            status_code = 200
            def json(self):
                return {"ok": True}
            def raise_for_status(self):
                return None

        responses = [
            MagicMock(status_code=503, raise_for_status=MagicMock(
                side_effect=Exception("503"))),
            MagicMock(status_code=503, raise_for_status=MagicMock(
                side_effect=Exception("503"))),
        ]

        with patch("httpx.get", side_effect=responses + [] ) as mocked:
            responses.append(FakeResponse())
            mocked.side_effect = responses
            client = ServiceClient("http://test", retries=3, backoff=0)
            result = client.get("/x")
            assert result == {"ok": True}
            assert mocked.call_count == 3

    @patch("httpx.get", side_effect=httpx.ConnectError("connection refused"))
    def test_circuit_opens_after_exhausting_retries(self, mocked):
        client = ServiceClient("http://test", retries=2, backoff=0,
                               breaker=CircuitBreaker(failure_threshold=1, open_timeout=60))
        with pytest.raises(httpx.ConnectError):
            client.get("/x")
        with pytest.raises(CircuitOpenError):
            client.get("/x")  # OPEN — без попыток соединения
        assert mocked.call_count == 2


class TestOrderServiceUnit:
    @patch("app.main.menu_client")
    def test_create_order_with_mocked_menu(self, mock_menu, client):
        mock_menu.get.return_value = {"id": 1, "name": "Борщ", "price": 350.0}

        response = client.post("/orders", json={"dish_id": 1, "client_name": "Иван"})

        assert response.status_code == 201
        body = response.json()
        assert body["total"] == 350.0
        assert body["status"] == "created"
        mock_menu.get.assert_called_once_with("/dishes/1")

    @patch("app.main.menu_client")
    def test_create_order_menu_unavailable(self, mock_menu, client):
        mock_menu.get.side_effect = Exception("down")

        response = client.post("/orders", json={"dish_id": 1, "client_name": "Иван"})

        assert response.status_code == 503

    def test_get_missing_order(self, client):
        response = client.get("/orders/9999")
        assert response.status_code == 404

    def test_health(self, client):
        response = client.get("/health")
        assert response.json() == {"status": "healthy"}