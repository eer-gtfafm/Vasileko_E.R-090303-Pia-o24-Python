"""Исключения приложения и их отображение в HTTP-ответы."""

from dataclasses import dataclass


@dataclass
class AppError(Exception):
    error_code: str
    message: str
    status_code: int = 400


class NotFoundError(AppError):
    def __init__(self, code: str, message: str):
        super().__init__(code, message, 404)


class BusinessRuleError(AppError):
    def __init__(self, code: str, message: str):
        super().__init__(code, message, 409)


class ForbiddenError(AppError):
    def __init__(self, code: str, message: str):
        super().__init__(code, message, 403)
