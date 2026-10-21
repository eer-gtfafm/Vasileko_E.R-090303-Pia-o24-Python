from typing import List

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Customer(Base):
    """Гость ресторана: клиент, оформляющий заказы."""

    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)

    orders: Mapped[List["Order"]] = relationship(
        back_populates="customer", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"Customer(id={self.id}, name={self.full_name!r})"


class Dish(Base):
    """Блюдо из меню ресторана."""

    __tablename__ = "dishes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    category: Mapped[str] = mapped_column(String(60), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    order_items: Mapped[List["OrderItem"]] = relationship(
        back_populates="dish", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"Dish(id={self.id}, name={self.name!r})"


class Order(Base):
    """Заказ: принадлежит клиенту и содержит несколько блюд (позиции)."""

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="принят")
    comment: Mapped[str] = mapped_column(Text, nullable=True)

    customer: Mapped["Customer"] = relationship(back_populates="orders")
    items: Mapped[List["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )

    def total(self) -> float:
        return round(sum(item.subtotal() for item in self.items), 2)

    def __repr__(self) -> str:
        return f"Order(id={self.id}, status={self.status!r})"


class OrderItem(Base):
    """Позиция заказа: связь N:M между заказом и блюдом с количеством."""

    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    dish_id: Mapped[int] = mapped_column(ForeignKey("dishes.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False, default=1)

    order: Mapped["Order"] = relationship(back_populates="items")
    dish: Mapped["Dish"] = relationship(back_populates="order_items")

    def subtotal(self) -> float:
        return round(float(self.dish.price) * self.quantity, 2)

    def __repr__(self) -> str:
        return f"OrderItem(order={self.order_id}, dish={self.dish_id}, qty={self.quantity})"