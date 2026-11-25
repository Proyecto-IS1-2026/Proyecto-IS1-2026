
import pytest

from qanda import create_app
from qanda.config import TestingConfig


@pytest.fixture
def app():
    aplicacion = create_app(TestingConfig)
    yield aplicacion

    aplicacion.extensions["db_engine"].dispose()


@pytest.fixture
def client(app):
    return app.test_client()
