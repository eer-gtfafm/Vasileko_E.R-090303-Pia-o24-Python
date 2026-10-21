"""Pydantic-схемы запросов/ответов API."""

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

Role = Literal["USER", "ADMIN"]
OrderStatus = Literal["CREATED", "CONFIRMED", "DELIVERED", "CANCELLED"]
DeliveryStatus = Literal["PENDING", "IN_TRANSIT", "DELIVERED"]


class CustomerCreate(BaseModel):
    email: EmailStr
    name: str = Field(min_length=2, max_length=120)
    password: str = Field(min_length=6, max_length=128)


class CustomerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: str
    role: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class DishCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str = Field(default="", max_length=500)
    price: float = Field(gt=0, description="Цена должна быть положительной")
    in_stock: bool = True


class DishUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    price: float | None = Field(default=None, gt=0)
    in_stock: bool | None = None


class DishOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    price: float
    in_stock: bool


class OrderItemIn(BaseModel):
    dish_id: int
    quantity: int = Field(ge=1, le=99)


class OrderCreate(BaseModel):
    items: list[OrderItemIn] = Field(min_length=1)
    address: str = Field(min_length=5, max_length=300)
    delivery_date: date | None = None

    @field_validator("delivery_date")
    @classmethod
    def delivery_date_not_past(cls, value: date | None) -> date | None:
        if value is not None and value < date.today():
            raise ValueError("Дата доставки не может быть в прошлом")
        return value


class OrderItemOut(BaseModel):
    dish_id: int
    name: str
    price: float
    quantity: int
    subtotal: float


class OrderOut(BaseModel):
    id: int
    customer_id: int
    status: str
    total: float
    items: list[OrderItemOut]
    delivery_address: str | None = None
    delivery_status: str | None = None


class DeliveryCreate(BaseModel):
    address: str = Field(min_length=5, max_length=300)
    scheduled_date: date | None = None


class DeliveryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    address: str
    status: str
    scheduled_date: date | None


class ErrorOut(BaseModel):
    error: str
    message: str
