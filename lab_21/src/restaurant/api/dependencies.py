"""Зависимости FastAPI: сессия БД и текущий пользователь."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from restaurant.config.database import SessionLocal
from restaurant.models.entities import Customer
from restaurant.services.security import decode_token

bearer = HTTPBearer(auto_error=False)


def get_db() -> iter:
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_customer(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> Customer:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Требуется авторизация")
    try:
        payload = decode_token(credentials.credentials)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    customer = db.get(Customer, int(payload["sub"]))
    if customer is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь не найден")
    return customer


def require_admin(customer: Customer = Depends(get_current_customer)) -> Customer:
    if customer.role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Требуются права администратора")
    return customer
