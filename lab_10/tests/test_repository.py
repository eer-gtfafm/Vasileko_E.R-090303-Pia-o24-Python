import pytest

from models import Room, RoomStatus, RoomType


def make_room(room_id=1, number="101", room_type=RoomType.STANDARD,
              price=2500.0, capacity=2, status=RoomStatus.FREE):
    return Room(room_id, number, room_type, price, capacity, status)


def test_create_and_get_by_id(repository):
    room = make_room()

    repository.create(room)

    assert repository.get_by_id(1) is room
    assert repository.get_by_id(99) is None


def test_get_all_update_and_delete(repository):
    repository.create(make_room(1, "101"))
    repository.create(make_room(2, "102"))

    assert len(repository.get_all()) == 2

    room = repository.get_by_id(1)
    room.status = RoomStatus.OCCUPIED
    repository.update(room)
    assert repository.get_by_id(1).status == RoomStatus.OCCUPIED

    assert repository.delete(1) is True
    assert repository.delete(1) is False
    assert len(repository.get_all()) == 1


def test_duplicate_id_is_rejected(repository):
    repository.create(make_room(1))

    with pytest.raises(ValueError):
        repository.create(make_room(1))


def test_next_id(repository):
    assert repository.next_id() == 1
    repository.create(make_room(5))
    assert repository.next_id() == 6
