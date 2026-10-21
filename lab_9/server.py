import json
import logging
import socket
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, Optional

from exceptions import NotFoundError, ProtocolError, ValidationError
from models import Task
from protocol import decode_message, encode_message, make_error, make_ok
from repository import TaskRepository
from service import TaskService

HOST = "127.0.0.1"
TCP_PORT = 5000
UDP_PORT = 5001
CLIENT_TIMEOUT = 30
MAX_WORKERS = 10

log = logging.getLogger("server")


# Сетевой уровень: сокет, приём запросов, отправка ответов.
# Бизнес-логика находится в TaskService, сеть её не изменяет напрямую.
class TaskServer:
    def __init__(self, service: TaskService, host: str = HOST, port: int = TCP_PORT,
                 max_workers: int = MAX_WORKERS):
        self._service = service
        self._host = host
        self._port = port
        self._max_workers = max_workers
        self._socket: Optional[socket.socket] = None
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._stopped = threading.Event()

    def start(self) -> int:
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind((self._host, self._port))
        self._socket.listen(MAX_WORKERS)
        self._socket.settimeout(0.5)
        self._host, self._port = self._socket.getsockname()
        log.info("Server started on %s:%s", self._host, self._port)
        return self._port

    def serve_forever(self) -> None:
        if self._socket is None:
            self.start()
        try:
            while not self._stopped.is_set():
                try:
                    connection, address = self._socket.accept()
                except socket.timeout:
                    continue
                except OSError:
                    break
                self._executor.submit(self._handle_client, connection, address)
        finally:
            self._executor.shutdown(wait=False)
            if self._socket is not None:
                self._socket.close()
            log.info("Server stopped")

    def stop(self) -> None:
        self._stopped.set()
        if self._socket is not None:
            try:
                self._socket.close()
            except OSError:
                pass

    def _handle_client(self, connection: socket.socket, address) -> None:
        client = f"{address[0]}:{address[1]}"
        log.info("Client connected: %s", client)
        connection.settimeout(CLIENT_TIMEOUT)
        buffer = b""
        try:
            with connection:
                while not self._stopped.is_set():
                    try:
                        chunk = connection.recv(4096)
                    except socket.timeout:
                        log.warning("Client timeout: %s", client)
                        break
                    except ConnectionResetError:
                        log.warning("Connection reset by client: %s", client)
                        break
                    if not chunk:
                        break
                    buffer += chunk
                    while b"\n" in buffer:
                        line, buffer = buffer.split(b"\n", 1)
                        if not line.strip():
                            continue
                        response = self._process_request(line, client)
                        connection.sendall(encode_message(response))
        except OSError as error:
            log.warning("Connection error with %s: %s", client, error)
        finally:
            log.info("Client disconnected: %s", client)

    def _process_request(self, raw: bytes, client: str) -> Dict[str, Any]:
        try:
            request = decode_message(raw)
            log.info("Command: %s from %s", request["command"], client)
            data = self._dispatch(request)
            log.info("Command %s completed", request["command"])
            return make_ok(data)
        except (ProtocolError, ValidationError, NotFoundError) as error:
            log.warning("Bad request from %s: %s", client, error)
            return make_error(str(error))
        except Exception as error:
            log.exception("Unhandled error: %s", error)
            return make_error("Внутренняя ошибка сервера")

    def _dispatch(self, request: Dict[str, Any]) -> Dict[str, Any]:
        command = request["command"]
        data = request["data"]
        handlers = {
            "list": self._list,
            "get": self._get,
            "create": self._create,
            "update": self._update,
            "delete": self._delete,
            "filter_by_priority": self._filter_by_priority,
        }
        handler = handlers.get(command)
        if handler is None:
            raise ProtocolError(f"Неизвестная команда: {command}")
        return handler(data)

    def _list(self, data: Dict[str, Any]) -> Dict[str, Any]:
        tasks = self._service.list_tasks()
        return {"tasks": [task.to_dict() for task in tasks], "count": len(tasks)}

    def _get(self, data: Dict[str, Any]) -> Dict[str, Any]:
        task = self._service.get_task(self._task_id(data))
        return {"task": task.to_dict()}

    def _create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        task = self._service.create_task(
            title=data.get("title"),
            priority=data.get("priority"),
            assignee=data.get("assignee"),
        )
        return {"task": task.to_dict()}

    def _update(self, data: Dict[str, Any]) -> Dict[str, Any]:
        task_id = self._task_id(data)
        changes = {key: value for key, value in data.items() if key != "id"}
        if not changes:
            raise ValidationError("Не переданы поля для изменения")
        task = self._service.update_task(task_id, changes)
        return {"task": task.to_dict()}

    def _delete(self, data: Dict[str, Any]) -> Dict[str, Any]:
        task_id = self._task_id(data)
        self._service.delete_task(task_id)
        return {"deleted": task_id}

    def _filter_by_priority(self, data: Dict[str, Any]) -> Dict[str, Any]:
        priority = data.get("priority")
        tasks = self._service.filter_by_priority(priority)
        return {
            "priority": str(priority),
            "tasks": [task.to_dict() for task in tasks],
            "count": len(tasks),
        }

    @staticmethod
    def _task_id(data: Dict[str, Any]) -> int:
        value = data.get("id")
        if value is None:
            raise ValidationError("Не указан идентификатор задачи")
        try:
            return int(value)
        except (TypeError, ValueError):
            raise ValidationError("Идентификатор задачи должен быть целым числом")


