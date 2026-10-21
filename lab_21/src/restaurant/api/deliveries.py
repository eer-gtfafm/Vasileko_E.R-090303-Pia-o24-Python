"""Роутер доставки."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from restaurant.api.dependencies import get_current_customer, get_db
from restaurant.models.entities import Customer
from restaurant.schemas.schemas import DeliveryCreate, DeliveryOut
from restaurant.services.services import DeliveryService

router = APIRouter(prefix="/deliveries", tags=["deliveries"])


@router.post("/orders/{order_id}", response_model=DeliveryOut, status_code=status.HTTP_201_CREATED)
def create_delivery(
    order_id: int,
    payload: DeliveryCreate,
    db: Session = Depends(get_db),
    customer: Customer = Depends(get_current_customer),
):
    service = DeliveryService(db)
    delivery = service.create_for_order(order_id, payload.address, payload.scheduled_date)
    return DeliveryOut.model_validate(delivery)


@router.get("/orders/{order_id}", response_model=DeliveryOut)
def get_delivery(order_id: int, db: Session = Depends(get_db), _: Customer = Depends(get_current_customer)):
    return DeliveryOut.model_validate(DeliveryService(db).get_by_order(order_id))


@router.patch("/{delivery_id}", response_model=DeliveryOut)
def update_delivery_status(
    delivery_id: int, status_new: str, db: Session = Depends(get_db), _: Customer = Depends(get_current_customer)
):
    return DeliveryOut.model_validate(DeliveryService(db).update_status(delivery_id, status_new))
