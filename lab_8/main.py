from factories.room_factory import RoomFactory
from models.enums import RoomType
from observers.observers import EventLogger, GuestNotifier
from repositories.memory_repository import InMemoryRepository
from services.booking_service import BookingService
from strategies.pricing import RegularTariff
from ui.console import ConsoleUI


def build_service() -> tuple[BookingService, EventLogger]:
    # Repository скрывает хранение: сервис получает только интерфейс
    room_repo = InMemoryRepository()
    booking_repo = InMemoryRepository()

    # Strategy передаётся в сервис извне и может быть заменена в любой момент
    service = BookingService(room_repo, booking_repo, RegularTariff())

    # Observer: журнал и уведомления гостю подписываются на события сервиса
    event_logger = EventLogger()
    service.attach(event_logger)
    service.attach(GuestNotifier())

    # Номера создаются через Factory, а не через конструкторы напрямую
    service.add_room(RoomFactory.create(RoomType.STANDARD, 1, "101", 2500))
    service.add_room(RoomFactory.create(RoomType.SUITE, 2, "201", 2500))
    service.add_room(RoomFactory.create(RoomType.FAMILY, 3, "301", 2500))

    return service, event_logger


def main():
    service, event_logger = build_service()
    ui = ConsoleUI(service, event_logger)
    ui.run()


if __name__ == "__main__":
    main()
