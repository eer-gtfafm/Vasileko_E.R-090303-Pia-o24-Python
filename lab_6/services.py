import inspect
from typing import List, Optional
from models import Room, Guest, Booking, RoomStatus
from exceptions import EntityNotFoundError
# ДОБАВЛЕН ИМПОРТ ДЕКОРАТОРОВ
from decorators import log_call, measure_time, require_status
from context import hotel_operation

class HotelService:
    def __init__(self):
        self.rooms: List[Room] = []
        self.guests: List[Guest] = []
        self.bookings: List[Booking] = []

    def add_room(self, room: Room) -> None:
        self.rooms.append(room)

    def add_guest(self, guest: Guest) -> None:
        self.guests.append(guest)

    def find_room(self, room_id: int) -> Room:
        for room in self.rooms:
            if room.id == room_id:
                return room
        raise EntityNotFoundError(f"Номер с ID {room_id} не найден")

    def find_guest(self, guest_id: int) -> Guest:
        for guest in self.guests:
            if guest.id == guest_id:
                return guest
        raise EntityNotFoundError(f"Гость с ID {guest_id} не найден")

    # ИСПРАВЛЕНО: используем декораторы логов и времени, а контекстный менеджер - внутри через with
    @log_call
    @measure_time
    def book_room(self, room_id: int, guest_id: int, days: int) -> Booking:
        room = self.find_room(room_id)
        guest = self.find_guest(guest_id)
        
        # ИСПРАВЛЕНО: контекстный менеджер вызывается через with
        with hotel_operation("Бронирование номера"):
            self._process_booking(room, guest, days)
            cost = room.calculate_cost(days)
            booking = Booking(
                id=len(self.bookings) + 1,
                guest_id=guest.id,
                room_id=room.id,
                days=days,
                total_cost=cost
            )
            self.bookings.append(booking)
            return booking

    # Декоратор с параметрами
    @require_status(RoomStatus.FREE)
    def _process_booking(self, room: Room, guest: Guest, days: int):
        room.status = RoomStatus.BOOKED
        print(f"Успешно: Гость '{guest.name}' забронировал номер {room.number} на {days} дн.")

    # Статистика
    def get_statistics(self) -> dict:
        total_rooms = len(self.rooms)
        free_rooms = sum(1 for r in self.rooms if r.status == RoomStatus.FREE)
        booked_rooms = sum(1 for r in self.rooms if r.status == RoomStatus.BOOKED)
        
        prices = [r.price_per_night for r in self.rooms]
        min_price = min(prices) if prices else 0
        max_price = max(prices) if prices else 0

        return {
            "Всего номеров": total_rooms,
            "Свободных": free_rooms,
            "Забронировано": booked_rooms,
            "Мин. цена": min_price,
            "Макс. цена": max_price
        }

    # Интроспекция
    def inspect_object(self, obj: object) -> None:
        print("\n=== ИНФОРМАЦИЯ ОБ ОБЪЕКТЕ (ИНТРОСПЕКЦИЯ) ===")
        print(f"Тип объекта: {type(obj).__name__}")
        print(f"Является ли экземпляром Room: {isinstance(obj, Room)}")
        print(f"Является ли подклассом BaseEntity: {issubclass(type(obj), Room) or issubclass(type(obj), Guest)}")
        print(f"Есть ли атрибут 'status': {hasattr(obj, 'status')}")
        if hasattr(obj, 'status'):
            print(f"Значение атрибута 'status': {getattr(obj, 'status')}")
            
        print("Методы объекта:")
        for name, method in inspect.getmembers(obj, predicate=inspect.ismethod):
            if not name.startswith('__'):
                print(f"  - {name}{inspect.signature(method)}")
        print("===========================================\n")