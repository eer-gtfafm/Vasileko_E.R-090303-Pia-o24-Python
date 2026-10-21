from typing import List, Any
from interfaces.repository import Repository

# LSP: Реализация репозитория в памяти. Может быть заменена на FileRepository без изменения сервиса.
class InMemoryRepository(Repository):
    def __init__(self):
        self._data: dict[int, Any] = {}

    def add(self, entity: Any) -> None:
        self._data[entity.id] = entity

    def get(self, entity_id: int) -> Any:
        return self._data.get(entity_id)

    def get_all(self) -> List[Any]:
        return list(self._data.values())

    def update(self, entity: Any) -> None:
        if entity.id in self._data:
            self._data[entity.id] = entity