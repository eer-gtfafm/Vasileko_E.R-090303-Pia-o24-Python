import unittest

from models import Priority, Task, TaskStatus
from repository import TaskRepository


def make_task(task_id=1):
    return Task(task_id, "Задача", Priority.HIGH, TaskStatus.NEW, "Иванов И. И.")


class TestRepository(unittest.TestCase):
    def test_add_and_get(self):
        repository = TaskRepository()
        task = make_task()

        repository.add(task)

        self.assertIs(repository.get(1), task)
        self.assertIsNone(repository.get(2))

    def test_get_all_update_and_delete(self):
        repository = TaskRepository()
        repository.add(make_task(1))
        repository.add(make_task(2))

        self.assertEqual(len(repository.get_all()), 2)

        task = repository.get(1)
        task.status = TaskStatus.IN_PROGRESS
        repository.update(task)
        self.assertEqual(repository.get(1).status, TaskStatus.IN_PROGRESS)

        self.assertTrue(repository.delete(1))
        self.assertFalse(repository.delete(1))
        self.assertEqual(len(repository.get_all()), 1)

    def test_duplicate_id_is_rejected(self):
        repository = TaskRepository()
        repository.add(make_task(1))

        with self.assertRaises(ValueError):
            repository.add(make_task(1))

    def test_next_id(self):
        repository = TaskRepository()
        self.assertEqual(repository.next_id(), 1)
        repository.add(make_task(5))
        self.assertEqual(repository.next_id(), 6)


if __name__ == "__main__":
    unittest.main()