# UDP-операция «статус сервера»: одна датаграмма — один ответ.
# Потеря отдельного запроса не критична, клиент может повторить его.
class UdpStatusServer(threading.Thread):
    def __init__(self, service: TaskService, host: str = HOST, port: int = UDP_PORT):
        super().__init__(daemon=True, name="udp-status")
        self._service = service
        self._host = host
        self._port = port
        self._started_at = time.time()
        self._socket: Optional[socket.socket] = None
        self._stopped = threading.Event()

    def run(self) -> None:
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.bind((self._host, self._port))
        self._socket.settimeout(0.5)
        log.info("UDP status server started on %s:%s", self._host, self._port)
        while not self._stopped.is_set():
            try:
                raw, address = self._socket.recvfrom(4096)
            except socket.timeout:
                continue
            except OSError:
                break
            response = self._process(raw)
            self._socket.sendto(json.dumps(response, ensure_ascii=False).encode("utf-8"), address)
        self._socket.close()
        log.info("UDP status server stopped")

    def stop(self) -> None:
        self._stopped.set()

    def _process(self, raw: bytes) -> Dict[str, Any]:
        try:
            request = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            log.warning("Bad UDP datagram")
            return make_error("Некорректная датаграмма")
        if request.get("command") != "status":
            return make_error(f"Неизвестная команда: {request.get('command')}")
        statistics = self._service.get_statistics()
        statistics["uptime"] = round(time.time() - self._started_at, 1)
        log.info("UDP status requested")
        return make_ok(statistics)


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("server.log", encoding="utf-8"),
        ],
    )


def main() -> None:
    configure_logging()
    service = TaskService(TaskRepository())
    service.create_task("Подготовить отчёт по лабораторной работе", "высокий", "Елисеева Е. Р.")
    service.create_task("Проверить тесты протокола", "средний", "Иванов И. И.")
    service.create_task("Оформить список литературы", "низкий", "Петров П. П.")

    server = TaskServer(service)
    udp_server = UdpStatusServer(service)
    udp_server.start()
    server.start()
    print(f"Сервер запущен на {HOST}:{TCP_PORT}, UDP-статус на {UDP_PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log.info("Server interrupted by user")
    finally:
        udp_server.stop()
        server.stop()


if __name__ == "__main__":
    main()
