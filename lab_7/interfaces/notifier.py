from typing import Protocol

# ISP: Отдельный маленький интерфейс для уведомлений.
class Notifier(Protocol):
    def send(self, recipient: str, message: str) -> None: ...