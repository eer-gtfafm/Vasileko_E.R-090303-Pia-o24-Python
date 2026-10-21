import json
from typing import Any, Dict, Optional

from exceptions import ProtocolError

DELIMITER = b"\n"
MAX_MESSAGE_SIZE = 64 * 1024


# Прикладной протокол: newline-delimited JSON.
# Каждое сообщение — один JSON-объект, завершающийся символом \n,
# поэтому граница сообщения определяется однозначно.
def encode_message(payload: Dict[str, Any]) -> bytes:
    try:
        text = json.dumps(payload, ensure_ascii=False)
    except (TypeError, ValueError) as error:
        raise ProtocolError(f"Сообщение невозможно сериализовать: {error}")
    return (text + "\n").encode("utf-8")


def _decode_object(raw: bytes) -> Dict[str, Any]:
    if len(raw) > MAX_MESSAGE_SIZE:
        raise ProtocolError("Сообщение превышает допустимый размер")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise ProtocolError("Сообщение не является корректным UTF-8")

    text = text.strip()
    if not text:
        raise ProtocolError("Пустое сообщение")

    try:
        payload = json.loads(text)
    except json.JSONDecodeError as error:
        raise ProtocolError(f"Некорректный JSON: {error.msg}")

    if not isinstance(payload, dict):
        raise ProtocolError("Сообщение должно быть JSON-объектом")
    return payload


def decode_message(raw: bytes) -> Dict[str, Any]:
    payload = _decode_object(raw)
    if "command" not in payload:
        raise ProtocolError("В запросе отсутствует поле command")
    if not isinstance(payload["command"], str):
        raise ProtocolError("Поле command должно быть строкой")

    payload.setdefault("data", {})
    if not isinstance(payload["data"], dict):
        raise ProtocolError("Поле data должно быть JSON-объектом")
    return payload


def decode_response(raw: bytes) -> Dict[str, Any]:
    payload = _decode_object(raw)
    if payload.get("status") not in ("ok", "error"):
        raise ProtocolError("Некорректное поле status в ответе")
    if payload["status"] == "error" and "error" not in payload:
        raise ProtocolError("В ответе об ошибке отсутствует поле error")
    payload.setdefault("data", {})
    return payload


def make_request(command: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return {"command": command, "data": data or {}}


def make_ok(data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return {"status": "ok", "data": data or {}}


def make_error(message: str) -> Dict[str, Any]:
    return {"status": "error", "error": message}
