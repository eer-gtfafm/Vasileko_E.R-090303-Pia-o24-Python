import sys
from models import Room, Guest, RoomStatus
from services import HotelService
from exceptions import HotelError

def print_menu():
    print("\n--- МЕНЮ УПРАВЛЕНИЯ ГОСТИНИЦЕЙ ---")
    print("1. Добавить номер")
    print("2. Добавить гостя")
    print("3. Забронировать номер (Доп. операция)")
    print("4. Вывести все номера")
    print("5. Вывести всех гостей")
    print("6. Показать статистику")
    print("7. Демонстрация интроспекции")
    print("0. Выход")

def main():
    service = HotelService()
    
    # Предзаполнение для тестов
    service.add_room(Room(id=1, number="101", price_per_night=2500.0))
    service.add_room(Room(id=2, number="102", price_per_night=3500.0, status=RoomStatus.MAINTENANCE))
    service.add_guest(Guest(id=1, name="Иван Иванов", passport="1234 567890"))

    while True:
        print_menu()
        choice = input("Выберите действие: ").strip()

        try:
            if choice == "1":
                room_id = int(input("Введите ID номера: "))
                number = input("Введите номер комнаты: ")
                price = float(input("Введите цену за ночь: "))
                service.add_room(Room(id=room_id, number=number, price_per_night=price))
                print("Номер добавлен.")

            elif choice == "2":
                guest_id = int(input("Введите ID гостя: "))
                name = input("Введите имя гостя: ")
                passport = input("Введите паспорт: ")
                service.add_guest(Guest(id=guest_id, name=name, passport=passport))
                print("Гость добавлен.")

            elif choice == "3":
                room_id = int(input("Введите ID номера для брони: "))
                guest_id = int(input("Введите ID гостя: "))
                days = int(input("Введите количество дней: "))
                # Здесь сработают контекстный менеджер и декораторы
                booking = service.book_room(room_id, guest_id, days)
                print(f"Бронирование создано! Итоговая стоимость: {booking.total_cost} руб.")

            elif choice == "4":
                print("\nСписок номеров:")
                for r in service.rooms:
                    print(f"  {r.get_report_data()}")

            elif choice == "5":
                print("\nСписок гостей:")
                for g in service.guests:
                    print(f"  ID: {g.id}, Имя: {g.name}")

            elif choice == "6":
                stats = service.get_statistics()
                print("\n--- СТАТИСТИКА ---")
                for key, value in stats.items():
                    print(f"{key}: {value}")

            elif choice == "7":
                if service.rooms:
                    service.inspect_object(service.rooms[0])
                else:
                    print("Нет номеров для интроспекции.")

            elif choice == "0":
                print("Выход из программы...")
                sys.exit(0)

            else:
                print("Неверный пункт меню. Попробуйте снова.")

        except ValueError:
            print("Ошибка: Введите корректное числовое значение.")
        except HotelError as e:
            print(f"Ошибка предметной области: {e}")
        except Exception as e:
            print(f"Непредвиденная ошибка: {e}")

if __name__ == "__main__":
    main()