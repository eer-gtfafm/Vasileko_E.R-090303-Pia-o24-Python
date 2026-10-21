from typing import List
from interfaces.observer import Observer
from models.entities import Event


# Наблюдатель 1: ведёт журнал всех событий гостиницы.
class EventLogger(Observer):
    def __init__(self):
        self.journal: List[Event] = []

    def update(self, event: Event) -> None:
        self.journal.append(event)
        print(f"[ЖУРНАЛ] {event.type.value}: {event.message}")

    def show(self) -> str:
        if not self.journal:
            return "Журнал пуст."
        lines = ["--- ЖУРНАЛ СОБЫТИЙ ---"]
        for index, event in enumerate(self.journal, start=1):
            lines.append(f"{index}. [{event.type.value}] {event.message}")
        return "\n".join(lines)


# Наблюдатель 2: уведомляет гостя об изменении бронирования.
class GuestNotifier(Observer):
    def update(self, event: Event) -> None:
        print(f"[УВЕДОМЛЕНИЕ] {event.message}")
