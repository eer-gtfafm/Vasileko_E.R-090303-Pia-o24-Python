import io
import unittest
from contextlib import redirect_stdout

from factories.room_factory import RoomFactory
from models.entities import FamilyRoom, Room, StandardRoom, SuiteRoom
from models.enums import BookingStatus, EventType, RoomStatus, RoomType, TariffType
from observers.observers import EventLogger, GuestNotifier
from repositories.memory_repository import InMemoryRepository
from services.booking_service import BookingService
from strategies.pricing import RegularTariff, SeasonalTariff, WeekendTariff


def make_service(strategy=None):
    service = BookingService(InMemoryRepository(), InMemoryRepository(), strategy or RegularTariff())
    service.add_room(RoomFactory.create(RoomType.STANDARD, 1, "101", 2000))
    service.add_room(RoomFactory.create(RoomType.SUITE, 2, "201", 2000))
    service.add_room(RoomFactory.create(RoomType.FAMILY, 3, "301", 2000))
    return service


class TestFactory(unittest.TestCase):
    def test_factory_creates_rooms_of_different_types(self):
        standard = RoomFactory.create(RoomType.STANDARD, 1, "101", 2000)
        suite = RoomFactory.create(RoomType.SUITE, 2, "201", 2000)
        family = RoomFactory.create(RoomType.FAMILY, 3, "301", 2000)

        self.assertIsInstance(standard, StandardRoom)
        self.assertIsInstance(suite, SuiteRoom)
        self.assertIsInstance(family, FamilyRoom)
        self.assertEqual(standard.room_type, RoomType.STANDARD)
        self.assertGreater(suite.price_per_night, standard.price_per_night)
        self.assertGreater(family.capacity, standard.capacity)

    def test_factory_raises_for_unknown_type(self):
        with self.assertRaises(ValueError):
            RoomFactory.create("unknown", 1, "101", 2000)


class TestStrategy(unittest.TestCase):
    def test_strategy_changes_price(self):
        service = make_service(RegularTariff())
        regular = service.calculate_price(1, 2)

        service.set_strategy(SeasonalTariff())
        seasonal = service.calculate_price(1, 2)

        service.set_strategy(WeekendTariff())
        weekend = service.calculate_price(1, 2)

        self.assertEqual(regular, 4000)
        self.assertGreater(seasonal, regular)
        self.assertLess(weekend, regular)

    def test_booking_saves_applied_tariff(self):
        service = make_service()
        service.set_strategy(SeasonalTariff())

        booking = service.book(1, "Иванов И. И.", 2)

        self.assertEqual(booking.tariff, TariffType.SEASONAL)
        self.assertEqual(booking.total_cost, 5200)


class TestRepository(unittest.TestCase):
    def test_repository_crud(self):
        repository = InMemoryRepository()
        room = RoomFactory.create(RoomType.STANDARD, 10, "110", 1500)

        repository.add(room)
        self.assertIs(repository.get(10), room)
        self.assertEqual(len(repository.get_all()), 1)

        room.status = RoomStatus.MAINTENANCE
        repository.update(room)
        self.assertEqual(repository.get(10).status, RoomStatus.MAINTENANCE)

        repository.delete(10)
        self.assertIsNone(repository.get(10))
        self.assertEqual(repository.get_all(), [])

    def test_service_does_not_depend_on_concrete_repository(self):
        class DictRepository:
            def __init__(self):
                self.data = {}

            def add(self, entity):
                self.data[entity.id] = entity

            def get(self, entity_id):
                return self.data.get(entity_id)

            def get_all(self):
                return list(self.data.values())

            def update(self, entity):
                self.data[entity.id] = entity

            def delete(self, entity_id):
                self.data.pop(entity_id, None)

        service = BookingService(DictRepository(), DictRepository(), RegularTariff())
        service.add_room(RoomFactory.create(RoomType.STANDARD, 1, "101", 1000))

        booking = service.book(1, "Петров П. П.", 3)

        self.assertEqual(booking.total_cost, 3000)
        self.assertEqual(len(service.get_bookings()), 1)


class TestBookingOperations(unittest.TestCase):
    def test_book_room_marks_it_booked(self):
        service = make_service()

        booking = service.book(1, "Сидоров С. С.", 3)

        self.assertEqual(booking.id, 1)
        self.assertEqual(booking.total_cost, 6000)
        self.assertEqual(service.get_rooms()[0].status, RoomStatus.BOOKED)
        self.assertEqual(service.get_bookings()[0].guest_name, "Сидоров С. С.")

    def test_cannot_book_busy_room(self):
        service = make_service()
        service.book(1, "Сидоров С. С.", 3)

        with self.assertRaises(ValueError):
            service.book(1, "Петров П. П.", 1)

    def test_booking_rejects_invalid_days(self):
        service = make_service()

        with self.assertRaises(ValueError):
            service.book(1, "Сидоров С. С.", 0)

    def test_cancel_frees_room(self):
        service = make_service()
        booking = service.book(1, "Сидоров С. С.", 2)

        service.cancel(booking.id)

        self.assertEqual(service.get_rooms()[0].status, RoomStatus.FREE)
        self.assertEqual(service.get_bookings()[0].status, BookingStatus.CANCELLED)

    def test_check_in_and_check_out(self):
        service = make_service()
        booking = service.book(2, "Сидоров С. С.", 2)

        service.check_in(booking.id)
        self.assertEqual(service.get_rooms()[1].status, RoomStatus.OCCUPIED)

        service.check_out(booking.id)
        self.assertEqual(service.get_rooms()[1].status, RoomStatus.FREE)
        self.assertEqual(service.get_bookings()[0].status, BookingStatus.COMPLETED)


class TestObserver(unittest.TestCase):
    def test_observers_receive_event(self):
        service = make_service()
        logger = EventLogger()
        notifier = GuestNotifier()
        service.attach(logger)
        service.attach(notifier)

        with redirect_stdout(io.StringIO()):
            service.book(1, "Иванов И. И.", 2)

        self.assertEqual(len(logger.journal), 1)
        self.assertEqual(logger.journal[0].type, EventType.BOOKING_CREATED)

    def test_detached_observer_gets_no_events(self):
        service = make_service()
        logger = EventLogger()
        service.attach(logger)

        with redirect_stdout(io.StringIO()):
            service.book(1, "Иванов И. И.", 2)
        service.detach(logger)

        with redirect_stdout(io.StringIO()):
            service.book(2, "Петров П. П.", 1)

        self.assertEqual(len(logger.journal), 1)


if __name__ == "__main__":
    unittest.main()
