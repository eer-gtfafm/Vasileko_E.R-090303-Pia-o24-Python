class TaskServiceError(Exception):
    """Базовое исключение предметной области."""


class ValidationError(TaskServiceError):
    """Переданы некорректные данные."""


class NotFoundError(TaskServiceError):
    """Задача не найдена."""


class ProtocolError(Exception):
    """Нарушен формат сообщения прикладного протокола."""
