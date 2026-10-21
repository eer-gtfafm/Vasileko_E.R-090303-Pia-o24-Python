import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

os.environ["DATABASE_URL"] = f"sqlite:///{tempfile.mkdtemp()}/test.db"

from app.main import app


@pytest.fixture()
def client():
    app.config.update(TESTING=True)
    with app.test_client() as test_client:
        yield test_client


class TestHealth:
    def test_health(self, client):
        response = client.get("/health")

        assert response.status_code == 200
        body = response.get_json()
        assert body["status"] == "healthy"
        assert body["service"] == "restaurant"

    def test_root(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert response.get_json()["service"] == "Restaurant API"


class TestDishesCrud:
    def test_list_dishes(self, client):
        response = client.get("/dishes")

        assert response.status_code == 200
        dishes = response.get_json()
        assert len(dishes) == 5
        assert any(d["name"] == "Борщ" for d in dishes)

    def test_api_alias_list(self, client):
        assert client.get("/api/dishes").status_code == 200

    def test_get_dish(self, client):
        response = client.get("/dishes/1")

        assert response.status_code == 200
        assert response.get_json()["id"] == 1

    def test_get_missing_dish(self, client):
        response = client.get("/dishes/999")

        assert response.status_code == 404
        assert "не найдено" in response.get_json()["error"]

    def test_create_dish(self, client):
        response = client.post("/dishes", json={"name": "Суп", "price": 250.0})

        assert response.status_code == 201
        assert response.get_json()["name"] == "Суп"
        assert client.get("/dishes/6").get_json()["price"] == 250.0

    def test_create_dish_invalid_name(self, client):
        response = client.post("/dishes", json={"name": "", "price": 250.0})

        assert response.status_code == 400
        assert "пустым" in response.get_json()["error"]

    def test_create_dish_invalid_price(self, client):
        response = client.post("/dishes", json={"name": "Суп", "price": -10})

        assert response.status_code == 400

    def test_create_dish_wrong_type(self, client):
        response = client.post("/dishes", json={"name": "Суп", "price": "дорого"})

        assert response.status_code == 400

    def test_delete_dish(self, client):
        created = client.post("/dishes", json={"name": "Для удаления", "price": 100.0})
        dish_id = created.get_json()["id"]

        assert client.delete(f"/dishes/{dish_id}").status_code == 204
        assert client.get(f"/dishes/{dish_id}").status_code == 404

    def test_delete_missing_dish(self, client):
        assert client.delete("/dishes/999").status_code == 404