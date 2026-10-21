"""Интеграционные тесты REST API (TestClient + SQLite)."""

import pytest

from tests.conftest import USER_EMAIL, USER_PASSWORD, auth, seed_dishes


class TestHealth:
    def test_health(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"

    def test_docs_available(self, client):
        assert client.get("/docs").status_code == 200
        assert client.get("/openapi.json").status_code == 200


class TestAuthApi:
    EMAIL = "new@example.com"

    def test_register_success(self, client):
        resp = client.post("/auth/register", json={"email": self.EMAIL, "name": "Новый", "password": "secret123"})
        assert resp.status_code == 201
        body = resp.json()
        assert body["email"] == self.EMAIL
        assert body["role"] == "USER"

    def test_register_duplicate_conflict(self, client, user_token):
        resp = client.post("/auth/register", json={"email": USER_EMAIL, "name": "Дубль", "password": "secret123"})
        assert resp.status_code == 409
        assert resp.json()["error"] == "EMAIL_ALREADY_REGISTERED"

    def test_login_success(self, client, user_token):
        resp = client.post("/auth/login", json={"email": USER_EMAIL, "password": USER_PASSWORD})
        assert resp.status_code == 200
        assert resp.json()["token_type"] == "bearer"
        assert resp.json()["access_token"]

    def test_login_wrong_password_403(self, client):
        resp = client.post("/auth/login", json={"email": USER_EMAIL, "password": "badpass123"})
        assert resp.status_code == 403
        assert resp.json()["error"] == "INVALID_CREDENTIALS"

    @pytest.mark.parametrize(
        "payload",
        [
            {"email": "bad-email", "name": "Иван", "password": "secret123"},
            {"email": "a@b.ru", "name": "И", "password": "secret123"},
            {"email": "a@b.ru", "name": "Иван", "password": "123"},
        ],
    )
    def test_register_validation_422(self, client, payload):
        resp = client.post("/auth/register", json=payload)
        assert resp.status_code == 422


class TestDishesApi:
    def test_create_dish_requires_admin(self, client):
        resp = client.post("/dishes", json={"name": "Борщ", "price": 350.0})
        assert resp.status_code == 401

    def test_unauthorized_create_dish(self, client, user_token):
        resp = client.post("/dishes", json={"name": "Борщ", "price": 350.0}, headers=auth(user_token))
        assert resp.status_code == 403

    def test_admin_create_dish(self, client, admin_token):
        resp = client.post(
            "/dishes", json={"name": "Борщ", "price": 350.0, "description": "Классический"}, headers=auth(admin_token)
        )
        assert resp.status_code == 201
        assert resp.json()["name"] == "Борщ"

    def test_list_dishes(self, client, db_session):
        seed_dishes(db_session)
        resp = client.get("/dishes")
        assert resp.status_code == 200
        assert len(resp.json()) == 3

    def test_list_available_only(self, client, db_session, admin_token):
        seed_dishes(db_session)
        client.patch_data = None
        resp = client.get("/dishes/available")
        assert resp.status_code == 200
        assert all(d["in_stock"] for d in resp.json())

    def test_sort_desc(self, client, db_session):
        seed_dishes(db_session)
        resp = client.get("/dishes?sort=desc")
        prices = [d["price"] for d in resp.json()]
        assert prices == sorted(prices, reverse=True)

    def test_get_missing_dish_404(self, client):
        resp = client.get("/dishes/999")
        assert resp.status_code == 404
        assert resp.json()["error"] == "DISH_NOT_FOUND"

    @pytest.mark.parametrize(
        "payload",
        [
            {"name": "", "price": 10},
            {"name": "X", "price": 0},
            {"name": "X", "price": -5},
        ],
    )
    def test_create_dish_validation_422(self, client, admin_token, payload):
        resp = client.post("/dishes", json=payload, headers=auth(admin_token))
        assert resp.status_code == 422


class TestOrdersApi:
    def make_order(self, client, token, db_session):
        seed_dishes(db_session)
        resp = client.post(
            "/orders",
            json={"items": [{"dish_id": 1, "quantity": 2}], "address": "Москва, ул. Ленина 1"},
            headers=auth(token),
        )
        return resp

    def test_create_order_requires_auth(self, client):
        resp = client.post("/orders", json={"items": [{"dish_id": 1, "quantity": 1}], "address": "Москва"})
        assert resp.status_code == 401

    def test_create_order_full_cycle(self, client, user_token, db_session):
        resp = self.make_order(client, user_token, db_session)
        assert resp.status_code == 201
        body = resp.json()
        assert body["status"] == "CONFIRMED"
        assert body["total"] == 350 * 2
        assert body["items"][0]["name"] == "Борщ"

    def test_create_order_out_of_stock_409(self, client, admin_token, user_token, db_session):
        seed_dishes(db_session)
        dish = client.post(
            "/dishes", json={"name": "Каша", "price": 100.0, "in_stock": False}, headers=auth(admin_token)
        ).json()
        resp = client.post(
            "/orders",
            json={"items": [{"dish_id": dish["id"], "quantity": 1}], "address": "Москва, ул. Ленина 1"},
            headers=auth(user_token),
        )
        assert resp.status_code == 409
        assert resp.json()["error"] == "DISH_OUT_OF_STOCK"

    def test_my_orders_list(self, client, user_token, db_session):
        self.make_order(client, user_token, db_session)
        resp = client.get("/orders", headers=auth(user_token))
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_other_customer_order_403(self, client, user_token, db_session):
        order = self.make_order(client, user_token, db_session).json()
        client.post("/auth/register", json={"email": "other@example.com", "name": "Другой", "password": "secret123"})
        other = client.post("/auth/login", json={"email": "other@example.com", "password": "secret123"}).json()
        resp = client.get(f"/orders/{order['id']}", headers=auth(other["access_token"]))
        assert resp.status_code == 403

    def test_confirm_order_admin(self, client, user_token, admin_token, db_session):
        order = self.make_order(client, user_token, db_session).json()
        resp = client.post(f"/orders/{order['id']}/confirm", headers=auth(admin_token))
        assert resp.status_code == 200

    def test_cancel_order_flow(self, client, user_token, db_session):
        order = self.make_order(client, user_token, db_session).json()
        resp = client.post(f"/orders/{order['id']}/cancel", headers=auth(user_token))
        assert resp.status_code == 200
        assert resp.json()["status"] == "CANCELLED"

    def test_cancel_delivered_order_409(self, client, user_token, db_session, admin_token):
        order = self.make_order(client, user_token, db_session).json()
        client.post(f"/orders/{order['id']}/confirm", headers=auth(admin_token))
        resp = client.post(f"/orders/{order['id']}/cancel", headers=auth(user_token))
        assert resp.status_code == 200

    def test_order_validation_422_empty_items(self, client, user_token):
        resp = client.post("/orders", json={"items": [], "address": "Москва"}, headers=auth(user_token))
        assert resp.status_code == 422


class TestDeliveriesApi:
    def create_full(self, client, user_token, admin_token, db_session):
        seed_dishes(db_session)
        order = client.post(
            "/orders",
            json={"items": [{"dish_id": 1, "quantity": 1}], "address": "Москва, ул. Ленина 1"},
            headers=auth(user_token),
        ).json()
        delivery = client.post(
            f"/deliveries/orders/{order['id']}", json={"address": "Москва, ул. Ленина 1"}, headers=auth(user_token)
        )
        return order, delivery

    def test_create_delivery(self, client, user_token, admin_token, db_session):
        order, delivery = self.create_full(client, user_token, admin_token, db_session)
        assert delivery.status_code == 201
        assert delivery.json()["status"] == "PENDING"

    def test_duplicate_delivery_409(self, client, user_token, admin_token, db_session):
        order, delivery = self.create_full(client, user_token, admin_token, db_session)
        resp = client.post(
            f"/deliveries/orders/{order['id']}",
            json={"address": "Москва, ул. Ленина 2"},
            headers=auth(user_token),
        )
        assert resp.status_code == 409
        assert resp.json()["error"] == "DELIVERY_EXISTS"

    def test_get_delivery(self, client, user_token, admin_token, db_session):
        order, delivery = self.create_full(client, user_token, admin_token, db_session)
        resp = client.get(f"/deliveries/orders/{order['id']}", headers=auth(user_token))
        assert resp.status_code == 200
        assert resp.json()["address"] == "Москва, ул. Ленина 1"

    def test_update_status(self, client, user_token, admin_token, db_session):
        order, delivery = self.create_full(client, user_token, admin_token, db_session)
        resp = client.patch(
            f"/deliveries/{delivery.json()['id']}",
            params={"status_new": "IN_TRANSIT"},
            headers=auth(user_token),
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "IN_TRANSIT"

    def test_get_delivery_for_missing_order_404(self, client, user_token):
        resp = client.get("/deliveries/orders/999", headers=auth(user_token))
        assert resp.status_code == 404
