import os
import uuid

import pytest
from fastapi.testclient import TestClient

from app.db import asegurar_restricciones
from app.main import app

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.getenv("NEO4J_INTEGRATION") != "1",
        reason="Defina NEO4J_INTEGRATION=1 y tenga Neo4j levantado",
    ),
]


def test_ciclo_crud_completo_con_neo4j_real():
    asegurar_restricciones()
    c = TestClient(app)
    codigo = f"TEST-{uuid.uuid4().hex[:8]}"
    cuerpo = {"codigo": codigo, "tipo": "MATERIA_PRIMA", "producto": "Leche", "cantidad_kg": 10}

    assert c.post("/lotes", json=cuerpo).status_code == 201
    assert c.post("/lotes", json=cuerpo).status_code == 409  # unicidad real en Neo4j
    assert c.get(f"/lotes/{codigo}").json()["cantidad_kg"] == 10
    assert c.patch(f"/lotes/{codigo}", json={"cantidad_kg": 25}).json()["cantidad_kg"] == 25
    put = {"tipo": "PRODUCTO", "producto": "Queso", "cantidad_kg": 5, "estado": "ACTIVO"}
    assert c.put(f"/lotes/{codigo}", json=put).json()["producto"] == "Queso"
    assert c.delete(f"/lotes/{codigo}").status_code == 204
    assert c.get(f"/lotes/{codigo}").status_code == 404
