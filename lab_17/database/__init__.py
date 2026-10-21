from functools import lru_cache

from database.models import Database

from config import get_settings


@lru_cache(maxsize=1)
def get_db() -> Database:
    """Один объект Database на процесс (кэш)."""
    return Database(get_settings().database_url)