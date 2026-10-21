from datetime import date

from src.repositories.base import DuplicateError, NotFoundError, ValidationError
from src.repositories.sqlite import SqliteRepository
from src.services.hotel import RoomService


def parse_date(text: str) -> date:
    return date.fromisoformat(text.strip())


def print_rooms(rooms) -> None:
    if not rooms:
        print("Номеров нет.")
        return
    for room in rooms:
        print(f"  [{room.id}] {room.number} — {room.price} ₽/ночь, "
              f"{room.capacity} мест, статус: {room.status}")


def print_bookings(bookings) -> None:
    if not bookings:
        print("Бронирований нет.")
        return
    for b in bookings:
        print(f"  №{b.id}: номер {b.room_id}, гость {b.guest_id}, "
              f"{b.interval.check_in} — {b.interval.check_out} "
              f"({b.nights} ноч., {b.total} ₽)")


def main() -> None:
    repository = SqliteRepository("hotel_test.db")
    service = RoomService(repository)
    print("=== Гостиница: система бронирования номеров ===")

    while True:
        print("\nМеню:")
        print("1. Создать номер")
        print("2. Список номеров")
        print("3. Свободные номера")
        print("4. Регистрация гостя")
        print("5. Бронирование")
        print("6. Отмена бронирования")
        print("7. Список бронирований")
        print("0. Выход")
        choice = input("Выберите действие: ").strip()
        try:
            if choice == "0":
                break
            elif choice == "1":
                number = input("Номер комнаты: ").strip()
                price = float(input("Цена за ночь: "))
                capacity = int(input("Вместимость: "))
                room = service.create_room(number, price, capacity)
                print(f"Номер {room.number} создан (ID {room.id})")
            elif choice == "2":
                print_rooms(service.list_rooms())
            elif choice == "3":
                capacity_raw = input("Мин. вместимость (Enter — любая): ").strip()
                capacity = int(capacity_raw) if capacity_raw else None
                print_rooms(service.find_free_rooms(capacity))
            elif choice == "4":
                name = input("ФИО: ").strip()
                email = input("Email (Enter — без): ").strip()
                guest = service.register_guest(name, email)
                print(f"Гость {guest.full_name} зарегистрирован (ID {guest.id})")
            elif choice == "5":
                room_id = int(input("ID номера: "))
                guest_id = int(input("ID гостя: "))
                check_in = parse_date(input("Дата заезда (ГГГГ-ММ-ДД): "))
                check_out = parse_date(input("Дата выезда (ГГГГ-ММ-ДД): "))
                booking = service.book_room(room_id, guest_id, check_in, check_out)
                print(f"Бронирование №{booking.id}: {booking.nights} ноч., {booking.total} ₽")
            elif choice == "6":
                booking_id = int(input("ID бронирования: "))
                booking = service.cancel_booking(booking_id)
                print(f"Бронирование №{booking.id} отменено")
            elif choice == "7":
                print_bookings(service.bookings_list())
            else:
                print("Неизвестный пункт")
        except (NotFoundError, DuplicateError, ValidationError, ValueError) as error:
            print("Ошибка:", error)

    repository.close()


if __name__ == "__main__":
    main()