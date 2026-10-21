from repositories.memory_repository import InMemoryRepository
from infrastructure.notifiers import ConsoleNotifier
from services.domain_service import HotelService
from services.report_service import ReportService
from ui.console import ConsoleUI

def main():
    # DIP: Внедрение зависимостей (Dependency Injection) через конструктор
    room_repo = InMemoryRepository()
    booking_repo = InMemoryRepository()
    notifier = ConsoleNotifier() # Легко заменить на EmailNotifier() или SmsNotifier()

    # Инициализация сервисов
    hotel_service = HotelService(room_repo, booking_repo, notifier)
    report_service = ReportService(room_repo, booking_repo)

    # Запуск UI
    ui = ConsoleUI(hotel_service, report_service)
    ui.run()

if __name__ == "__main__":
    main()