import pytest

from exceptions import RoomNotFoundError, ValidationError
from models import RoomStatus, RoomType

PAYLOAD = {"number": "101", "room_type": "стандартный", "price_per_night": 2500, "capacity": 2}


def test_create_room(service):
    room = service.create_room(PAYLOAD)

    assert room.id == 1
    assert room.room_type == RoomType.STANDARD
    assert room.status == RoomStatus.FREE
    assert len(service.list_rooms({})) == 1


def test_create_room_validation(service):
    with pytest.raises(ValidationError):
        service.create_room({**PAYLOAD, "price_per_night": -10})
    with pytest.raises(ValidationError):
        service.create_room({**PAYLOAD, "number": "  "})
    with pytest.raises(ValidationError):
        service.create_room({**PAYLOAD, "room_type": "апартаменты"})


def test_patch_and_replace_room(service):
    room = service.create_room(PAYLOAD)

    patched = service.patch_room(room.id, {"price_per_night": 2700})
    assert patched.price_per_night == 2700
    assert patched.number == "101"

    replaced = service.replace_room(room.id, {**PAYLOAD, "number": "202", "capacity": 3})
    assert replaced.number == "202"
    assert replaced.capacity == 3


def test_delete_room(service):
    room = service.create_room(PAYLOAD)

    service.delete_room(room.id)
    assert service.list_rooms({}) == []

    with pytest.raises(RoomNotFoundError):
        service.delete_room(room.id)


def test_filter_and_sort_rooms(service):
    service.create_room({**PAYLOAD, "number": "101", "price_per_night": 2500})
    service.create_room({**PAYLOAD, "number": "102", "price_per_night": 6000, "room_type": "люкс"})
    service.create_room({**PAYLOAD, "number": "103", "price_per_night": 4200, "room_type": "семейный"})

    filtered = service.list_rooms({"room_type": RoomType.SUITE})
    assert [room.number for room in filtered] == ["102"]

    by_price = service.list_rooms({"min_price": 3000, "max_price": 5000})
    assert [room.number for room in by_price] == ["103"]

    sorted_rooms = service.list_rooms({"sort": "price", "order": "desc"})
    assert [room.price_per_night for room in sorted_rooms] == [6000, 4200, 2500]


def test_available_rooms(service):
    service.create_room({**PAYLOAD, "number": "101"})
    service.create_room({**PAYLOAD, "number": "102", "status": "занят"})
    service.create_room({**PAYLOAD, "number": "103", "status": "на обслуживании"})

    available = service.get_available_rooms({})

    assert [room.number for room in available] == ["101"]
    assert all(room.status == RoomStatus.FREE for room in available)
