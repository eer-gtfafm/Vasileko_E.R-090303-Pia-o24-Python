from config import get_settings
from database.models import Database, Room, RoomType


def seed(url: str | None = None) -> None:
    """Заполняет базу тестовыми данными: 3 типа, 20 номеров."""
    db = Database(url or get_settings().database_url)
    db.create_tables()
    session = db.session()

    if session.query(RoomType).count() > 0:
        print("База уже заполнена")
        session.close()
        return

    types = {}
    for name in ("Стандартный", "Люкс", "Семейный"):
        room_type = RoomType(name=name)
        session.add(room_type)
        session.flush()
        types[name] = room_type

    seed_rooms = [
        ("101", "Стандартный", 2500, 2), ("102", "Стандартный", 2700, 2),
        ("103", "Стандартный", 2400, 1), ("104", "Стандартный", 2900, 3),
        ("105", "Стандартный", 2600, 2), ("106", "Стандартный", 2800, 2),
        ("201", "Люкс", 6000, 2), ("202", "Люкс", 6500, 3),
        ("203", "Люкс", 6200, 2), ("204", "Люкс", 6800, 2),
        ("205", "Люкс", 7000, 3), ("206", "Люкс", 7200, 3),
        ("301", "Семейный", 4200, 4), ("302", "Семейный", 4400, 4),
        ("303", "Семейный", 4500, 5), ("304", "Семейный", 4800, 6),
        ("305", "Семейный", 4600, 4), ("306", "Семейный", 5000, 6),
        ("401", "Люкс", 7500, 2), ("402", "Семейный", 5200, 6),
    ]
    for number, type_name, price, capacity in seed_rooms:
        session.add(Room(number=number, room_type_id=types[type_name].id,
                         price=price, capacity=capacity))

    session.commit()
    print(f"Заполнено: 3 типа, {len(seed_rooms)} номеров")
    session.close()


if __name__ == "__main__":
    seed()