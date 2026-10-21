from enum import Enum


class RoomType(Enum):
    STANDARD = "стандартный"
    SUITE = "люкс"
    FAMILY = "семейный"


class RoomStatus(Enum):
    FREE = "свободен"
    BOOKED = "забронирован"
    OCCUPIED = "занят"
    MAINTENANCE = "на обслуживании"


class BookingStatus(Enum):
    CREATED = "создано"
    ACTIVE = "гость проживает"
    COMPLETED = "завершено"
    CANCELLED = "отменено"


class TariffType(Enum):
    REGULAR = "обычный тариф"
    SEASONAL = "сезонный тариф"
    WEEKEND = "тариф выходного дня"


class EventType(Enum):
    BOOKING_CREATED = "бронирование создано"
    BOOKING_CANCELLED = "бронирование отменено"
    CHECK_IN = "заселение"
    CHECK_OUT = "выселение"
