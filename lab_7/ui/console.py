from services.domain_service import HotelService
from services.report_service import ReportService
from models.entities import Room

# SRP: UI отвечает только за ввод/вывод. Никакой бизнес-логики.
class ConsoleUI:
    def __init__(self, hotel_service: HotelService, report_service: ReportService):
        self.hotel_service = hotel_service
        self.report_service = report_service

    def run(self):
        while True:
            print("\n--- МЕНЮ ГОСТИНИЦЫ ---")
            print("1. Добавить номер")
            print("2. Забронировать номер")
            print("3. Заселить гостя")
            print("4. Выселить гостя")
            print("5. Показать отчет")
            print("0. Выход")
            choice = input("Выберите действие: ").strip()

            try:
                if choice == "1":
                    r_id = int(input("ID номера: "))
                    num = input("Номер комнаты: ")
                    price = float(input("Цена за ночь: "))
                    self.hotel_service.room_repo.add(Room(id=r_id, number=num, price_per_night=price))
                    print("Номер добавлен.")
                elif choice == "2":
                    r_id = int(input("ID номера: "))
                    name = input("Имя гостя: ")
                    days = int(input("Количество дней: "))
                    self.hotel_service.book_room(r_id, name, days)
                elif choice == "3":
                    r_id = int(input("ID номера: "))
                    self.hotel_service.check_in(r_id)
                elif choice == "4":
                    r_id = int(input("ID номера: "))
                    self.hotel_service.check_out(r_id)
                elif choice == "5":
                    print(self.report_service.generate_report())
                elif choice == "0":
                    break
            except ValueError as e:
                print(f"Ошибка ввода: {e}")
            except Exception as e:
                print(f"Ошибка: {e}")
