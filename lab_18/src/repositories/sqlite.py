import sqlite3
from datetime import date
from typing import List, Optional

from src.models.room import Booking, BookingInterval, Guest, Room
from src.repositories.base import DuplicateError, Repository


class SqliteRepository(Repository):
    """Реализация хранилища на SQLite (для интеграционных тестов)."""

    def __init__(self, db_path: str):
        super().__init__()
        self._db = sqlite3.connect(db_path)
        self._create_schema()

    def _create_schema(self) -> None:
        self._db.executescript(
            """
            CREATE TABLE IF NOT EXISTS rooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                number TEXT NOT NULL UNIQUE,
                price REAL NOT NULL,
                capacity INTEGER NOT NULL,
                status TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS guests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE
            );
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_id INTEGER NOT NULL,
                guest_id INTEGER NOT NULL,
                check_in TEXT NOT NULL,
                check_out TEXT NOT NULL,
                nights INTEGER NOT NULL,
                total REAL NOT NULL
            );
            """
        )
        self._db.commit()

    def close(self) -> None:
        self._db.close()

    def add_room(self, room: Room) -> Room:
        try:
            cursor = self._db.execute(
                "INSERT INTO rooms (number, price, capacity, status) VALUES (?, ?, ?, ?)",
                (room.number, room.price, room.capacity, room.status),
            )
            self._db.commit()
        except sqlite3.IntegrityError:
            raise DuplicateError(f"Номер {room.number} уже существует")
        room.id = cursor.lastrowid
        return room

    def get_room(self, room_id: int) -> Optional[Room]:
        row = self._db.execute("SELECT * FROM rooms WHERE id = ?", (room_id,)).fetchone()
        if row is None:
            return None
        room = Room(row[0], row[1], row[2], row[3], row[4])
        return room

    def list_rooms(self) -> List[Room]:
        rows = self._db.execute("SELECT * FROM rooms ORDER BY id").fetchall()
        return [Room(r[0], r[1], r[2], r[3], r[4]) for r in rows]

    def delete_room(self, room_id: int) -> bool:
        cursor = self._db.execute("DELETE FROM rooms WHERE id = ?", (room_id,))
        self._db.commit()
        return cursor.rowcount > 0

    def update_room_status(self, room_id: int, status: str) -> None:
        self._db.execute("UPDATE rooms SET status = ? WHERE id = ?", (status, room_id))
        self._db.commit()

    def add_guest(self, guest: Guest) -> Guest:
        try:
            cursor = self._db.execute(
                "INSERT INTO guests (full_name, email) VALUES (?, ?)",
                (guest.full_name, guest.email),
            )
            self._db.commit()
        except sqlite3.IntegrityError:
            raise DuplicateError(f"Гость с email {guest.email} уже существует")
        guest.id = cursor.lastrowid
        return guest

    def get_guest(self, guest_id: int) -> Optional[Guest]:
        row = self._db.execute("SELECT * FROM guests WHERE id = ?", (guest_id,)).fetchone()
        if row is None:
            return None
        return Guest(row[0], row[1], row[2] or "")

    def list_guests(self) -> List[Guest]:
        rows = self._db.execute("SELECT * FROM guests ORDER BY id").fetchall()
        return [Guest(r[0], r[1], r[2] or "") for r in rows]

    def add_booking(self, booking: Booking) -> Booking:
        cursor = self._db.execute(
            "INSERT INTO bookings (room_id, guest_id, check_in, check_out, nights, total) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (booking.room_id, booking.guest_id,
             booking.interval.check_in.isoformat(), booking.interval.check_out.isoformat(),
             booking.nights, booking.total),
        )
        self._db.commit()
        booking.id = cursor.lastrowid
        return booking

    def get_booking(self, booking_id: int) -> Optional[Booking]:
        row = self._db.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,)).fetchone()
        if row is None:
            return None
        return self._booking_from_row(row)

    def list_bookings(self) -> List[Booking]:
        rows = self._db.execute("SELECT * FROM bookings ORDER BY id").fetchall()
        return [self._booking_from_row(r) for r in rows]

    def bookings_for_room(self, room_id: int) -> List[Booking]:
        rows = self._db.execute(
            "SELECT * FROM bookings WHERE room_id = ? ORDER BY id", (room_id,)
        ).fetchall()
        return [self._booking_from_row(r) for r in rows]

    def delete_booking(self, booking_id: int) -> bool:
        cursor = self._db.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
        self._db.commit()
        return cursor.rowcount > 0

    def _booking_from_row(self, row) -> Booking:
        interval = BookingInterval(
            date.fromisoformat(row[3]),
            date.fromisoformat(row[4]),
        )
        booking = Booking(row[0], row[1], row[2], interval)
        booking.nights = row[5]
        booking.total = row[6]
        return booking