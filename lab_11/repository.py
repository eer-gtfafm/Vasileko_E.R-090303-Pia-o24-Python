from typing import Any, Dict, List, Optional, Sequence

from database import Database, row_to_dict, rows_to_dicts
from models import Booking, Room
from schemas import SORT_FIELDS

ROOM_COLUMNS = "id, number, room_type, price_per_night, capacity, status"


# Все запросы параметризованы: значения передаются отдельным кортежем,
# что защищает приложение от SQL-инъекций.
class RoomRepository:
    def __init__(self, db: Database):
        self._db = db

    def list(self, filters: Dict[str, Any]) -> List[dict]:
        conditions: List[str] = []
        params: List[Any] = []

        if "room_type" in filters:
            conditions.append("room_type = ?")
            params.append(filters["room_type"])
        if "status" in filters:
            conditions.append("status = ?")
            params.append(filters["status"])
        if "min_price" in filters:
            conditions.append("price_per_night >= ?")
            params.append(filters["min_price"])
        if "max_price" in filters:
            conditions.append("price_per_night <= ?")
            params.append(filters["max_price"])

        sql = f"SELECT {ROOM_COLUMNS} FROM rooms"
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)

        sort = filters.get("sort")
        if sort:
            direction = "DESC" if filters.get("order") == "desc" else "ASC"
            # имя столбца берётся из белого списка, а не из запроса пользователя
            sql += f" ORDER BY {SORT_FIELDS[sort]} {direction}"
        sql += " ORDER BY id" if not sort else ""

        return rows_to_dicts(self._db.query_all(sql, tuple(params)))

    def get(self, room_id: int) -> Optional[dict]:
        row = self._db.query_one(f"SELECT {ROOM_COLUMNS} FROM rooms WHERE id = ?", (room_id,))
        return row_to_dict(row)

    def get_by_number(self, number: str) -> Optional[dict]:
        row = self._db.query_one(f"SELECT {ROOM_COLUMNS} FROM rooms WHERE number = ?", (number,))
        return row_to_dict(row)

    def create(self, room: Room) -> dict:
        cursor = self._db.execute(
            "INSERT INTO rooms (number, room_type, price_per_night, capacity, status) "
            "VALUES (?, ?, ?, ?, ?)",
            (room.number, room.room_type, room.price_per_night, room.capacity, room.status),
        )
        return self.get(cursor.lastrowid)

    def update(self, room_id: int, data: Dict[str, Any]) -> Optional[dict]:
        if not data:
            return self.get(room_id)
        columns = ", ".join(f"{field} = ?" for field in data)
        params: Sequence[Any] = (*data.values(), room_id)
        self._db.execute(f"UPDATE rooms SET {columns} WHERE id = ?", params)
        return self.get(room_id)

    def delete(self, room_id: int) -> bool:
        cursor = self._db.execute("DELETE FROM rooms WHERE id = ?", (room_id,))
        return cursor.rowcount > 0

    def set_status(self, room_id: int, status: str) -> None:
        self._db.execute("UPDATE rooms SET status = ? WHERE id = ?", (status, room_id))

    # Специализированный запрос варианта: свободные номера с учётом
    # вместимости и пересечения дат с активными бронированиями.
    def available(self, capacity: Optional[int] = None,
                  date_from: Optional[str] = None, date_to: Optional[str] = None) -> List[dict]:
        conditions = ["r.status = 'свободен'"]
        params: List[Any] = []

        if capacity is not None:
            conditions.append("r.capacity >= ?")
            params.append(capacity)

        if date_from and date_to:
            conditions.append(
                "NOT EXISTS (SELECT 1 FROM bookings b "
                "WHERE b.room_id = r.id AND b.status = 'активно' "
                "AND b.check_in < ? AND b.check_out > ?)"
            )
            params.extend([date_to, date_from])

        sql = (
            f"SELECT r.id, r.number, r.room_type, r.price_per_night, r.capacity, r.status "
            f"FROM rooms r WHERE {' AND '.join(conditions)} ORDER BY r.price_per_night"
        )
        return rows_to_dicts(self._db.query_all(sql, tuple(params)))


class GuestRepository:
    def __init__(self, db: Database):
        self._db = db

    def get(self, guest_id: int) -> Optional[dict]:
        row = self._db.query_one(
            "SELECT id, full_name, email, phone FROM guests WHERE id = ?", (guest_id,)
        )
        return row_to_dict(row)

    def list(self) -> List[dict]:
        return rows_to_dicts(self._db.query_all("SELECT id, full_name, email, phone FROM guests ORDER BY id"))


class ServiceRepository:
    def __init__(self, db: Database):
        self._db = db

    def get(self, service_id: int) -> Optional[dict]:
        row = self._db.query_one("SELECT id, name, price FROM services WHERE id = ?", (service_id,))
        return row_to_dict(row)

    def list(self) -> List[dict]:
        return rows_to_dicts(self._db.query_all("SELECT id, name, price FROM services ORDER BY id"))


class BookingRepository:
    def __init__(self, db: Database):
        self._db = db

    # Транзакция: бронирование, его услуги и смена статуса номера
    # сохраняются целиком или не сохраняются вовсе.
    def create(self, booking: Booking, services: List[Dict[str, Any]]) -> dict:
        with self._db.transaction() as connection:
            cursor = connection.execute(
                "INSERT INTO bookings (room_id, guest_id, check_in, check_out, total_price, status) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (booking.room_id, booking.guest_id, booking.check_in,
                 booking.check_out, booking.total_price, booking.status),
            )
            booking_id = cursor.lastrowid
            for item in services:
                connection.execute(
                    "INSERT INTO booking_services (booking_id, service_id, quantity) VALUES (?, ?, ?)",
                    (booking_id, item["service_id"], item["quantity"]),
                )
            connection.execute("UPDATE rooms SET status = 'занят' WHERE id = ?", (booking.room_id,))
        return self.get(booking_id)

    def get(self, booking_id: int) -> Optional[dict]:
        row = self._db.query_one(
            "SELECT b.id, b.room_id, r.number AS room_number, b.guest_id, g.full_name AS guest_name, "
            "b.check_in, b.check_out, b.total_price, b.status "
            "FROM bookings b "
            "JOIN rooms r ON r.id = b.room_id "
            "JOIN guests g ON g.id = b.guest_id "
            "WHERE b.id = ?",
            (booking_id,),
        )
        if row is None:
            return None
        result = row_to_dict(row)
        result["services"] = rows_to_dicts(self._db.query_all(
            "SELECT s.id AS service_id, s.name, bs.quantity, s.price "
            "FROM booking_services bs JOIN services s ON s.id = bs.service_id "
            "WHERE bs.booking_id = ? ORDER BY s.name",
            (booking_id,),
        ))
        return result

    def list(self) -> List[dict]:
        rows = self._db.query_all(
            "SELECT b.id, b.room_id, r.number AS room_number, b.guest_id, g.full_name AS guest_name, "
            "b.check_in, b.check_out, b.total_price, b.status "
            "FROM bookings b "
            "JOIN rooms r ON r.id = b.room_id "
            "JOIN guests g ON g.id = b.guest_id "
            "ORDER BY b.id"
        )
        return rows_to_dicts(rows)
