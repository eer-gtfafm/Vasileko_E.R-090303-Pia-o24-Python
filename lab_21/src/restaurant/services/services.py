"""Сервисный слой: бизнес-правила ресторана."""

import logging
from datetime import date

from sqlalchemy.orm import Session

from restaurant.exceptions.errors import BusinessRuleError, ForbiddenError, NotFoundError
from restaurant.models.entities import Customer, Delivery, Dish, Order, OrderItem
from restaurant.repositories.repositories import (
    CustomerRepository,
    DeliveryRepository,
    DishRepository,
    OrderItemRepository,
    OrderRepository,
)
from restaurant.schemas.schemas import CustomerCreate, DishCreate, DishUpdate, OrderCreate
from restaurant.services.security import create_access_token, hash_password, verify_password

logger = logging.getLogger("restaurant")


class AuthService:
    """Регистрация и аутентификация клиентов."""

    def __init__(self, session: Session):
        self.customers = CustomerRepository(session)
        self._session = session

    def register(self, payload: CustomerCreate) -> Customer:
        if self.customers.get_by_email(payload.email) is not None:
            raise BusinessRuleError("EMAIL_ALREADY_REGISTERED", "Пользователь с таким email уже зарегистрирован")
        customer = Customer(
            email=payload.email,
            name=payload.name,
            hashed_password=hash_password(payload.password),
            role="USER",
        )
        self.customers.add(customer)
        self.customers.commit()
        logger.info("Зарегистрирован клиент %s (%s)", customer.email, customer.id)
        return customer

    def authenticate(self, email: str, password: str) -> tuple[Customer, str]:
        customer = self.customers.get_by_email(email)
        if customer is None or not verify_password(password, customer.hashed_password):
            raise ForbiddenError("INVALID_CREDENTIALS", "Неверный email или пароль")
        token = create_access_token(customer.id, customer.role)
        return customer, token


