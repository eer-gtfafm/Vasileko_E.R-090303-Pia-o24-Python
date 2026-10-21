import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_health(client):
    assert client.get("/health").json() == {"status": "healthy"}


def test_list_dishes(client):
    dishes = client.get("/dishes").json()
    assert len(dishes) == 4
    assert dishes[0]["name"] == "Борщ"


def test_get_dish(client):
    dish = client.get("/dishes/1").json()
    assert dish["price"] == 350.0


def test_get_missing_dish(client):
    assert client.get("/dishes/999").status_code == 404


def test_dish_available_field(client):
    assert client.get("/dishes/2").json()["available"] is True