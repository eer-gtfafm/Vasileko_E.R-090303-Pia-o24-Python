import pytest

from app.services.services import DuplicateError, NotFoundError, OrderError


class TestCustomerService:
    def test_create_and_get(self, services):
        customers, _, _, _ = services
        created = customers.create("Петрова Анна", "+7 900 222-22-22")

        assert created.id is not None
        assert customers.get(created.id).full_name == "Петрова Анна"

    def test_create_duplicate_phone(self, services):
        customers, _, _, _ = services
        customers.create("Иванов Иван", "+7 900 111-11-11")

        with pytest.raises(DuplicateError):
            customers.create("Иванов Пётр", "+7 900 111-11-11")

    def test_update_customer(self, filled):
        customers, _, _, customer = filled
        updated = customers.update(customer.id, full_name="Иванов Пётр")

        assert updated.full_name == "Иванов Пётр"
        assert customers.get(customer.id).full_name == "Иванов Пётр"

    def test_delete_customer(self, filled):
        customers, _, _, customer = filled
        customers.delete(customer.id)

        with pytest.raises(NotFoundError):
            customers.get(customer.id)

    def test_get_missing_customer(self, services):
        customers, _, _, _ = services
        with pytest.raises(NotFoundError):
            customers.get(999)


class TestDishService:
    def test_create_and_find_by_category(self, filled):
        _, dishes, _, _ = filled

        assert len(dishes.find(category="супы")) == 1

    def test_find_by_search(self, filled):
        _, dishes, _, _ = filled

        assert len(dishes.find(search="Цезарь")) == 1
        assert len(dishes.find(search="несуществующее")) == 0

    def test_duplicate_dish_name(self, services):
        _, dishes, _, _ = services
        dishes.create("Борщ", "супы", 350.0)

        with pytest.raises(DuplicateError):
            dishes.create("Борщ", "супы", 400.0)

    def test_invalid_price(self, services):
        _, dishes, _, _ = services

        with pytest.raises(OrderError):
            dishes.create("Хлеб", "выпечка", 0)

    def test_sort_by_price(self, filled):
        _, dishes, _, _ = filled
        result = dishes.find(sort_by_price=True)

        prices = [float(d.price) for d in result]
        assert prices == sorted(prices)

    def test_update_delete_dish(self, filled):
        _, dishes, _, _ = filled
        dish = dishes.find(search="Борщ")[0]

        updated = dishes.update(dish.id, price=400.0)
        assert float(updated.price) == 400.0

        dishes.delete(dish.id)
        with pytest.raises(NotFoundError):
            dishes.get(dish.id)


class TestOrderService:
    def test_create_order_transaction(self, filled):
        _, dishes, orders, customer = filled
        борщ = dishes.find(search="Борщ")[0]
        цезарь = dishes.find(search="Цезарь")[0]

        order = orders.create_order(customer.id, [(борщ.id, 2), (цезарь.id, 1)])

        assert order.status == "принят"
        assert order.total() == 350 * 2 + 420
        assert len(order.items) == 2

    def test_order_without_items(self, filled):
        _, _, orders, customer = filled

        with pytest.raises(OrderError):
            orders.create_order(customer.id, [])

    def test_order_unknown_dish_rollback(self, filled):
        _, _, orders, customer = filled

        with pytest.raises(NotFoundError):
            orders.create_order(customer.id, [(9999, 1)])

        assert len(orders.list()) == 0

    def test_add_item_and_change_quantity(self, filled):
        _, dishes, orders, customer = filled
        борщ = dishes.find(search="Борщ")[0]
        цезарь = dishes.find(search="Цезарь")[0]
        order = orders.create_order(customer.id, [(борщ.id, 1)])

        orders.add_item(order.id, цезарь.id, 1)
        updated = orders.get(order.id)
        assert updated.total() == 350 + 420

        item = updated.items[0]
        orders.change_quantity(item.id, 3)
        assert orders.get(order.id).total() == 350 * 3 + 420

    def test_orders_of_customer(self, filled):
        _, dishes, orders, customer = filled
        борщ = dishes.find(search="Борщ")[0]
        orders.create_order(customer.id, [(борщ.id, 1)])
        orders.create_order(customer.id, [(борщ.id, 2)])

        assert len(orders.orders_of_customer(customer.id)) == 2

    def test_update_status(self, filled):
        _, dishes, orders, customer = filled
        борщ = dishes.find(search="Борщ")[0]
        order = orders.create_order(customer.id, [(борщ.id, 1)])

        orders.set_status(order.id, "выполнен")
        assert orders.get(order.id).status == "выполнен"

        with pytest.raises(OrderError):
            orders.set_status(order.id, "недопустимый")

    def test_stats(self, filled):
        _, dishes, orders, customer = filled
        борщ = dishes.find(search="Борщ")[0]
        orders.create_order(customer.id, [(борщ.id, 2)])

        stats = orders.stats()
        assert stats["count"] == 1
        assert stats["total"] == 700.0
        assert stats["average"] == 700.0