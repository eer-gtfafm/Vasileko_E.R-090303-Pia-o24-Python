from typing import List, Optional

from sqlalchemy import func, or_, select

from database.models import Booking, Client, Room, RoomType


class NotFoundError(Exception):
    pass


class RoomRepository:
    """Доступ к номерам: поиск свободных, фильтрация, CRUD."""

    def __init__(self, session):
        self._session = session

    def list_all(self) -> List[Room]:
        return list(self._session.scalars(select(Room).order_by(Room.number)))

    def get(self, room_id: int) -> Optional[Room]:
        return self._session.get(Room, room_id)

    def free_rooms(self, capacity: Optional[int] = None) -> List[Room]:
        stmt = select(Room).where(Room.status == Room.STATUS_FREE)
        if capacity:
            stmt = stmt.where(Room.capacity >= capacity)
        return list(self._session.scalars(stmt.order_by(Room.price)))

    def search(self, query: str) -> List[Room]:
        """Поиск по номеру комнаты или типу (регистронезависимо, кириллица-safe)."""
        lowered = query.strip().lower()
        rooms = list(self._session.scalars(
            select(Room).join(RoomType, Room.room_type_id == RoomType.id)
        ))
        return [
            r for r in rooms
            if lowered in r.number.lower()
            or lowered in (r.room_type.name or "").lower()
        ]

    def create(self, number: str, room_type_id: int, price: float,
               capacity: int) -> Room:
        room = Room(number=number, room_type_id=room_type_id, price=price,
                    capacity=capacity, status=Room.STATUS_FREE)
        self._session.add(room)
        self._session.commit()
        return room

    def update(self, room_id: int, fields: dict) -> Optional[Room]:
        room = self.get(room_id)
        if room is None:
            return None
        for key, value in fields.items():
            setattr(room, key, value)
        self._session.commit()
        return room

    def delete(self, room_id: int) -> bool:
        room = self.get(room_id)
        if room is None:
            return False
        self._session.delete(room)
        self._session.commit()
        return True

    def set_status(self, room_id: int, status: str) -> None:
        room = self.get(room_id)
        if room:
            room.status = status
            self._session.commit()


class ClientRepository:
    """Доступ к клиентам (пользователям бота)."""

    def __init__(self, session):
        self._session = session

    def get(self, client_id: int) -> Optional[Client]:
        return self._session.get(Client, client_id)

    def get_by_telegram(self, telegram_id: int) -> Optional[Client]:
        return self._session.scalars(
            select(Client).where(Client.telegram_id == telegram_id)
        ).first()

    def create(self, telegram_id: int, full_name: str) -> Client:
        client = Client(telegram_id=telegram_id, full_name=full_name)
        self._session.add(client)
        self._session.commit()
        return client

    def get_or_create(self, telegram_id: int, full_name: str) -> Client:
        client = self.get_by_telegram(telegram_id)
        if client is None:
            client = self.create(telegram_id, full_name)
        return client

    def list_all(self) -> List[Client]:
        return list(self._session.scalars(select(Client).order_by(Client.id)))


class RoomTypeRepository:
    """Доступ к типам номеров."""

    def __init__(self, session):
        self._session = session

    def list_all(self) -> List[RoomType]:
        return list(self._session.scalars(select(RoomType).order_by(RoomType.name)))

    def get(self, room_type_id: int) -> Optional[RoomType]:
        return self._session.get(RoomType, room_type_id)


class BookingRepository:
    """Доступ к бронированиям."""

    def __init__(self, session):
        self._session = session

    def get(self, booking_id: int) -> Optional[Booking]:
        return self._session.get(Booking, booking_id)

    def list_by_client(self, client_id: int) -> List[Booking]:
        return list(self._session.scalars(
            select(Booking).where(Booking.client_id == client_id).order_by(Booking.id.desc())
        ))

    def create(self, client_id: int, room_id: int, check_in: str,
               check_out: str, nights: int, total: float) -> Booking:
        booking = Booking(client_id=client_id, room_id=room_id, check_in=check_in,
                          check_out=check_out, nights=nights, total=total)
        self._session.add(booking)
        self._session.commit()
        return booking

    def delete(self, booking_id: int) -> bool:
        booking = self.get(booking_id)
        if booking is None:
            return False
        self._session.delete(booking)
        self._session.commit()
        return True