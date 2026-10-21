"""Тесты сервисного слоя: бизнес-правила ресторана (с реальной БД)."""

import pytest

from restaurant.exceptions.errors import BusinessRuleError, ForbiddenError, NotFoundError
from restaurant.schemas.schemas import CustomerCreate, DishCreate, OrderCreate, OrderItemIn
from restaurant.services.services import AuthService, DeliveryService, DishService, OrderService


@pytest.fixture()
def auth(db_session):
    return AuthService(db_session)


@pytest.fixture()
def dishes(db_session):
    return DishService(db_session)


@pytest.fixture()
def orders(db_session):
    return OrderService(db_session)


@pytest.fixture()
def deliveries(db_session):
    return DeliveryService(db_session)


@pytest.fixture()
def customer(db_session, auth):
    return auth.register(CustomerCreate(email="bob@example.com", name="Боб", password="secret123"))


def make_dishes(dishes, names: list[tuple[str, float]]):
    created = []
    for name, price in names:
        created.append(dishes.create(DishCreate(name=name, price=price, description="")))
    return created


class TestAuthRules:
    def test_register_creates_user(self, auth, customer):
        assert customer.email == "bob@example.com"
        assert customer.role == "USER"

    def test_register_duplicate_email_raises(self, auth, customer):
        with pytest.raises(BusinessRuleError) as exc:
            auth.register(CustomerCreate(email="bob@example.com", name="Ещё Боб", password="secret123"))
        assert exc.value.error_code == "EMAIL_ALREADY_REGISTERED"

    def test_authenticate_success(self, auth, customer):
        found, token = auth.authenticate("bob@example.com", "secret123")
        assert found.id == customer.id
        assert token

    def test_authenticate_wrong_password_raises(self, auth, customer):
        with pytest.raises(ForbiddenError):
            auth.authenticate("bob@example.com", "wrongpass1")


class TestDishRules:
    def test_create_sets_fields(self, dishes, db_session):
        dish = dishes.create(DishCreate(name="Суп", price=250.0, description="Грибной"))
        assert dish.name == "Суп"
        assert dish.price == 250.0
        assert dish.in_stock is True

    def test_get_missing_dish_raises(self, dishes):
        with pytest.raises(NotFoundError) as exc:
            dishes.get(999)
        assert exc.value.error_code == "DISH_NOT_FOUND"

    def test_list_sorted_asc(self, dishes):
        make_dishes(dishes, [("Борщ", 350), ("Стейк", 890), ("Суп", 150)])
        names = [d.name for d in dishes.list("asc")]
        assert names == ["Суп", "Борщ", "Стейк"]

    def test_list_sorted_desc(self, dishes):
        make_dishes(dishes, [("Борщ", 350), ("Стейк", 890), ("Суп", 150)])
        names = [d.name for d in dishes.list("desc")]
        assert names == ["Стейк", "Борщ", "Суп"]

    def test_update_changes_price(self, dishes):
        dish = dishes.create(DishCreate(name="Борщ", price=350.0))
        updated = dishes.update(dish.id, DishCreate(name="Борщ", price=400.0))
        assert updated.price == 400.0

    def test_delete_removes_dish(self, dishes):
        dish = dishes.create(DishCreate(name="Временное", price=100.0))
        dishes.delete(dish.id)
        with pytest.raises(NotFoundError):
            dishes.get(dish.id)


