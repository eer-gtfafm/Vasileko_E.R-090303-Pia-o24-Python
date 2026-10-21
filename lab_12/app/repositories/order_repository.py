from typing import Dict, List, Optional, Sequence, Tuple

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Dish, Order, OrderItem


class OrderRepository:
    """Доступ к данным заказов и их позиций."""

    def __init__(self, session: Session):
        self._session = session

    def get(self, order_id: int) -> Optional[Order]:
        return self._session.get(Order, order_id)

    def get_all(self) -> List[Order]:
        return list(self._session.scalars(select(Order).order_by(Order.id)))

    def get_by_customer(self, customer_id: int) -> List[Order]:
        return list(self._session.scalars(
            select(Order).where(Order.customer_id == customer_id).order_by(Order.id)
        ))

    def find(self, status: Optional[str] = None) -> List[Order]:
        stmt = select(Order)
        if status:
            stmt = stmt.where(Order.status == status)
        return list(self._session.scalars(stmt.order_by(Order.id)))

    def add_item(self, order_id: int, dish_id: int, quantity: int) -> OrderItem:
        item = OrderItem(order_id=order_id, dish_id=dish_id, quantity=quantity)
        self._session.add(item)
        self._session.commit()
        return item

    def set_item_quantity(self, item_id: int, quantity: int) -> Optional[OrderItem]:
        item = self._session.get(OrderItem, item_id)
        if item is None:
            return None
        item.quantity = quantity
        self._session.commit()
        return item

    def add(self, order: Order) -> Order:
        self._session.add(order)
        self._session.commit()
        return order

    def update_status(self, order_id: int, status: str) -> Optional[Order]:
        order = self.get(order_id)
        if order is None:
            return None
        order.status = status
        self._session.commit()
        return order

    def delete(self, order_id: int) -> bool:
        order = self.get(order_id)
        if order is None:
            return False
        self._session.delete(order)
        self._session.commit()
        return True

    # Транзакция: проверка блюд, создание заказа, добавление позиций
    # и расчёт стоимости выполняются атомарно.
    def create_with_items(
        self, customer_id: int, items: Sequence[Tuple[int, int]], comment: Optional[str] = None
    ) -> Order:
        order = Order(customer_id=customer_id, status="принят", comment=comment)
        self._session.add(order)
        self._session.flush()
        for dish_id, quantity in items:
            self._session.add(OrderItem(order_id=order.id, dish_id=dish_id, quantity=quantity))
        self._session.commit()
        return order

    def stats(self) -> Dict[str, float]:
        """Агрегирующие запросы: сумма, средний чек, число заказов."""
        total = sum(order.total() for order in self.get_all())
        count = len(self.get_all())
        average = total / count if count else 0.0
        return {"count": count, "total": round(total, 2), "average": round(average, 2)}