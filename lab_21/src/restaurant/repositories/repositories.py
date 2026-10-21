"""Слой доступа к данным (Repository)."""

from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from restaurant.models.entities import Customer, Delivery, Dish, Order, OrderItem

T = TypeVar("T")


class BaseRepository(Generic[T]):
    model: type[T]

    def __init__(self, session: Session):
        self._session = session

    def get(self, entity_id: int) -> T | None:
        return self._session.get(self.model, entity_id)

    def list(self) -> list[T]:
        return list(self._session.execute(select(self.model)).scalars())

    def add(self, entity: T) -> T:
        self._session.add(entity)
        return entity

    def delete(self, entity: T) -> None:
        self._session.delete(entity)

    def commit(self) -> None:
        self._session.commit()


class CustomerRepository(BaseRepository[Customer]):
    model = Customer

    def get_by_email(self, email: str) -> Customer | None:
        return self._session.execute(select(Customer).where(Customer.email == email)).scalar_one_or_none()


class DishRepository(BaseRepository[Dish]):
    model = Dish

    def list_available(self) -> list[Dish]:
        return list(self._session.execute(select(Dish).where(Dish.in_stock.is_(True))).scalars())

    def list_sorted(self, order: str = "asc") -> list[Dish]:
        stmt = select(Dish)
        stmt = stmt.order_by(Dish.price.asc() if order == "asc" else Dish.price.desc())
        return list(self._session.execute(stmt).scalars())


class OrderRepository(BaseRepository[Order]):
    model = Order

    def list_by_customer(self, customer_id: int) -> list[Order]:
        return list(self._session.execute(select(Order).where(Order.customer_id == customer_id)).scalars())


class OrderItemRepository(BaseRepository[OrderItem]):
    model = OrderItem


class DeliveryRepository(BaseRepository[Delivery]):
    model = Delivery

    def get_by_order(self, order_id: int) -> Delivery | None:
        return self._session.execute(select(Delivery).where(Delivery.order_id == order_id)).scalar_one_or_none()
