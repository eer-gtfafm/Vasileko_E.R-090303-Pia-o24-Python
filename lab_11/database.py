import sqlite3
from contextlib import contextmanager
from pathlib import Path
from threading import RLock
from typing import Any, Iterator, List, Optional, Sequence

BASE_DIR = Path(__file__).resolve().parent
SCHEMA_PATH = BASE_DIR / "schema.sql"
SEED_PATH = BASE_DIR / "seed.sql"


# Обёртка над sqlite3: единое подключение, блокировка для потоков Flask
# и явное управление транзакциями.
class Database:
    def __init__(self, path: str = "hotel.db"):
        self.path = path
        self._lock = RLock()
        self._in_transaction = False
        self.connection = sqlite3.connect(path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")

    def execute(self, sql: str, params: Sequence[Any] = ()) -> sqlite3.Cursor:
        with self._lock:
            cursor = self.connection.execute(sql, params)
            if not self._in_transaction:
                self.connection.commit()
            return cursor

    def query_all(self, sql: str, params: Sequence[Any] = ()) -> List[sqlite3.Row]:
        with self._lock:
            return self.connection.execute(sql, params).fetchall()

    def query_one(self, sql: str, params: Sequence[Any] = ()) -> Optional[sqlite3.Row]:
        with self._lock:
            return self.connection.execute(sql, params).fetchone()

    def executescript(self, path: Path) -> None:
        with self._lock:
            self.connection.executescript(Path(path).read_text(encoding="utf-8"))
            self.connection.commit()

    # Транзакция: все операции выполняются целиком или откатываются
    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        with self._lock:
            self._in_transaction = True
            try:
                self.connection.execute("BEGIN IMMEDIATE")
                yield self.connection
                self.connection.commit()
            except Exception:
                self.connection.rollback()
                raise
            finally:
                self._in_transaction = False

    def close(self) -> None:
        self.connection.close()


def init_db(db: Database, seed: bool = True) -> None:
    db.executescript(SCHEMA_PATH)
    if seed:
        db.executescript(SEED_PATH)


def row_to_dict(row: Optional[sqlite3.Row]) -> Optional[dict]:
    return dict(row) if row is not None else None


def rows_to_dicts(rows: List[sqlite3.Row]) -> List[dict]:
    return [dict(row) for row in rows]
