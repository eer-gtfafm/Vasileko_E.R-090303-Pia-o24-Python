from typing import Protocol
from models.entities import Event


# Наблюдатель получает событие и сам решает, что с ним делать.
class Observer(Protocol):
    def update(self, event: Event) -> None: ...
