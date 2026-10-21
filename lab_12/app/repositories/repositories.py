from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Customer, Dish


class CustomerRepository:
    """Доступ к данным клиентов."""

    def __init__(self, session: Session):
        self._session = session

    def get(self, customer_id: int) -> Optional[Customer]:
        return self._session.get(Customer, customer_id)

    def get_all(self) -> List[Customer]:
        return list(self._session.scalars(select(Customer).order_by(Customer.id)))

    def get_by_phone(self, phone: str) -> Optional[Customer]:
        return self._session.scalars(
            select(Customer).where(Customer.phone == phone)
        ).first()

    def create(self, full_name: str, phone: str) -> Customer:
        customer = Customer(full_name=full_name, phone=phone)
        self._session.add(customer)
        self._session.commit()
        return customer

    def update(self, customer_id: int, full_name: Optional[str] = None,
               phone: Optional[str] = None) -> Optional[Customer]:
        customer = self.get(customer_id)
        if customer is None:
            return None
        if full_name is not None:
            customer.full_name = full_name
        if phone is not None:
            customer.phone = phone
        self._session.commit()
        return customer

    def delete(self, customer_id: int) -> bool:
        customer = self.get(customer_id)
        if customer is None:
            return False
        self._session.delete(customer)
        self._session.commit()
        return True


class DishRepository:
    """Доступ к данным блюд."""

    def __init__(self, session: Session):
        self._session = session

    def get(self, dish_id: int) -> Optional[Dish]:
        return self._session.get(Dish, dish_id)

    def get_all(self) -> List[Dish]:
        return list(self._session.scalars(select(Dish).order_by(Dish.id)))

    def get_by_name(self, name: str) -> Optional[Dish]:
        return self._session.scalars(select(Dish).where(Dish.name == name)).first()

    # Фильтрация по категории, поиск по части названия, сортировка по цене
    def find(self, category: Optional[str] = None, search: Optional[str] = None,
             sort_by_price: bool = False) -> List[Dish]:
        stmt = select(Dish)
        if category:
            stmt = stmt.where(Dish.category == category)
        if search:
            stmt = stmt.where(Dish.name.contains(search))
        if sort_by_price:
            stmt = stmt.order_by(Dish.price)
        else:
            stmt = stmt.order_by(Dish.id)
        return list(self._session.scalars(stmt))

    def create(self, name: str, category: str, price: float) -> Dish:
        dish = Dish(name=name, category=category, price=price)
        self._session.add(dish)
        self._session.commit()
        return dish

    def update(self, dish_id: int, name: Optional[str] = None,
               category: Optional[str] = None, price: Optional[float] = None) -> Optional[Dish]:
        dish = self.get(dish_id)
        if dish is None:
            return None
        if name is not None:
            dish.name = name
        if category is not None:
            dish.category = category
        if price is not None:
            dish.price = price
        self._session.commit()
        return dish

    def delete(self, dish_id: int) -> bool:
        dish = self.get(dish_id)
        if dish is None:
            return False
        self._session.delete(dish)
        self._session.commit()
        return True