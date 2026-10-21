"""Роутер каталога блюд."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from restaurant.api.dependencies import get_db, require_admin
from restaurant.models.entities import Customer
from restaurant.schemas.schemas import DishCreate, DishOut, DishUpdate
from restaurant.services.services import DishService

router = APIRouter(prefix="/dishes", tags=["dishes"])


@router.get("", response_model=list[DishOut])
def list_dishes(sort: str | None = Query(default=None, pattern="^(asc|desc)$"), db: Session = Depends(get_db)):
    return DishService(db).list(sort)


@router.get("/available", response_model=list[DishOut])
def list_available(db: Session = Depends(get_db)):
    return DishService(db).list_available()


@router.get("/{dish_id}", response_model=DishOut)
def get_dish(dish_id: int, db: Session = Depends(get_db)):
    return DishService(db).get(dish_id)


@router.post("", response_model=DishOut, status_code=status.HTTP_201_CREATED)
def create_dish(payload: DishCreate, db: Session = Depends(get_db), _: Customer = Depends(require_admin)):
    return DishService(db).create(payload)


@router.put("/{dish_id}", response_model=DishOut)
def update_dish(dish_id: int, payload: DishUpdate, db: Session = Depends(get_db), _: Customer = Depends(require_admin)):
    return DishService(db).update(dish_id, payload)


@router.delete("/{dish_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dish(dish_id: int, db: Session = Depends(get_db), _: Customer = Depends(require_admin)):
    DishService(db).delete(dish_id)
