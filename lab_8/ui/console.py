from factories.room_factory import RoomFactory
from models.enums import TariffType
from observers.observers import EventLogger
from services.booking_service import BookingService
from strategies.pricing import RegularTariff, SeasonalTariff, WeekendTariff

# Доступные тарифы: UI выбирает стратегию, сервис о ней ничего не знает
TARIFFS = {
    "1": RegularTariff,
    "2": SeasonalTariff,
    "3": WeekendTariff,
}


# SRP: консольный интерфейс отвечает только за ввод и вывод.
class ConsoleUI:
    def __init__(self, booking_service: BookingService, event_logger: EventLogger):
        self.booking_service = booking_service
        self.event_logger = event_logger

    def run(self):
        while True:
            self._print_menu()
            choice = input("Выберите действие: ").strip()

            try:
                if choice == "1":
                    self._show_rooms()
                elif choice == "2":
                    self._add_room()
                elif choice == "3":
                    self._calculate_price()
                elif choice == "4":
                    self._book_room()
                elif choice == "5":
                    booking_id = int(input("ID бронирования: "))
                    self.booking_service.check_in(booking_id)
                elif choice == "6":
                    booking_id = int(input("ID бронирования: "))
                    self.booking_service.check_out(booking_id)
                elif choice == "7":
                    booking_id = int(input("ID бронирования: "))
                    self.booking_service.cancel(booking_id)
                elif choice == "8":
                    self._change_tariff()
                elif choice == "9":
                    self._show_bookings()
                elif choice == "10":
                    print(self.event_logger.show())
                elif choice == "0":
                    print("Работа завершена.")
                    break
                else:
                    print("Неизвестная команда.")
            except ValueError as error:
                print(f"Ошибка: {error}")

    def _print_menu(self):
        print("\n--- МЕНЮ ГОСТИНИЦЫ ---")
        print("1. Показать номера")
        print("2. Добавить номер")
        print("3. Рассчитать стоимость проживания")
        print("4. Забронировать номер")
        print("5. Заселить гостя")
        print("6. Выселить гостя")
        print("7. Отменить бронирование")
        print(f"8. Сменить тариф (сейчас: {self.booking_service.tariff.value})")
        print("9. Показать бронирования")
        print("10. Показать журнал событий")
        print("0. Выход")

    def _show_rooms(self):
        rooms = self.booking_service.get_rooms()
        if not rooms:
            print("Список номеров пуст.")
            return
        print("\nНомера гостиницы:")
        for room in rooms:
            print(f"  ID {room.id}: {room.description()}")

    def _add_room(self):
        types = RoomFactory.types()
        print("\nТипы номеров:")
        for index, room_type in enumerate(types, start=1):
            print(f"  {index}. {room_type.value}")

        type_index = int(input("Тип номера: "))
        if type_index < 1 or type_index > len(types):
            raise ValueError("Некорректный тип номера")

        number = input("Номер комнаты: ").strip()
        base_price = float(input("Базовая цена за ночь: "))

        rooms = self.booking_service.get_rooms()
        room_id = max((room.id for room in rooms), default=0) + 1

        room = RoomFactory.create(types[type_index - 1], room_id, number, base_price)
        self.booking_service.add_room(room)
        print(f"Номер добавлен: {room.description()}")

    def _calculate_price(self):
        room_id = int(input("ID номера: "))
        days = int(input("Количество дней: "))
        cost = self.booking_service.calculate_price(room_id, days)
        print(f"Стоимость по тарифу «{self.booking_service.tariff.value}»: {cost:.2f} руб.")

    def _book_room(self):
        room_id = int(input("ID номера: "))
        guest_name = input("Имя гостя: ").strip()
        days = int(input("Количество дней: "))
        booking = self.booking_service.book(room_id, guest_name, days)
        print(f"Бронирование №{booking.id} создано. Итого: {booking.total_cost:.2f} руб.")

    def _change_tariff(self):
        print("\nДоступные тарифы:")
        for key, strategy in TARIFFS.items():
            print(f"  {key}. {strategy.tariff.value}")
        tariff_key = input("Выберите тариф: ").strip()
        strategy_class = TARIFFS.get(tariff_key)
        if strategy_class is None:
            raise ValueError("Неизвестный тариф")
        self.booking_service.set_strategy(strategy_class())
        print(f"Тариф изменён: {self.booking_service.tariff.value}")

    def _show_bookings(self):
        bookings = self.booking_service.get_bookings()
        if not bookings:
            print("Бронирований нет.")
            return
        print("\nБронирования:")
        for booking in bookings:
            print(f"  {booking.description()}")
