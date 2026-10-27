from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.db import get_driver
from app.main import app


@pytest.fixture
def driver_falso():
    """Instala un driver de Neo4j simulado y lo retira al terminar el test."""
    drv = MagicMock()
    app.dependency_overrides[get_driver] = lambda: drv
    yield drv
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    """Cliente HTTP de prueba (sin ejecutar el arranque de la app)."""
    return TestClient(app)