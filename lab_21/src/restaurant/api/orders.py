"""Роутер заказов."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from restaurant.api.dependencies import get_current_customer, get_db, require_admin
from restaurant.models.entities import Customer
from restaurant.schemas.schemas import OrderCreate, OrderItemOut, OrderOut
from restaurant.services.services import OrderService

router = APIRouter(prefix="/orders", tags=["orders"])


def _to_out(order) -> OrderOut:
    items = [
        OrderItemOut(
            dish_id=item.dish_id,
            name=item.dish.name,
            price=item.unit_price,
            quantity=item.quantity,
            subtotal=round(item.unit_price * item.quantity, 2),
        )
        for item in order.items
    ]
    delivery = order.delivery
    return OrderOut(
        id=order.id,
        customer_id=order.customer_id,
        status=order.status,
        total=round(order.total, 2),
        items=items,
        delivery_address=delivery.address if delivery else None,
        delivery_status=delivery.status if delivery else None,
    )


@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
    customer: Customer = Depends(get_current_customer),
):
    order = OrderService(db).create(customer.id, payload)
    return _to_out(order)


@router.get("", response_model=list[OrderOut])
def my_orders(db: Session = Depends(get_db), customer: Customer = Depends(get_current_customer)):
    return [_to_out(o) for o in OrderService(db).list_for_customer(customer.id)]


@router.get("/all", response_model=list[OrderOut])
def all_orders(db: Session = Depends(get_db), _: Customer = Depends(require_admin)):
    return [_to_out(o) for o in OrderService(db).list_all()]


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db), customer: Customer = Depends(get_current_customer)):
    order = OrderService(db).get_for_customer(order_id, customer.id, is_admin=customer.role == "ADMIN")
    return _to_out(order)


@router.post("/{order_id}/confirm", response_model=OrderOut)
def confirm_order(order_id: int, db: Session = Depends(get_db), _: Customer = Depends(require_admin)):
    return _to_out(OrderService(db).confirm(order_id))


@router.post("/{order_id}/cancel", response_model=OrderOut)
def cancel_order(order_id: int, db: Session = Depends(get_db), customer: Customer = Depends(get_current_customer)):
    return _to_out(OrderService(db).cancel(order_id, customer.id))
