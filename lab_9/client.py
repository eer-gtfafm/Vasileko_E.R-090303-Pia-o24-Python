import json
import socket
import sys
from typing import Any, Dict, Optional

from protocol import decode_response, encode_message, make_request
from server import HOST, TCP_PORT, UDP_PORT

CLIENT_TIMEOUT = 5
MAX_RESPONSE_SIZE = 64 * 1024


class TaskClient:
    def __init__(self, host: str = HOST, port: int = TCP_PORT, timeout: float = CLIENT_TIMEOUT):
        self._host = host
        self._port = port
        self._timeout = timeout
        self._socket: Optional[socket.socket] = None
        self._buffer = b""

    def connect(self) -> None:
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(self._timeout)
        self._socket.connect((self._host, self._port))

    def close(self) -> None:
        if self._socket is not None:
            self._socket.close()
            self._socket = None

    # Отправка запроса и получение одного ответа (до символа \n)
    def send_request(self, command: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if self._socket is None:
            raise ConnectionError("Соединение с сервером не установлено")
        self._socket.sendall(encode_message(make_request(command, data)))
        return self._receive_response()

    def _receive_response(self) -> Dict[str, Any]:
        while b"\n" not in self._buffer:
            chunk = self._socket.recv(4096)
            if not chunk:
                raise ConnectionError("Соединение разорвано сервером")
            self._buffer += chunk
            if len(self._buffer) > MAX_RESPONSE_SIZE:
                raise ValueError("Ответ сервера слишком большой")
        line, self._buffer = self._buffer.split(b"\n", 1)
        return decode_response(line)


def udp_status(host: str = HOST, port: int = UDP_PORT) -> Dict[str, Any]:
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.settimeout(CLIENT_TIMEOUT)
    try:
        udp_socket.sendto(encode_message(make_request("status")), (host, port))
        raw, _ = udp_socket.recvfrom(4096)
        return json.loads(raw.decode("utf-8"))
    finally:
        udp_socket.close()


def print_tasks(tasks) -> None:
    if not tasks:
        print("Задач нет.")
        return
    print(f"{'ID':>3}  {'Приоритет':<9} {'Статус':<10} {'Исполнитель':<20} Название")
    for task in tasks:
        print(f"{task['id']:>3}  {task['priority']:<9} {task['status']:<10} "
              f"{task['assignee']:<20} {task['title']}")


def print_response(response: Dict[str, Any]) -> None:
    if response.get("status") == "error":
        print(f"Ошибка: {response.get('error', 'неизвестная ошибка')}")
        return

    data = response.get("data", {})
    if "tasks" in data:
        print_tasks(data["tasks"])
        print(f"Всего задач: {data.get('count', len(data['tasks']))}")
    elif "task" in data:
        print_tasks([data["task"]])
    elif "deleted" in data:
        print(f"Задача {data['deleted']} удалена.")
    else:
        print(data)


def print_menu() -> None:
    print("\n=== КЛИЕНТ УЧЕБНЫХ ЗАДАЧ ===")
    print("1. Получить список задач")
    print("2. Получить задачу по ID")
    print("3. Создать задачу")
    print("4. Изменить задачу")
    print("5. Удалить задачу")
    print("6. Задачи по приоритету")
    print("7. Статус сервера (UDP)")
    print("0. Выход")


def run_client() -> None:
    client = TaskClient()
    try:
        client.connect()
    except ConnectionRefusedError:
        print(f"Сервер недоступен: {HOST}:{TCP_PORT}. Сначала запустите server.py")
        return
    except socket.timeout:
        print("Тайм-аут подключения к серверу")
        return

    print(f"Подключение установлено: {HOST}:{TCP_PORT}")
    try:
        while True:
            print_menu()
            choice = input("Введите команду: ").strip()
            try:
                if choice == "1":
                    print_response(client.send_request("list"))
                elif choice == "2":
                    task_id = int(input("ID задачи: "))
                    print_response(client.send_request("get", {"id": task_id}))
                elif choice == "3":
                    title = input("Название: ")
                    priority = input("Приоритет (низкий/средний/высокий): ")
                    assignee = input("Исполнитель: ")
                    print_response(client.send_request(
                        "create", {"title": title, "priority": priority, "assignee": assignee}
                    ))
                elif choice == "4":
                    task_id = int(input("ID задачи: "))
                    field = input("Поле (title/priority/status/assignee): ").strip()
                    value = input("Новое значение: ")
                    print_response(client.send_request("update", {"id": task_id, field: value}))
                elif choice == "5":
                    task_id = int(input("ID задачи: "))
                    print_response(client.send_request("delete", {"id": task_id}))
                elif choice == "6":
                    priority = input("Приоритет (низкий/средний/высокий): ")
                    print_response(client.send_request("filter_by_priority", {"priority": priority}))
                elif choice == "7":
                    response = udp_status()
                    print_response(response)
                elif choice == "0":
                    break
                else:
                    print("Неизвестная команда меню.")
            except ValueError as error:
                print(f"Ошибка ввода: {error}")
            except socket.timeout:
                print("Тайм-аут ожидания ответа от сервера")
            except (ConnectionError, OSError) as error:
                print(f"Ошибка соединения: {error}")
                break
    finally:
        client.close()
        print("Соединение закрыто.")


if __name__ == "__main__":
    try:
        run_client()
    except KeyboardInterrupt:
        print("\nКлиент остановлен.")
        sys.exit(0)
