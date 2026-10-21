import unittest

from exceptions import NotFoundError, ValidationError
from models import Priority, TaskStatus
from repository import TaskRepository
from service import TaskService


class TestService(unittest.TestCase):
    def setUp(self):
        self.service = TaskService(TaskRepository())

    def test_create_task(self):
        task = self.service.create_task("Написать отчёт", "высокий", "Иванов И. И.")

        self.assertEqual(task.id, 1)
        self.assertEqual(task.priority, Priority.HIGH)
        self.assertEqual(task.status, TaskStatus.NEW)
        self.assertEqual(len(self.service.list_tasks()), 1)

    def test_create_task_validation(self):
        with self.assertRaises(ValidationError):
            self.service.create_task("", "высокий", "Иванов И. И.")
        with self.assertRaises(ValidationError):
            self.service.create_task("Задача", "срочный", "Иванов И. И.")

    def test_update_and_delete_task(self):
        task = self.service.create_task("Черновик", "низкий", "Петров П. П.")

        updated = self.service.update_task(task.id, {"status": "в работе", "priority": "средний"})
        self.assertEqual(updated.status, TaskStatus.IN_PROGRESS)
        self.assertEqual(updated.priority, Priority.MEDIUM)

        self.service.delete_task(task.id)
        self.assertEqual(self.service.list_tasks(), [])
        with self.assertRaises(NotFoundError):
            self.service.get_task(task.id)

    def test_filter_by_priority(self):
        self.service.create_task("Высокая 1", "высокий", "Иванов И. И.")
        self.service.create_task("Низкая", "низкий", "Петров П. П.")
        self.service.create_task("Высокая 2", "высокий", "Сидоров С. С.")

        high = self.service.filter_by_priority("высокий")
        self.assertEqual(len(high), 2)
        self.assertTrue(all(task.priority == Priority.HIGH for task in high))

        self.assertEqual(self.service.filter_by_priority("низкий")[0].title, "Низкая")

    def test_statistics(self):
        self.service.create_task("Задача 1", "высокий", "Иванов И. И.")
        self.service.create_task("Задача 2", "низкий", "Петров П. П.")

        statistics = self.service.get_statistics()
        self.assertEqual(statistics["total"], 2)
        self.assertEqual(statistics["by_status"][TaskStatus.NEW.value], 2)


if __name__ == "__main__":
    unittest.main()
