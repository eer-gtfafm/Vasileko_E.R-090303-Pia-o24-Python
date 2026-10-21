import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["DATABASE_URL"] = f"sqlite:///{tempfile.mkdtemp()}/test_restaurant.db"

from app import create_app  # noqa: E402


@pytest.fixture()
def client():
    app = create_app()
    app.config.update(TESTING=True)
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture()
def dish_id(client) -> int:
    response = client.post("/api/dishes", json={
        "name": "Тестовое блюдо", "description": "для теста",
        "price": 250.0, "calories": 200, "available": True, "category_id": 1,
    })
    assert response.status_code == 201
    return response.get_json()["id"]