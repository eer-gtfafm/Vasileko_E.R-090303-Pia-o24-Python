"""Роутер аутентификации."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from restaurant.api.dependencies import get_db
from restaurant.schemas.schemas import CustomerCreate, CustomerOut, LoginRequest, TokenOut
from restaurant.services.services import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=CustomerOut, status_code=201)
def register(payload: CustomerCreate, db: Session = Depends(get_db)) -> CustomerOut:
    customer = AuthService(db).register(payload)
    return CustomerOut.model_validate(customer)


@router.post("/login", response_model=TokenOut)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenOut:
    customer, token = AuthService(db).authenticate(payload.email, payload.password)
    return TokenOut(access_token=token, role=customer.role)
