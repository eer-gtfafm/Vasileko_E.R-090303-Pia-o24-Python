import socket
import threading
import unittest

from exceptions import ProtocolError
from protocol import (
    decode_message,
    encode_message,
    make_error,
    make_ok,
    make_request,
)


class TestProtocol(unittest.TestCase):
    def test_encode_decode_roundtrip(self):
        payload = make_request("create", {"title": "Задача", "priority": "высокий"})

        encoded = encode_message(payload)
        self.assertTrue(encoded.endswith(b"\n"))

        decoded = decode_message(encoded)
        self.assertEqual(decoded["command"], "create")
        self.assertEqual(decoded["data"]["priority"], "высокий")

    def test_decode_invalid_json(self):
        with self.assertRaises(ProtocolError):
            decode_message(b"{not json}\n")

    def test_decode_missing_command(self):
        with self.assertRaises(ProtocolError):
            decode_message(b'{"data": {}}\n')

    def test_decode_non_object(self):
        with self.assertRaises(ProtocolError):
            decode_message(b"[1, 2, 3]\n")

    def test_response_builders(self):
        ok = make_ok({"count": 1})
        error = make_error("Задача не найдена")

        self.assertEqual(ok["status"], "ok")
        self.assertEqual(ok["data"]["count"], 1)
        self.assertEqual(error["status"], "error")
        self.assertEqual(error["error"], "Задача не найдена")

    def test_client_receives_timeout(self):
        # Сервер принимает соединение, но не отвечает: клиент должен
        # завершить ожидание по тайм-ауту, а не зависнуть навсегда.
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.bind(("127.0.0.1", 0))
        listener.listen(1)
        address = listener.getsockname()

        def accept_and_wait():
            connection, _ = listener.accept()
            connection.recv(1024)
            threading.Event().wait(3)
            connection.close()

        thread = threading.Thread(target=accept_and_wait, daemon=True)
        thread.start()

        client = socket.create_connection(address, timeout=2)
        client.settimeout(0.5)
        client.sendall(encode_message(make_request("list")))
        with self.assertRaises(socket.timeout):
            client.recv(4096)

        client.close()
        listener.close()


if __name__ == "__main__":
    unittest.main()
