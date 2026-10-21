from typing import Any, Dict, List, Optional

from exceptions import NotFoundError, ValidationError
from models import Priority, Task, TaskStatus
from repository import TaskRepository


# Бизнес-логика работы с учебными задачами.
# Сервис не знает ни про сокеты, ни про JSON: он работает с объектами Task.
class TaskService:
    def __init__(self, repository: TaskRepository):
        self._repository = repository

    def list_tasks(self) -> List[Task]:
        return self._repository.get_all()

    def get_task(self, task_id: int) -> Task:
        task = self._repository.get(task_id)
        if task is None:
            raise NotFoundError(f"Задача с ID {task_id} не найдена")
        return task

    def create_task(self, title: str, priority: str, assignee: str) -> Task:
        task = Task(
            id=self._repository.next_id(),
            title=self._validate_text(title, "Название задачи"),
            priority=self._parse_priority(priority),
            status=TaskStatus.NEW,
            assignee=self._validate_text(assignee, "Исполнитель"),
        )
        self._repository.add(task)
        return task

    def update_task(self, task_id: int, changes: Dict[str, Any]) -> Task:
        task = self.get_task(task_id)

        if "title" in changes:
            task.title = self._validate_text(changes["title"], "Название задачи")
        if "priority" in changes:
            task.priority = self._parse_priority(changes["priority"])
        if "status" in changes:
            task.status = self._parse_status(changes["status"])
        if "assignee" in changes:
            task.assignee = self._validate_text(changes["assignee"], "Исполнитель")

        self._repository.update(task)
        return task

    def delete_task(self, task_id: int) -> None:
        if not self._repository.delete(task_id):
            raise NotFoundError(f"Задача с ID {task_id} не найдена")

    # Специализированная операция варианта: получение задач по приоритету
    def filter_by_priority(self, priority: str) -> List[Task]:
        value = self._parse_priority(priority)
        return [task for task in self._repository.get_all() if task.priority == value]

    # Статистика используется UDP-операцией «статус сервера»
    def get_statistics(self) -> Dict[str, Any]:
        tasks = self._repository.get_all()
        by_status = {status.value: 0 for status in TaskStatus}
        for task in tasks:
            by_status[task.status.value] += 1
        return {"total": len(tasks), "by_status": by_status}

    @staticmethod
    def _validate_text(value: Any, field: str) -> str:
        text = str(value).strip() if value is not None else ""
        if not text:
            raise ValidationError(f"Поле «{field}» не может быть пустым")
        return text

    @staticmethod
    def _parse_priority(value: Any) -> Priority:
        try:
            return Priority(str(value).strip().lower())
        except ValueError:
            allowed = ", ".join(item.value for item in Priority)
            raise ValidationError(f"Недопустимый приоритет, ожидается одно из: {allowed}")

    @staticmethod
    def _parse_status(value: Any) -> TaskStatus:
        try:
            return TaskStatus(str(value).strip().lower())
        except ValueError:
            allowed = ", ".join(item.value for item in TaskStatus)
            raise ValidationError(f"Недопустимый статус, ожидается одно из: {allowed}")
