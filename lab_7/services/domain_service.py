from models.entities import Room, Booking
from models.enums import RoomStatus
from interfaces.repository import Repository
from interfaces.notifier import Notifier

# SRP: Сервис отвечает только за бизнес-логику бронирования.
# DIP: Зависимости (репозитории и уведомитель) передаются извне через конструктор (Dependency Injection).
class HotelService:
    def __init__(self, room_repo: Repository, booking_repo: Repository, notifier: Notifier):
        self.room_repo = room_repo
        self.booking_repo = booking_repo
        self.notifier = notifier

    def book_room(self, room_id: int, guest_name: str, days: int) -> Booking:
        room = self.room_repo.get(room_id)
        if not room:
            raise ValueError("Номер не найден")
        
        if room.status != RoomStatus.FREE:
            raise ValueError(f"Номер {room.number} недоступен (статус: {room.status.value})")

        room.status = RoomStatus.BOOKED
        self.room_repo.update(room)

        cost = room.price_per_night * days
        booking = Booking(
            id=len(self.booking_repo.get_all()) + 1,
            room_id=room.id,
            guest_name=guest_name,
            days=days,
            total_cost=cost
        )
        self.booking_repo.add(booking)
        
        self.notifier.send(guest_name, f"Вы забронировали номер {room.number} на {days} дней. Стоимость: {cost} руб.")
        return booking

    def check_in(self, room_id: int) -> None:
        room = self.room_repo.get(room_id)
        if not room:
            raise ValueError("Номер не найден")
        if room.status != RoomStatus.BOOKED:
            raise ValueError(f"Нельзя заселиться: номер {room.number} не забронирован")
        
        room.status = RoomStatus.OCCUPIED
        self.room_repo.update(room)
        self.notifier.send("Администратор", f"Гость заселен в номер {room.number}")

    def check_out(self, room_id: int) -> None:
        room = self.room_repo.get(room_id)
        if not room:
            raise ValueError("Номер не найден")
        if room.status != RoomStatus.OCCUPIED:
            raise ValueError(f"Нельзя выселиться: номер {room.number} не занят")
        
        room.status = RoomStatus.FREE
        self.room_repo.update(room)
        self.notifier.send("Администратор", f"Гость выселен из номера {room.number}. Номер свободен.")
