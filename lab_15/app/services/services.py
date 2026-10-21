from typing import List, Optional

from app.models.models import Category, Dish, Order
from app.repositories.repositories import CategoryRepository, DishRepository, OrderRepository


class NotFoundError(Exception):
    pass


class ConflictError(Exception):
    pass


class ValidationError(Exception):
    pass


class DishService:
    """Бизнес-логика блюд."""

    def __init__(self, repository: DishRepository, category_repository: CategoryRepository):
        self._repository = repository
        self._categories = category_repository

    def list(self, search: Optional[str] = None, category_id: Optional[int] = None,
             available: Optional[bool] = None, sort: str = "name",
             order: str = "asc") -> List[Dish]:
        return self._repository.search(search, category_id, available, sort, order)

    def get(self, dish_id: int) -> Dish:
        dish = self._repository.get(dish_id)
        if dish is None:
            raise NotFoundError(f"Блюдо с ID {dish_id} не найдено")
        return dish

    def create(self, name: str, description: str, price: float, calories: int,
               available: bool, category_id: int) -> Dish:
        if not name.strip():
            raise ValidationError("Название блюда не может быть пустым")
        if price <= 0:
            raise ValidationError("Цена должна быть положительной")
        if calories < 0:
            raise ValidationError("Калорийность не может быть отрицательной")
        if self._categories.get(category_id) is None:
            raise ValidationError(f"Категория с ID {category_id} не существует")
        return self._repository.create(name, description, price, calories, available, category_id)

    def update(self, dish_id: int, fields: dict) -> Dish:
        self.get(dish_id)
        if "price" in fields and fields["price"] is not None and fields["price"] <= 0:
            raise ValidationError("Цена должна быть положительной")
        if "calories" in fields and fields["calories"] is not None and fields["calories"] < 0:
            raise ValidationError("Калорийность не может быть отрицательной")
        dish = self._repository.update(dish_id, fields)
        return dish

    def delete(self, dish_id: int) -> None:
        if not self._repository.delete(dish_id):
            raise NotFoundError(f"Блюдо с ID {dish_id} не найдено")


class CategoryService:
    """Бизнес-логика категорий."""

    def __init__(self, repository: CategoryRepository):
        self._repository = repository

    def list(self) -> List[Category]:
        return self._repository.get_all()

    def create(self, name: str) -> Category:
        if not name.strip():
            raise ValidationError("Название категории не может быть пустым")
        if self._repository.get_by_name(name) is not None:
            raise ConflictError(f"Категория «{name}» уже существует")
        return self._repository.create(name)


class OrderService:
    """Бизнес-логика заказов (работа со связанными сущностями)."""

    def __init__(self, repository: OrderRepository, dish_repository: DishRepository):
        self._repository = repository
        self._dishes = dish_repository

    def list(self) -> List[Order]:
        return self._repository.get_all()

    def get(self, order_id: int) -> Order:
        order = self._repository.get(order_id)
        if order is None:
            raise NotFoundError(f"Заказ с ID {order_id} не найден")
        return order

    def create(self, customer_name: str, dish_ids: List[int]) -> Order:
        if not customer_name.strip():
            raise ValidationError("Имя клиента не может быть пустым")
        if not dish_ids:
            raise ValidationError("Заказ должен содержать хотя бы одно блюдо")
        for dish_id in dish_ids:
            if self._dishes.get(dish_id) is None:
                raise NotFoundError(f"Блюдо с ID {dish_id} не найдено")
        return self._repository.create(customer_name, dish_ids)

    def set_status(self, order_id: int, status: str) -> Order:
        allowed = ("принят", "готовится", "выполнен", "отменён")
        if status not in allowed:
            raise ValidationError(f"Недопустимый статус: {', '.join(allowed)}")
        order = self._repository.set_status(order_id, status)
        if order is None:
            raise NotFoundError(f"Заказ с ID {order_id} не найден")
        return order

    def total(self, order_id: int) -> float:
        return self.get(order_id).total()

    def stats(self) -> dict:
        orders = self._repository.get_all()
        total = len(orders)
        revenue = round(sum(order.total() for order in orders), 2)
        average = round(revenue / total, 2) if total else 0.0
        return {"total": total, "revenue": revenue, "average": average}