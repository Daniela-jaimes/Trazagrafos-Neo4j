"""Pruebas del arranque y cierre de la aplicación (lifespan)."""
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from neo4j.exceptions import ServiceUnavailable

from app.main import app


def test_arranque_asegura_restricciones_y_cierra_driver():
    """Al arrancar se crea la restricción y al apagar se cierra el driver."""
    with patch("app.main.asegurar_restricciones") as asegurar, \
            patch("app.main.cerrar_driver") as cerrar:
        with TestClient(app):
            asegurar.assert_called_once_with()
            cerrar.assert_not_called()
        cerrar.assert_called_once_with()


def test_arranque_tolera_neo4j_caido():
    """Si Neo4j no responde al arrancar, la API levanta igualmente."""
    with patch("app.main.asegurar_restricciones",
               side_effect=ServiceUnavailable("offline")), \
            patch("app.main.cerrar_driver"):
        with TestClient(app) as cliente:
            assert cliente.get("/openapi.json").status_code == 200


def test_asegurar_restricciones_es_idempotente():
    """La restricción se crea con IF NOT EXISTS y el nombre del seed."""
    from app.db import asegurar_restricciones

    drv = MagicMock()
    asegurar_restricciones(drv)
    query = drv.execute_query.call_args.args[0]
    assert "IF NOT EXISTS" in query and "lote_codigo" in query