class TestOrderBusinessRules:
    def test_rule_cannot_order_missing_dish(self, orders, customer):
        payload = OrderCreate(items=[OrderItemIn(dish_id=999, quantity=1)], address="Москва, ул. Ленина 1")
        with pytest.raises(NotFoundError) as exc:
            orders.create(customer.id, payload)
        assert exc.value.error_code == "DISH_NOT_FOUND"

    def test_rule_cannot_order_out_of_stock(self, orders, customer, dishes, db_session):
        dish = dishes.create(DishCreate(name="Каша", price=150.0, in_stock=False))
        payload = OrderCreate(items=[OrderItemIn(dish_id=dish.id, quantity=1)], address="Москва, ул. Ленина 1")
        with pytest.raises(BusinessRuleError) as exc:
            orders.create(customer.id, payload)
        assert exc.value.error_code == "DISH_OUT_OF_STOCK"

    def test_rule_order_total_calculated(self, orders, customer, dishes):
        [borsh, steak] = make_dishes(dishes, [("Борщ", 350), ("Стейк", 890)])
        payload = OrderCreate(
            items=[OrderItemIn(dish_id=borsh.id, quantity=2), OrderItemIn(dish_id=steak.id, quantity=1)],
            address="Москва, ул. Ленина 1",
        )
        order = orders.create(customer.id, payload)
        assert order.total == 350 * 2 + 890
        assert order.status == "CONFIRMED"

    def test_rule_cannot_order_more_than_budget(self, orders, customer, dishes):
        dish = dishes.create(DishCreate(name="Лобстер", price=60_000.0))
        payload = OrderCreate(items=[OrderItemIn(dish_id=dish.id, quantity=2)], address="Москва, ул. Ленина 1")
        with pytest.raises(BusinessRuleError) as exc:
            orders.create(customer.id, payload)
        assert exc.value.error_code == "ORDER_TOO_EXPENSIVE"

    def test_rule_max_items_limit(self, orders, customer, dishes):
        dish = dishes.create(DishCreate(name="Пельмени", price=100.0))
        items = [OrderItemIn(dish_id=dish.id, quantity=1) for _ in range(21)]
        payload = OrderCreate(items=items, address="Москва, ул. Ленина 1")
        with pytest.raises(BusinessRuleError) as exc:
            orders.create(customer.id, payload)
        assert exc.value.error_code == "TOO_MANY_ITEMS"

    def test_foreign_order_access_denied(self, orders, customer, db_session, auth, dishes):
        other = auth.register(CustomerCreate(email="alice@example.com", name="Алиса", password="secret123"))
        dish = dishes.create(DishCreate(name="Пицца", price=500.0))
        order = orders.create(
            other.id,
            OrderCreate(items=[OrderItemIn(dish_id=dish.id, quantity=1)], address="Москва, ул. Ленина 1"),
        )
        with pytest.raises(ForbiddenError) as exc:
            orders.get_for_customer(order.id, customer.id)
        assert exc.value.error_code == "ORDER_ACCESS_DENIED"

    @pytest.mark.parametrize("dish_id", [0, -1, 10000])
    def test_missing_dish_parametrized(self, orders, customer, dish_id):
        payload = OrderCreate(items=[OrderItemIn(dish_id=dish_id, quantity=1)], address="Москва, ул. Ленина 1")
        with pytest.raises(NotFoundError):
            orders.create(customer.id, payload)


class TestDeliveryRules:
    def test_rule_delivery_requires_confirmed_order(self, deliveries, orders, customer, dishes, db_session):
        dish = dishes.create(DishCreate(name="Салат", price=200.0))
        order = orders.create(
            customer.id,
            OrderCreate(items=[OrderItemIn(dish_id=dish.id, quantity=1)], address="Москва, ул. Ленина 1"),
        )
        order.status = "CREATED"
        db_session.commit()
        with pytest.raises(BusinessRuleError) as exc:
            deliveries.create_for_order(order.id, "Москва, ул. Ленина 1")
        assert exc.value.error_code == "ORDER_NOT_CONFIRMED"

    def test_rule_one_delivery_per_order(self, deliveries, orders, customer, dishes):
        dish = dishes.create(DishCreate(name="Суши", price=600.0))
        order = orders.create(
            customer.id,
            OrderCreate(items=[OrderItemIn(dish_id=dish.id, quantity=1)], address="Москва, ул. Ленина 1"),
        )
        deliveries.create_for_order(order.id, "Москва, ул. Ленина 1")
        with pytest.raises(BusinessRuleError) as exc:
            deliveries.create_for_order(order.id, "Москва, ул. Ленина 2")
        assert exc.value.error_code == "DELIVERY_EXISTS"

    def test_delivery_for_missing_order_raises(self, deliveries):
        with pytest.raises(NotFoundError):
            deliveries.create_for_order(999, "Москва, ул. Ленина 1")

    def test_update_delivery_status(self, deliveries, orders, customer, dishes):
        dish = dishes.create(DishCreate(name="Шашлык", price=700.0))
        order = orders.create(
            customer.id,
            OrderCreate(items=[OrderItemIn(dish_id=dish.id, quantity=1)], address="Москва, ул. Ленина 1"),
        )
        delivery = deliveries.create_for_order(order.id, "Москва, ул. Ленина 1")
        updated = deliveries.update_status(delivery.id, "IN_TRANSIT")
        assert updated.status == "IN_TRANSIT"

    def test_update_invalid_status_raises(self, deliveries, orders, customer, dishes):
        dish = dishes.create(DishCreate(name="Роллы", price=500.0))
        order = orders.create(
            customer.id,
            OrderCreate(items=[OrderItemIn(dish_id=dish.id, quantity=1)], address="Москва, ул. Ленина 1"),
        )
        delivery = deliveries.create_for_order(order.id, "Москва, ул. Ленина 1")
        with pytest.raises(BusinessRuleError):
            deliveries.update_status(delivery.id, "LOST")
