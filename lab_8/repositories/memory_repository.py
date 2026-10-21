from typing import Any, List, Optional
from interfaces.repository import Repository


# Хранилище в оперативной памяти. Сервис о нём ничего не знает.
class InMemoryRepository(Repository):
    def __init__(self):
        self._data: dict[int, Any] = {}

    def add(self, entity: Any) -> None:
        if entity.id in self._data:
            raise ValueError(f"Объект с ID {entity.id} уже существует")
        self._data[entity.id] = entity

    def get(self, entity_id: int) -> Optional[Any]:
        return self._data.get(entity_id)

    def get_all(self) -> List[Any]:
        return list(self._data.values())

    def update(self, entity: Any) -> None:
        if entity.id not in self._data:
            raise ValueError(f"Объект с ID {entity.id} не найден")
        self._data[entity.id] = entity

    def delete(self, entity_id: int) -> None:
        self._data.pop(entity_id, None)
