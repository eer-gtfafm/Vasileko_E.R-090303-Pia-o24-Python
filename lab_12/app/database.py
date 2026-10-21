from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    pass


class Database:
    """Подключение к СУБД: Engine, Session и создание таблиц по моделям ORM."""

    def __init__(self, url: str = "sqlite:///restaurant.db", echo: bool = False):
        self.url = url
        self.engine = create_engine(url, echo=echo)
        self._session_factory = sessionmaker(bind=self.engine, expire_on_commit=False)

    def create_tables(self) -> None:
        Base.metadata.create_all(self.engine)

    def drop_tables(self) -> None:
        Base.metadata.drop_all(self.engine)

    def session(self) -> Session:
        return self._session_factory()