from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict


class Priority(Enum):
    LOW = "низкий"
    MEDIUM = "средний"
    HIGH = "высокий"


class TaskStatus(Enum):
    NEW = "новая"
    IN_PROGRESS = "в работе"
    DONE = "выполнена"


# Основная сущность предметной области «учебная задача»:
# идентификатор и четыре дополнительных поля.
@dataclass
class Task:
    id: int
    title: str
    priority: Priority
    status: TaskStatus
    assignee: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "priority": self.priority.value,
            "status": self.status.value,
            "assignee": self.assignee,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        return cls(
            id=int(data["id"]),
            title=str(data["title"]),
            priority=Priority(str(data["priority"])),
            status=TaskStatus(str(data["status"])),
            assignee=str(data["assignee"]),
        )
