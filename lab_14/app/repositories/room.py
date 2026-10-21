from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.room import Room


class RoomNotFoundError(Exception):
    pass


class RoomRepository:
    """Доступ к данным: CRUD, фильтрация, сортировка, пагинация, статистика."""

    def __init__(self, db: Session):
        self._db = db

    def get(self, room_id: int) -> Optional[Room]:
        return self._db.get(Room, room_id)

    def get_by_number(self, number: str) -> Optional[Room]:
        return self._db.scalars(select(Room).where(Room.number == number)).first()

    def list(self, room_type: Optional[str] = None, min_price: Optional[float] = None,
             max_price: Optional[float] = None, available: Optional[bool] = None,
             sort: str = "price", order: str = "asc",
             skip: int = 0, limit: int = 20) -> Tuple[List[Room], int]:
        stmt = select(Room)
        count_stmt = select(func.count(Room.id))
        if room_type:
            stmt = stmt.where(Room.room_type == room_type)
            count_stmt = count_stmt.where(Room.room_type == room_type)
        if min_price is not None:
            stmt = stmt.where(Room.price >= min_price)
            count_stmt = count_stmt.where(Room.price >= min_price)
        if max_price is not None:
            stmt = stmt.where(Room.price <= max_price)
            count_stmt = count_stmt.where(Room.price <= max_price)
        if available is not None:
            stmt = stmt.where(Room.available == available)
            count_stmt = count_stmt.where(Room.available == available)

        column = {"price": Room.price, "number": Room.number, "capacity": Room.capacity}.get(sort, Room.price)
        stmt = stmt.order_by(column.asc() if order == "asc" else column.desc())
        stmt = stmt.offset(skip).limit(limit)

        return list(self._db.scalars(stmt)), int(self._db.scalar(count_stmt) or 0)

    def search(self, query: str, limit: int = 20) -> List[Room]:
        pattern = f"%{query}%"
        stmt = select(Room).where(Room.number.contains(query) | Room.room_type.contains(query)).limit(limit)
        return list(self._db.scalars(stmt))

    def create(self, number: str, room_type: str, floor: int, capacity: int,
               price: float, available: bool, amenities: List[str]) -> Room:
        room = Room(
            number=number, room_type=room_type, floor=floor, capacity=capacity,
            price=price, available=available, amenities=",".join(amenities),
        )
        self._db.add(room)
        self._db.commit()
        self._db.refresh(room)
        return room

    def update(self, room_id: int, fields: dict) -> Optional[Room]:
        room = self.get(room_id)
        if room is None:
            return None
        for key, value in fields.items():
            setattr(room, key, value)
        self._db.commit()
        self._db.refresh(room)
        return room

    def delete(self, room_id: int) -> bool:
        room = self.get(room_id)
        if room is None:
            return False
        self._db.delete(room)
        self._db.commit()
        return True

    def statistics(self) -> dict:
        total = int(self._db.scalar(select(func.count(Room.id))) or 0)
        available_count = int(self._db.scalar(select(func.count(Room.id)).where(Room.available.is_(True))) or 0)
        average_price = float(self._db.scalar(select(func.avg(Room.price))) or 0.0)
        min_price = float(self._db.scalar(select(func.min(Room.price))) or 0.0)
        max_price = float(self._db.scalar(select(func.max(Room.price))) or 0.0)
        return {
            "total": total,
            "available_count": available_count,
            "average_price": round(average_price, 2),
            "min_price": min_price,
            "max_price": max_price,
        }

    def count(self) -> int:
        return int(self._db.scalar(select(func.count(Room.id))) or 0)