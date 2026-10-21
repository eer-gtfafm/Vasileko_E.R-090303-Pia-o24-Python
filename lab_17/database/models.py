from typing import Optional

from sqlalchemy import ForeignKey, Integer, Float, String, Date, Text, Numeric, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker


class Base(DeclarativeBase):
    pass


class RoomType(Base):
    """Тип номера (связь 1:N с номерами)."""

    __tablename__ = "room_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)

    rooms: Mapped[list["Room"]] = relationship(back_populates="room_type")

    def __repr__(self) -> str:
        return f"RoomType({self.name!r})"


class Room(Base):
    """Гостиничный номер."""

    __tablename__ = "rooms"

    STATUS_FREE = "свободен"
    STATUS_BOOKED = "занят"

    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[str] = mapped_column(String(10), unique=True)
    price: Mapped[float] = mapped_column(Float)
    capacity: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20), default=STATUS_FREE)

    room_type_id: Mapped[int] = mapped_column(ForeignKey("room_types.id"))
    room_type: Mapped["RoomType"] = relationship(back_populates="rooms")

    bookings: Mapped[list["Booking"]] = relationship(back_populates="room")

    def __repr__(self) -> str:
        return f"Room({self.number!r}, {self.price})"


class Client(Base):
    """Клиент (пользователь Telegram)."""

    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True)
    full_name: Mapped[str] = mapped_column(String(120))

    bookings: Mapped[list["Booking"]] = relationship(back_populates="client")

    def __repr__(self) -> str:
        return f"Client({self.full_name!r})"


class Booking(Base):
    """Бронирование номера клиентом."""

    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    check_in: Mapped[str] = mapped_column(String(20))
    check_out: Mapped[str] = mapped_column(String(20))
    nights: Mapped[int] = mapped_column(Integer)
    total: Mapped[float] = mapped_column(Float)

    client: Mapped["Client"] = relationship(back_populates="bookings")
    room: Mapped["Room"] = relationship(back_populates="bookings")

    def __repr__(self) -> str:
        return f"Booking({self.room.number!r}, {self.client.full_name!r})"


class Database:
    """Подключение к БД и сессия SQLAlchemy."""

    def __init__(self, url: str = "sqlite:///hotel_bot.db"):
        self.engine = create_engine(
            url, connect_args={"check_same_thread": False} if url.startswith("sqlite") else {}
        )
        self._session_factory = sessionmaker(bind=self.engine, expire_on_commit=False)

    def create_tables(self) -> None:
        Base.metadata.create_all(self.engine)

    def drop_tables(self) -> None:
        Base.metadata.drop_all(self.engine)

    def session(self):
        return self._session_factory()