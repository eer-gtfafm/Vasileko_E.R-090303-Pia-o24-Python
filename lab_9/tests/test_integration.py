import socket
import threading
import unittest

from client import TaskClient, udp_status
from repository import TaskRepository
from server import TaskServer, UdpStatusServer
from service import TaskService


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.service = TaskService(TaskRepository())
        self.tcp_port = free_port()
        self.server = TaskServer(self.service, port=self.tcp_port)
        self.server.start()
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.stop()
        self.thread.join(timeout=2)

    def make_client(self) -> TaskClient:
        client = TaskClient(port=self.tcp_port)
        client.connect()
        self.addCleanup(client.close)
        return client

    def test_client_server_create_and_list(self):
        client = self.make_client()

        created = client.send_request(
            "create", {"title": "Сдать лабораторную", "priority": "высокий", "assignee": "Иванов И. И."}
        )
        self.assertEqual(created["status"], "ok")
        task_id = created["data"]["task"]["id"]

        listed = client.send_request("list")
        self.assertEqual(listed["status"], "ok")
        self.assertEqual(listed["data"]["count"], 1)
        self.assertEqual(listed["data"]["tasks"][0]["id"], task_id)

    def test_client_server_filter_and_delete(self):
        client = self.make_client()
        client.send_request("create", {"title": "Низкая", "priority": "низкий", "assignee": "Петров П. П."})
        client.send_request("create", {"title": "Высокая", "priority": "высокий", "assignee": "Сидоров С. С."})

        filtered = client.send_request("filter_by_priority", {"priority": "высокий"})
        self.assertEqual(filtered["data"]["count"], 1)
        self.assertEqual(filtered["data"]["tasks"][0]["title"], "Высокая")

        deleted = client.send_request("delete", {"id": filtered["data"]["tasks"][0]["id"]})
        self.assertEqual(deleted["status"], "ok")

        missing = client.send_request("get", {"id": 999})
        self.assertEqual(missing["status"], "error")

    def test_client_server_unknown_command(self):
        client = self.make_client()

        response = client.send_request("unknown")

        self.assertEqual(response["status"], "error")
        self.assertIn("Неизвестная команда", response["error"])

    def test_udp_status(self):
        udp_port = free_port()
        udp_server = UdpStatusServer(self.service, port=udp_port)
        udp_server.start()
        self.addCleanup(udp_server.stop)
        self.service.create_task("Задача", "высокий", "Иванов И. И.")

        response = udp_status(port=udp_port)

        self.assertEqual(response["status"], "ok")
        self.assertEqual(response["data"]["total"], 1)


if __name__ == "__main__":
    unittest.main()
