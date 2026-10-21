import pytest

from app.main import _connect


@pytest.fixture(autouse=True)
def clean_database():
    """Очищает таблицу deliveries перед каждым тестом,
    чтобы запуски не зависели от данных предыдущих сессий."""
    connection = _connect()
    try:
        connection.execute("DELETE FROM deliveries")
        connection.commit()
    finally:
        connection.close()
    yield