class DishService:
    """Каталог блюд (CRUD доступен администратору)."""

    def __init__(self, session: Session):
        self.dishes = DishRepository(session)
        self._session = session

    def list(self, sort: str | None = None) -> list[Dish]:
        return self.dishes.list_sorted(sort) if sort in {"asc", "desc"} else self.dishes.list()

    def list_available(self) -> list[Dish]:
        return self.dishes.list_available()

    def get(self, dish_id: int) -> Dish:
        dish = self.dishes.get(dish_id)
        if dish is None:
            raise NotFoundError("DISH_NOT_FOUND", f"Блюдо с id {dish_id} не найдено")
        return dish

    def create(self, payload: DishCreate) -> Dish:
        dish = Dish(**payload.model_dump())
        self.dishes.add(dish)
        self.dishes.commit()
        logger.info("Создано блюдо %s (id=%s, цена=%.2f)", dish.name, dish.id, dish.price)
        return dish

    def update(self, dish_id: int, payload: DishUpdate) -> Dish:
        dish = self.get(dish_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(dish, field, value)
        self.dishes.commit()
        return dish

    def delete(self, dish_id: int) -> None:
        dish = self.get(dish_id)
        self.dishes.delete(dish)
        self.dishes.commit()


class OrderService:
    """Оформление заказа с бизнес-правилами."""

    def __init__(self, session: Session):
        self.orders = OrderRepository(session)
        self.items = OrderItemRepository(session)
        self.dishes = DishRepository(session)
        self.deliveries = DeliveryRepository(session)
        self._session = session

    def create(self, customer_id: int, payload: OrderCreate) -> Order:
        if len(payload.items) > 20:
            raise BusinessRuleError("TOO_MANY_ITEMS", "Заказ не может содержать более 20 позиций")

        order = Order(customer_id=customer_id, status="CREATED", total=0)
        self.orders.add(order)
        total = 0.0
        for item in payload.items:
            dish = self.dishes.get(item.dish_id)
            if dish is None:
                raise NotFoundError("DISH_NOT_FOUND", f"Блюдо с id {item.dish_id} не найдено")
            if not dish.in_stock:
                raise BusinessRuleError("DISH_OUT_OF_STOCK", f"Блюдо «{dish.name}» отсутствует в меню")
            unit_price = dish.price
            self.items.add(OrderItem(order=order, dish_id=dish.id, quantity=item.quantity, unit_price=unit_price))
            total += unit_price * item.quantity
        if total > 100_000:
            raise BusinessRuleError("ORDER_TOO_EXPENSIVE", "Сумма заказа превышает 100 000 руб.")

        order.total = total
        order.status = "CONFIRMED"
        self.orders.commit()
        logger.info("Создан заказ id=%s клиента %s на сумму %.2f", order.id, customer_id, total)
        return order

    def get_for_customer(self, order_id: int, customer_id: int, is_admin: bool = False) -> Order:
        order = self.orders.get(order_id)
        if order is None:
            raise NotFoundError("ORDER_NOT_FOUND", f"Заказ с id {order_id} не найден")
        if not is_admin and order.customer_id != customer_id:
            raise ForbiddenError("ORDER_ACCESS_DENIED", "Заказ принадлежит другому клиенту")
        return order

    def list_for_customer(self, customer_id: int) -> list[Order]:
        return self.orders.list_by_customer(customer_id)

    def list_all(self) -> list[Order]:
        return self.orders.list()

    def confirm(self, order_id: int) -> Order:
        order = self.orders.get(order_id)
        if order is None:
            raise NotFoundError("ORDER_NOT_FOUND", f"Заказ с id {order_id} не найден")
        if order.status in {"DELIVERED", "CANCELLED"}:
            raise BusinessRuleError("INVALID_STATUS_CHANGE", f"Нельзя изменить статус заказа «{order.status}»")
        order.status = "CONFIRMED"
        self.orders.commit()
        return order

    def cancel(self, order_id: int, customer_id: int) -> Order:
        order = self.get_for_customer(order_id, customer_id)
        if order.status in {"DELIVERED", "CANCELLED"}:
            raise BusinessRuleError("INVALID_STATUS_CHANGE", f"Нельзя отменить заказ в статусе «{order.status}»")
        order.status = "CANCELLED"
        self.orders.commit()
        return order


class DeliveryService:
    """Управление доставкой заказов."""

    def __init__(self, session: Session):
        self.deliveries = DeliveryRepository(session)
        self.orders = OrderRepository(session)
        self._session = session

    def create_for_order(self, order_id: int, address: str, scheduled_date: date | None = None) -> Delivery:
        order = self.orders.get(order_id)
        if order is None:
            raise NotFoundError("ORDER_NOT_FOUND", f"Заказ с id {order_id} не найден")
        if self.deliveries.get_by_order(order_id) is not None:
            raise BusinessRuleError("DELIVERY_EXISTS", "Доставка для этого заказа уже создана")
        if order.status != "CONFIRMED":
            raise BusinessRuleError("ORDER_NOT_CONFIRMED", "Доставку можно создать только для подтверждённого заказа")
        delivery = Delivery(order_id=order.id, address=address, scheduled_date=scheduled_date)
        self.deliveries.add(delivery)
        self.deliveries.commit()
        order.delivery = delivery
        self._session.commit()
        logger.info("Создана доставка id=%s для заказа %s", delivery.id, order_id)
        return delivery

    def get_by_order(self, order_id: int) -> Delivery:
        delivery = self.deliveries.get_by_order(order_id)
        if delivery is None:
            raise NotFoundError("DELIVERY_NOT_FOUND", f"Доставка для заказа {order_id} не найдена")
        return delivery

    def update_status(self, delivery_id: int, status: str) -> Delivery:
        delivery = self.deliveries.get(delivery_id)
        if delivery is None:
            raise NotFoundError("DELIVERY_NOT_FOUND", f"Доставка с id {delivery_id} не найдена")
        valid = {"PENDING", "IN_TRANSIT", "DELIVERED"}
        if status not in valid:
            raise BusinessRuleError("INVALID_DELIVERY_STATUS", f"Недопустимый статус доставки «{status}»")
        delivery.status = status
        self.deliveries.commit()
        return delivery
