"""Тесты с Mock: изоляция сервисного слоя от реальной БД."""

from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from restaurant.exceptions.errors import BusinessRuleError, NotFoundError
from restaurant.models.entities import Customer, Dish, Order, OrderItem
from restaurant.schemas.schemas import CustomerCreate, OrderCreate, OrderItemIn
from restaurant.services.services import AuthService, OrderService


class TestAuthServiceWithMock:
    def test_register_mocks_repository(self):
        session = MagicMock()
        service = AuthService(session)
        service.customers = MagicMock()
        service.customers.get_by_email.return_value = None
        service.customers.add.return_value = None

        customer = service.register(CustomerCreate(email="mock@example.com", name="Мок", password="secret123"))

        service.customers.get_by_email.assert_called_once_with("mock@example.com")
        service.customers.add.assert_called_once()
        service.customers.commit.assert_called_once()
        assert customer.role == "USER"

    def test_register_duplicate_with_mock_raises(self):
        session = MagicMock()
        service = AuthService(session)
        service.customers = MagicMock()
        existing = Customer(id=1, email="mock@example.com", name="Существующий", hashed_password="x")
        service.customers.get_by_email.return_value = existing

        with pytest.raises(BusinessRuleError) as exc:
            service.register(CustomerCreate(email="mock@example.com", name="Мок", password="secret123"))
        assert exc.value.error_code == "EMAIL_ALREADY_REGISTERED"

    def test_authenticate_with_mock(self):
        session = MagicMock()
        service = AuthService(session)
        service.customers = MagicMock()
        customer = Customer(
            id=1,
            email="mock@example.com",
            name="Мок",
            hashed_password="$2b$12$abcdefghijklmnopqrstuv",
            role="USER",
        )
        service.customers.get_by_email.return_value = customer

        with (
            patch("restaurant.services.services.verify_password", return_value=True),
            patch("restaurant.services.services.create_access_token", return_value="fake-token"),
        ):
            found, token = service.authenticate("mock@example.com", "secret123")

        assert found.id == 1
        assert token == "fake-token"


class TestOrderServiceWithMock:
    def test_create_order_mocked_repository(self):
        session = MagicMock()
        service = OrderService(session)
        service.orders = MagicMock()
        service.items = MagicMock()
        service.dishes = MagicMock()
        dish = Dish(id=10, name="Борщ", price=350.0, in_stock=True)
        service.dishes.get.return_value = dish
        created_order = Order(id=1, customer_id=5, status="CREATED", total=0)
        service.orders.add.side_effect = lambda o: None
        service.orders.get.return_value = created_order

        order = service.create(5, OrderCreate(items=[OrderItemIn(dish_id=10, quantity=2)], address="Москва"))

        service.dishes.get.assert_called_once_with(10)
        service.items.add.assert_called_once()
        assert order.total == 700.0
        assert order.status == "CONFIRMED"

    def test_out_of_stock_detected_with_mock(self):
        session = MagicMock()
        service = OrderService(session)
        service.orders = MagicMock()
        service.items = MagicMock()
        service.dishes = MagicMock()
        service.dishes.get.return_value = Dish(id=7, name="Каша", price=100.0, in_stock=False)

        with pytest.raises(BusinessRuleError) as exc:
            service.create(5, OrderCreate(items=[OrderItemIn(dish_id=7, quantity=1)], address="Москва"))
        assert exc.value.error_code == "DISH_OUT_OF_STOCK"

    def test_missing_dish_with_mock(self):
        session = MagicMock()
        service = OrderService(session)
        service.orders = MagicMock()
        service.items = MagicMock()
        service.dishes = MagicMock()
        service.dishes.get.return_value = None

        with pytest.raises(NotFoundError):
            service.create(5, OrderCreate(items=[OrderItemIn(dish_id=999, quantity=1)], address="Москва"))

    def test_confirm_updates_status_with_mock(self):
        session = MagicMock()
        service = OrderService(session)
        service.orders = MagicMock()
        order = Order(id=1, customer_id=5, status="CREATED", total=100)
        service.orders.get.return_value = order

        result = service.confirm(1)

        service.orders.commit.assert_called_once()
        assert result.status == "CONFIRMED"


class TestOrderItemBuilder:
    def test_subtotal_calculation(self):
        item = OrderItem(id=1, dish_id=2, quantity=3, unit_price=120.0)
        assert item.unit_price * item.quantity == 360.0

    def test_quantity_bounds(self):
        with pytest.raises(ValidationError):
            OrderItemIn(dish_id=1, quantity=0)
        with pytest.raises(ValidationError):
            OrderItemIn(dish_id=1, quantity=100)
