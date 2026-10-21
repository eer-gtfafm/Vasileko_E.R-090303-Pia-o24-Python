from typing import List, Optional

from sqlalchemy import func, or_

from app.models.models import Category, Dish, Order, db


class CategoryRepository:
    """Доступ к категориям."""

    def __init__(self):
        pass

    def get_all(self) -> List[Category]:
        return list(Category.query.order_by(Category.name).all())

    def get(self, category_id: int) -> Optional[Category]:
        return db.session.get(Category, category_id)

    def get_by_name(self, name: str) -> Optional[Category]:
        return Category.query.filter(func.lower(Category.name) == name.strip().lower()).first()

    def create(self, name: str) -> Category:
        category = Category(name=name.strip())
        db.session.add(category)
        db.session.commit()
        return category


class DishRepository:
    """Доступ к блюдам: CRUD, поиск, фильтрация, сортировка."""

    def get_all(self) -> List[Dish]:
        return list(Dish.query.order_by(Dish.name).all())

    def get(self, dish_id: int) -> Optional[Dish]:
        return db.session.get(Dish, dish_id)

    def search(self, search: Optional[str], category_id: Optional[int],
               available: Optional[bool], sort: str, order: str) -> List[Dish]:
        query = Dish.query
        if search:
            query = query.filter(or_(Dish.name.contains(search), Dish.description.contains(search)))
        if category_id:
            query = query.filter(Dish.category_id == category_id)
        if available is not None:
            query = query.filter(Dish.available == available)

        column = {"name": Dish.name, "price": Dish.price, "calories": Dish.calories}.get(sort, Dish.name)
        if order == "desc":
            column = column.desc()
        return list(query.order_by(column).all())

    def create(self, name: str, description: str, price: float, calories: int,
               available: bool, category_id: int) -> Dish:
        dish = Dish(name=name.strip(), description=description, price=price,
                    calories=calories, available=available, category_id=category_id)
        db.session.add(dish)
        db.session.commit()
        return dish

    def update(self, dish_id: int, fields: dict) -> Optional[Dish]:
        dish = self.get(dish_id)
        if dish is None:
            return None
        for key, value in fields.items():
            setattr(dish, key, value)
        db.session.commit()
        return dish

    def delete(self, dish_id: int) -> bool:
        dish = self.get(dish_id)
        if dish is None:
            return False
        db.session.delete(dish)
        db.session.commit()
        return True


class OrderRepository:
    """Доступ к заказам."""

    def get_all(self) -> List[Order]:
        return list(Order.query.order_by(Order.id.desc()).all())

    def get(self, order_id: int) -> Optional[Order]:
        return db.session.get(Order, order_id)

    def create(self, customer_name: str, dish_ids: List[int]) -> Order:
        dishes = Dish.query.filter(Dish.id.in_(dish_ids)).all()
        order = Order(customer_name=customer_name.strip(), status="принят",
                      created_at=str(__import__("datetime").datetime.now().date()))
        order.dishes = dishes
        db.session.add(order)
        db.session.commit()
        return order

    def set_status(self, order_id: int, status: str) -> Optional[Order]:
        order = self.get(order_id)
        if order is None:
            return None
        order.status = status
        db.session.commit()
        return order

    def delete(self, order_id: int) -> bool:
        order = self.get(order_id)
        if order is None:
            return False
        db.session.delete(order)
        db.session.commit()
        return True