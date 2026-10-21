from datetime import date
from typing import Any, Dict, List, Mapping

from exceptions import InvalidIdError, ValidationError

ROOM_TYPES = ("стандартный", "люкс", "семейный")
ROOM_STATUSES = ("свободен", "занят", "на обслуживании")
SORT_FIELDS = {"price": "price_per_night", "number": "number", "capacity": "capacity"}
SORT_ORDERS = ("asc", "desc")


def parse_id(value: Any) -> int:
    try:
        result = int(str(value))
    except (TypeError, ValueError):
        raise InvalidIdError()
    if result <= 0:
        raise InvalidIdError("Идентификатор должен быть положительным целым числом")
    return result


def parse_json_object(payload: Any) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValidationError("Тело запроса должно быть JSON-объектом")
    return payload


def parse_room_type(value: Any) -> str:
    result = str(value).strip().lower()
    if result not in ROOM_TYPES:
        raise ValidationError(f"Недопустимый тип номера, ожидается одно из: {', '.join(ROOM_TYPES)}")
    return result


def parse_status(value: Any) -> str:
    result = str(value).strip().lower()
    if result not in ROOM_STATUSES:
        raise ValidationError(f"Недопустимый статус, ожидается одно из: {', '.join(ROOM_STATUSES)}")
    return result


def parse_number(value: Any) -> str:
    result = str(value).strip() if value is not None else ""
    if not result:
        raise ValidationError("Поле number не может быть пустым")
    return result


def parse_price(value: Any) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError):
        raise ValidationError("Поле price_per_night должно быть числом")
    if result <= 0:
        raise ValidationError("Поле price_per_night должно быть больше 0")
    return round(result, 2)


def parse_capacity(value: Any) -> int:
    try:
        result = int(value)
    except (TypeError, ValueError):
        raise ValidationError("Поле capacity должно быть целым числом")
    if result <= 0:
        raise ValidationError("Поле capacity должно быть больше 0")
    return result


def parse_date(value: Any, field: str) -> str:
    text = str(value).strip() if value is not None else ""
    try:
        return date.fromisoformat(text).isoformat()
    except ValueError:
        raise ValidationError(f"Поле {field} должно быть датой в формате YYYY-MM-DD")


# Валидация тела запроса для POST и PUT (partial=False) и PATCH (partial=True)
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
            raise ValidationError(f"Недопустимое поле сортировки: {', '.join(SORT_FIELDS)}")
        filters["sort"] = sort

    order = args.get("order")
    if order:
        if order not in SORT_ORDERS:
            raise ValidationError("Параметр order должен иметь значение asc или desc")
        filters["order"] = order

    return filters


def parse_booking_payload(payload: Any) -> Dict[str, Any]:
    data = parse_json_object(payload)

    room_id = parse_id(data.get("room_id")) if data.get("room_id") is not None else None
    if room_id is None:
        raise ValidationError("Не передано обязательное поле room_id")

    guest_id = parse_id(data.get("guest_id")) if data.get("guest_id") is not None else None
    if guest_id is None:
        raise ValidationError("Не передано обязательное поле guest_id")

    check_in = parse_date(data.get("check_in"), "check_in")
    check_out = parse_date(data.get("check_out"), "check_out")
    if check_out <= check_in:
        raise ValidationError("Дата выезда должна быть позже даты заезда")

    services: List[Dict[str, int]] = []
    raw_services = data.get("services", [])
    if not isinstance(raw_services, list):
        raise ValidationError("Поле services должно быть массивом")
    for item in raw_services:
        if not isinstance(item, dict) or "service_id" not in item:
            raise ValidationError("Каждая услуга должна содержать service_id")
        quantity = int(item.get("quantity", 1))
        if quantity <= 0:
            raise ValidationError("Количество услуг должно быть больше 0")
        services.append({"service_id": parse_id(item["service_id"]), "quantity": quantity})

    return {
        "room_id": room_id,
        "guest_id": guest_id,
        "check_in": check_in,
        "check_out": check_out,
        "services": services,
    }
