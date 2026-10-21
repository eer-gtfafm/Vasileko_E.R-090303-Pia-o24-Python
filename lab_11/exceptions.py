class ApiError(Exception):
    """Базовое исключение API: HTTP-код и машиночитаемый код ошибки."""

    def __init__(self, message: str, code: str, status_code: int):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code

    def to_dict(self) -> dict:
        return {"error": self.message, "code": self.code}


class ValidationError(ApiError):
    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR", 400)


class InvalidIdError(ApiError):
    def __init__(self, message: str = "Идентификатор должен быть целым числом"):
        super().__init__(message, "INVALID_ID", 400)


class RoomNotFoundError(ApiError):
    def __init__(self, room_id):
        super().__init__(f"Номер с ID {room_id} не найден", "ROOM_NOT_FOUND", 404)


class GuestNotFoundError(ApiError):
    def __init__(self, guest_id):
        super().__init__(f"Гость с ID {guest_id} не найден", "GUEST_NOT_FOUND", 404)


class RoomNotAvailableError(ApiError):
    def __init__(self, number: str):
        super().__init__(f"Номер {number} недоступен для бронирования", "ROOM_NOT_AVAILABLE", 409)


class RoomInUseError(ApiError):
    def __init__(self, room_id):
        super().__init__(
            f"Номер с ID {room_id} нельзя удалить: на него ссылаются бронирования",
            "ROOM_IN_USE",
            409,
        )


class BookingError(ApiError):
    def __init__(self, message: str):
        super().__init__(message, "BOOKING_ERROR", 400)
