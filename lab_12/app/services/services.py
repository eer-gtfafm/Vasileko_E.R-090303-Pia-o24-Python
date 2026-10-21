from typing import Dict, List, Optional, Sequence, Tuple

from app.models.entities import Customer, Dish, Order
from app.repositories.order_repository import OrderRepository
from app.repositories.repositories import CustomerRepository, DishRepository


class DuplicateError(Exception):
    """Попытка создать дубликат (одинаковый телефон клиента или название блюда)."""


class NotFoundError(Exception):
    """Объект не найден."""


class OrderError(Exception):
    """Некорректная бизнес-операция с заказом."""


class CustomerService:
    def __init__(self, repository: CustomerRepository):
        self._repository = repository

    def list(self) -> List[Customer]:
        return self._repository.get_all()

    def get(self, customer_id: int) -> Customer:
        customer = self._repository.get(customer_id)
        if customer is None:
            raise NotFoundError(f"Клиент с ID {customer_id} не найден")
        return customer

    def create(self, full_name: str, phone: str) -> Customer:
        if self._repository.get_by_phone(phone) is not None:
            raise DuplicateError(f"Клиент с телефоном {phone} уже существует")
        if not full_name.strip():
            raise OrderError("Имя клиента не может быть пустым")
        return self._repository.create(full_name.strip(), phone.strip())

    def update(self, customer_id: int, full_name: Optional[str] = None,
               phone: Optional[str] = None) -> Customer:
        customer = self._repository.update(customer_id, full_name, phone)
        if customer is None:
            raise NotFoundError(f"Клиент с ID {customer_id} не найден")
        return customer

    def delete(self, customer_id: int) -> None:
        if not self._repository.delete(customer_id):
            raise NotFoundError(f"Клиент с ID {customer_id} не найден")


class DishService:
    def __init__(self, repository: DishRepository):
        self._repository = repository

    def list(self) -> List[Dish]:
        return self._repository.get_all()

    def get(self, dish_id: int) -> Dish:
        dish = self._repository.get(dish_id)
        if dish is None:
            raise NotFoundError(f"Блюдо с ID {dish_id} не найдено")
        return dish

    def find(self, category: Optional[str] = None, search: Optional[str] = None,
             sort_by_price: bool = False) -> List[Dish]:
        return self._repository.find(category=category, search=search, sort_by_price=sort_by_price)

    def create(self, name: str, category: str, price: float) -> Dish:
        if self._repository.get_by_name(name) is not None:
            raise DuplicateError(f"Блюдо «{name}» уже есть в меню")
        if price <= 0:
            raise OrderError("Цена должна быть положительной")
        return self._repository.create(name.strip(), category.strip(), price)

    def update(self, dish_id: int, name: Optional[str] = None,
               category: Optional[str] = None, price: Optional[float] = None) -> Dish:
        dish = self._repository.update(dish_id, name, category, price)
        if dish is None:
            raise NotFoundError(f"Блюдо с ID {dish_id} не найдено")
        return dish

    def delete(self, dish_id: int) -> None:
        if not self._repository.delete(dish_id):
            raise NotFoundError(f"Блюдо с ID {dish_id} не найдено")


class OrderService:
    def __init__(self, order_repository: OrderRepository,
                 dish_repository: DishRepository,
                 customer_repository: CustomerRepository):
        self._orders = order_repository
        self._dishes = dish_repository
        self._customers = customer_repository

    def list(self) -> List[Order]:
        return self._orders.get_all()

    def get(self, order_id: int) -> Order:
        order = self._orders.get(order_id)
        if order is None:
            raise NotFoundError(f"Заказ с ID {order_id} не найден")
        return order

    def orders_of_customer(self, customer_id: int) -> List[Order]:
        self._customers.get(customer_id) or (lambda: (_ for _ in ()).throw(NotFoundError(f"Клиент с ID {customer_id} не найден")))()
        return self._orders.get_by_customer(customer_id)

    # Транзакционная операция: проверка блюд и клиента, создание заказа
    # и позиций, расчёт стоимости — атомарно через одну сессию.
    def create_order(self, customer_id: int, items: Sequence[Tuple[int, int]],
                     comment: Optional[str] = None) -> Order:
        customer = self._customers.get(customer_id)
        if customer is None:
            raise NotFoundError(f"Клиент с ID {customer_id} не найден")
        if not items:
            raise OrderError("Заказ должен содержать хотя бы одно блюдо")
        for dish_id, quantity in items:
            dish = self._dishes.get(dish_id)
            if dish is None:
                raise NotFoundError(f"Блюдо с ID {dish_id} не найдено")
            if quantity <= 0:
                raise OrderError("Количество блюда должно быть положительным")
        return self._orders.create_with_items(customer_id, items, comment)

    def add_item(self, order_id: int, dish_id: int, quantity: int) -> None:
        order = self.get(order_id)
        dish = self._dishes.get(dish_id)
        if dish is None:
            raise NotFoundError(f"Блюдо с ID {dish_id} не найдено")
        if quantity <= 0:
            raise OrderError("Количество блюда должно быть положительным")
        self._orders.add_item(order.id, dish_id, quantity)

    def change_quantity(self, item_id: int, quantity: int) -> None:
        if quantity <= 0:
            raise OrderError("Количество блюда должно быть положительным")
        if self._orders.set_item_quantity(item_id, quantity) is None:
            raise NotFoundError(f"Позиция с ID {item_id} не найдена")

    def set_status(self, order_id: int, status: str) -> Order:
        allowed = ("принят", "готовится", "выполнен", "отменён")
        if status not in allowed:
            raise OrderError(f"Недопустимый статус, ожидается одно из: {', '.join(allowed)}")
        order = self._orders.update_status(order_id, status)
        if order is None:
            raise NotFoundError(f"Заказ с ID {order_id} не найден")
        return order

    def delete(self, order_id: int) -> None:
        if not self._orders.delete(order_id):
            raise NotFoundError(f"Заказ с ID {order_id} не найден")

    def total(self, order_id: int) -> float:
        return self.get(order_id).total()

    def stats(self) -> Dict[str, float]:
        return self._orders.stats()