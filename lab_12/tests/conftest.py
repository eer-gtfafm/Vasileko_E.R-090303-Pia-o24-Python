import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Database  # noqa: E402
from app.repositories.order_repository import OrderRepository  # noqa: E402
from app.repositories.repositories import CustomerRepository, DishRepository  # noqa: E402
from app.services.services import (  # noqa: E402
    CustomerService,
    DishService,
    OrderService,
)


@pytest.fixture()
def db(tmp_path):
    database = Database(f"sqlite:///{tmp_path / 'test_restaurant.db'}")
    database.create_tables()
    yield database
    database.engine.dispose()


@pytest.fixture()
def services(db):
    session = db.session()
    customers = CustomerService(CustomerRepository(session))
    dishes = DishService(DishRepository(session))
    orders = OrderService(OrderRepository(session), DishRepository(session), CustomerRepository(session))
    yield customers, dishes, orders, session
    session.close()


@pytest.fixture()
def filled(services):
    customers, dishes, orders, session = services
    dishes.create("Борщ", "супы", 350.0)
    dishes.create("Цезарь", "салаты", 420.0)
    customer = customers.create("Иванов Иван", "+7 900 111-11-11")
    return customers, dishes, orders, customer