from threading import RLock
from typing import Dict, List, Optional

from models import Task


# Хранилище задач в памяти процесса. Несколько клиентских потоков
# обращаются к нему одновременно, поэтому операции защищены блокировкой.
class TaskRepository:
    def __init__(self):
        self._tasks: Dict[int, Task] = {}
        self._lock = RLock()

    def add(self, task: Task) -> None:
        with self._lock:
            if task.id in self._tasks:
                raise ValueError(f"Задача с ID {task.id} уже существует")
            self._tasks[task.id] = task

    def get(self, task_id: int) -> Optional[Task]:
        with self._lock:
            return self._tasks.get(task_id)

    def get_all(self) -> List[Task]:
        with self._lock:
            return list(self._tasks.values())

    def update(self, task: Task) -> None:
        with self._lock:
            if task.id not in self._tasks:
                raise ValueError(f"Задача с ID {task.id} не найдена")
            self._tasks[task.id] = task

    def delete(self, task_id: int) -> bool:
        with self._lock:
            return self._tasks.pop(task_id, None) is not None

    def next_id(self) -> int:
        with self._lock:
            return max(self._tasks, default=0) + 1
