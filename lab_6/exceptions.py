class HotelError(Exception):
    """Базовое исключение для предметной области."""
    pass

class RoomNotAvailableError(HotelError):
    """Номер недоступен для бронирования."""
    pass

class EntityNotFoundError(HotelError):
    """Объект не найден в системе."""
    pass