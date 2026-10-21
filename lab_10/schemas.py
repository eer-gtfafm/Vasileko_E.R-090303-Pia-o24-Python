from typing import Any, Dict, Mapping

from exceptions import InvalidIdError, ValidationError
from models import RoomStatus, RoomType

ROOM_TYPES = {item.value: item for item in RoomType}
ROOM_STATUSES = {item.value: item for item in RoomStatus}
SORT_FIELDS = {"price": "price_per_night", "number": "number", "capacity": "capacity"}
SORT_ORDERS = ("asc", "desc")


def parse_id(value: Any) -> int:
    try:
        room_id = int(str(value))
    except (TypeError, ValueError):
        raise InvalidIdError()
    if room_id <= 0:
        raise InvalidIdError("Идентификатор должен быть положительным целым числом")
    return room_id


def parse_json_object(payload: Any) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValidationError("Тело запроса должно быть JSON-объектом")
    return payload


def parse_room_type(value: Any) -> RoomType:
    room_type = ROOM_TYPES.get(str(value).strip().lower())
    if room_type is None:
        allowed = ", ".join(ROOM_TYPES)
        raise ValidationError(f"Недопустимый тип номера, ожидается одно из: {allowed}")
    return room_type


def parse_status(value: Any) -> RoomStatus:
    status = ROOM_STATUSES.get(str(value).strip().lower())
    if status is None:
        allowed = ", ".join(ROOM_STATUSES)
        raise ValidationError(f"Недопустимый статус, ожидается одно из: {allowed}")
    return status


def parse_number(value: Any) -> str:
    number = str(value).strip() if value is not None else ""
    if not number:
        raise ValidationError("Поле number не может быть пустым")
    return number


def parse_price(value: Any) -> float:
    try:
        price = float(value)
    except (TypeError, ValueError):
        raise ValidationError("Поле price_per_night должно быть числом")
    if price <= 0:
        raise ValidationError("Поле price_per_night должно быть больше 0")
    return round(price, 2)


def parse_capacity(value: Any) -> int:
    try:
        capacity = int(value)
    except (TypeError, ValueError):
        raise ValidationError("Поле capacity должно быть целым числом")
    if capacity <= 0:
        raise ValidationError("Поле capacity должно быть больше 0")
    return capacity


# Проверка тела запроса. partial=True используется для PATCH.
def parse_room_payload(payload: Any, partial: bool = False) -> Dict[str, Any]:
    data = parse_json_object(payload)
    result: Dict[str, Any] = {}

    if "number" in data:
        result["number"] = parse_number(data["number"])
    elif not partial:
        raise ValidationError("Не передано обязательное поле number")

    if "room_type" in data:
        result["room_type"] = parse_room_type(data["room_type"])
    elif not partial:
        raise ValidationError("Не передано обязательное поле room_type")

    if "price_per_night" in data:
        result["price_per_night"] = parse_price(data["price_per_night"])
    elif not partial:
        raise ValidationError("Не передано обязательное поле price_per_night")

    if "capacity" in data:
        result["capacity"] = parse_capacity(data["capacity"])
    elif not partial:
        raise ValidationError("Не передано обязательное поле capacity")

    if "status" in data:
        result["status"] = parse_status(data["status"])

    if partial and not result:
        raise ValidationError("Не переданы поля для изменения")

    return result


# Разбор query-параметров: фильтрация и сортировка.
def parse_filters(args: Mapping[str, str]) -> Dict[str, Any]:
    filters: Dict[str, Any] = {}

    if args.get("type"):
        filters["room_type"] = parse_room_type(args["type"])
    if args.get("status"):
        filters["status"] = parse_status(args["status"])

    min_price = args.get("min_price")
    max_price = args.get("max_price")
    if min_price not in (None, ""):
        filters["min_price"] = parse_price(min_price)
    if max_price not in (None, ""):
        filters["max_price"] = parse_price(max_price)
    if "min_price" in filters and "max_price" in filters and filters["min_price"] > filters["max_price"]:
        raise ValidationError("min_price не может быть больше max_price")

    sort = args.get("sort")
    if sort:
        if sort not in SORT_FIELDS:
            allowed = ", ".join(SORT_FIELDS)
            raise ValidationError(f"Недопустимое поле сортировки, ожидается одно из: {allowed}")
        filters["sort"] = sort

    order = args.get("order")
    if order:
        if order not in SORT_ORDERS:
            raise ValidationError("Параметр order должен иметь значение asc или desc")
        filters["order"] = order

    return filters
