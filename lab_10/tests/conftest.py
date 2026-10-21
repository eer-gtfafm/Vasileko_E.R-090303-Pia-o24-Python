import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app  # noqa: E402
from repository import RoomRepository  # noqa: E402
from service import RoomService  # noqa: E402


@pytest.fixture()
def repository():
    return RoomRepository()


@pytest.fixture()
def service(repository):
    return RoomService(repository)


@pytest.fixture()
def app(repository):
    application = create_app(repository=repository, seed=False)
    application.config.update(TESTING=True)
    return application


@pytest.fixture()
def client(app):
    return app.test_client()
