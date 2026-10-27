import pytest
from neo4j.exceptions import ConstraintError, ServiceUnavailable
from tests.helpers import LOTE, resultado
LOTE = {
    "codigo": "MP-900", "tipo": "MATERIA_PRIMA", "producto": "Leche",
    "cantidad_kg": 50.0, "estado": "ACTIVO",
}
NUEVO = dict(LOTE)


def resultado(*filas):
    """Simula la tupla que devuelve ``execute_query`` del driver de Neo4j.

    Args:
        *filas: Diccionarios que representan cada fila devuelta.

    Returns:
        Tupla ``(registros, resumen, claves)``.
    """
    return list(filas), None, None

# ------------CREATE
def test_crear_lote_devuelve_201(client, driver_falso):
    """POST /lotes devuelve 201."""
    driver_falso.execute_query.return_value = resultado({"l": LOTE})
    response = client.post("/lotes", json=NUEVO)
    assert response.status_code == 201
    assert response.json()["codigo"] == LOTE["codigo"]


def test_crear_lote_duplicado_409(client, driver_falso):
    """POST /lotes devuelve 409 si el código ya existe."""
    driver_falso.execute_query.side_effect = ConstraintError("duplicado")
    response = client.post("/lotes", json=NUEVO)
    assert response.status_code == 409
    assert "MP-900" in response.json()["detail"]


@pytest.mark.parametrize(
    "cambio",
    [
        {"tipo": "OTRO"},
        {"cantidad_kg": 0},
        {"cantidad_kg": -5},
        {"codigo": ""},
        {"producto": ""},
    ],
)
def test_crear_lote_datos_invalidos_422(client, driver_falso, cambio):
    """POST /lotes devuelve 422 con datos inválidos y no consulta la base."""
    response = client.post("/lotes", json={**NUEVO, **cambio})
    assert response.status_code == 422
    driver_falso.execute_query.assert_not_called()


def test_crear_lote_sin_neo4j_503(client, driver_falso):
    """POST /lotes devuelve 503 si Neo4j no está disponible."""
    driver_falso.execute_query.side_effect = ServiceUnavailable("caído")
    response = client.post("/lotes", json=NUEVO)
    assert response.status_code == 503
    assert response.json()["detail"] == "Neo4j no disponible"


# ---------- READ
def test_obtener_lote_200(client, driver_falso):
    """GET /lotes/{codigo} devuelve 200 y el lote."""
    driver_falso.execute_query.return_value = resultado({"l": LOTE})
    response = client.get("/lotes/MP-900")
    assert response.status_code == 200
    assert response.json()["codigo"] == "MP-900"


def test_obtener_lote_sin_neo4j_503(client, driver_falso):
    """GET /lotes/NOEXISTE devuelve 503 si el lote esta caido"""
    driver_falso.execute_query.side_effect = ServiceUnavailable("caído")
    response = client.get("/lotes/NOEXISTE")
    assert response.status_code == 503


def test_listar_lotes_200(client, driver_falso):
    """GET /lotes devuelve 200 y todos los lotes."""
    driver_falso.execute_query.return_value = resultado({"l": LOTE}, {"l": LOTE})
    response = client.get("/lotes")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_listar_lotes_pasa_filtros_y_paginacion(client, driver_falso):
    """GET /lotes envía a la consulta los filtros y la paginación recibidos."""
    driver_falso.execute_query.return_value = resultado()
    client.get("/lotes?tipo=PRODUCTO&estado=ACTIVO&skip=10&limit=5")
    params = driver_falso.execute_query.call_args.args[1]
    assert params == {"tipo": "PRODUCTO", "estado": "ACTIVO", "skip": 10, "limit": 5}



def test_listar_lotes_vacio_devuelve_lista_vacia(client, driver_falso):
    """GET /lotes sin lotes devuelve 200 y una lista vacía."""
    driver_falso.execute_query.return_value = resultado()
    response = client.get("/lotes")
    assert response.status_code == 200
    assert response.json() == []



def test_obtener_lote_inexistente_devuelve_404(client, driver_falso):
    """GET /lotes/NOEXISTE devuelve 404 si el lote no existe."""
    driver_falso.execute_query.return_value = resultado()
    response = client.get("/lotes/NOEXISTE")
    assert response.status_code == 404
    assert response.json()["detail"] == "Lote 'NOEXISTE' no encontrado"


@pytest.mark.parametrize("qs", ["limit=0", "limit=201", "skip=-1", "tipo=OTRO", "estado=activo"])
def test_listar_lotes_parametros_invalidos_422(client, qs):
    """GET /lotes devuelve 422 si un parámetro de consulta es inválido."""
    response = client.get(f"/lotes?{qs}")
    assert response.status_code == 422


def test_listar_lotes_sin_neo4j_503(client, driver_falso):
    """GET /lotes devuelve 503 si Neo4j no está disponible."""
    driver_falso.execute_query.side_effect = ServiceUnavailable("caído")
    response = client.get("/lotes")
    assert response.status_code == 503


# ------- UPDATE
CUERPO_PUT = {"tipo": "PRODUCTO", "producto": "Queso", "cantidad_kg": 12.5, "estado": "ACTIVO"}


def test_put_200(client, driver_falso):
    """PUT /lotes/{codigo} devuelve 200 y el lote reemplazado."""
    driver_falso.execute_query.return_value = resultado({"l": {**LOTE, **CUERPO_PUT}})
    response = client.put("/lotes/MP-900", json=CUERPO_PUT)
    assert response.status_code == 200
    assert response.json()["producto"] == "Queso"
    params = driver_falso.execute_query.call_args.args[1]
    assert params["codigo"] == "MP-900"


def test_put_inexistente_404(client, driver_falso):
    """PUT /lotes/{codigo} devuelve 404 si el lote no existe."""
    driver_falso.execute_query.return_value = resultado()
    response = client.put("/lotes/NO-EXISTE", json=CUERPO_PUT)
    assert response.status_code == 404


def test_put_cuerpo_incompleto_422(client):
    """PUT /lotes/{codigo} devuelve 422 si faltan campos obligatorios."""
    response = client.put("/lotes/MP-900", json={"producto": "Queso"})
    assert response.status_code == 422


def test_patch_200_solo_envia_campos_presentes(client, driver_falso):
    """PATCH /lotes/{codigo} devuelve 200 y envía solo los campos recibidos."""
    driver_falso.execute_query.return_value = resultado({"l": {**LOTE, "estado": "RETIRADO"}})
    response = client.patch("/lotes/MP-900", json={"estado": "RETIRADO"})
    assert response.status_code == 200
    assert response.json()["estado"] == "RETIRADO"
    params = driver_falso.execute_query.call_args.args[1]
    assert params["cambios"] == {"estado": "RETIRADO"}


def test_patch_vacio_422(client, driver_falso):
    """PATCH /lotes/{codigo} devuelve 422 si el cuerpo no trae ningún campo."""
    response = client.patch("/lotes/MP-900", json={})
    assert response.status_code == 422
    driver_falso.execute_query.assert_not_called()



def test_patch_inexistente_404(client, driver_falso):
    """PATCH devuelve 404 cuando el lote no existe."""
    driver_falso.execute_query.return_value = resultado()
    response = client.patch(
        "/lotes/NO-EXISTE",
        json={"estado": "ACTIVO"},
    )
    assert response.status_code == 404

# ------- DELETE
def test_delete_sin_relaciones_204(client, driver_falso):
    """DELETE /lotes/{codigo} devuelve 204 si el lote no tiene relaciones."""
    driver_falso.execute_query.side_effect = [
        resultado({"l": LOTE, "relaciones": 0}),
        resultado(),
    ]
    response = client.delete("/lotes/MP-900")
    assert response.status_code == 204
    assert response.content == b""
    assert driver_falso.execute_query.call_count == 2


def test_delete_con_relaciones_409_y_no_borra(client, driver_falso):
    """DELETE /lotes/{codigo} devuelve 409 y no borra si hay relaciones."""
    driver_falso.execute_query.return_value = resultado({"l": LOTE, "relaciones": 3})
    response = client.delete("/lotes/MP-900")
    assert response.status_code == 409
    assert "forzar=true" in response.json()["detail"]
    assert driver_falso.execute_query.call_count == 1  # solo la consulta, sin DELETE


def test_delete_con_relaciones_y_forzar_204(client, driver_falso):
    """DELETE /lotes/{codigo}?forzar=true borra el lote junto con sus relaciones."""
    driver_falso.execute_query.side_effect = [
        resultado({"l": LOTE, "relaciones": 3}),
        resultado(),
    ]
    response = client.delete("/lotes/MP-900?forzar=true")
    assert response.status_code == 204
    assert driver_falso.execute_query.call_count == 2


def test_delete_inexistente_404(client, driver_falso):
    """DELETE /lotes/{codigo} devuelve 404 si el lote no existe."""
    driver_falso.execute_query.return_value = resultado()
    response = client.delete("/lotes/NO-EXISTE")
    assert response.status_code == 404


def test_delete_sin_neo4j_503(client, driver_falso):
    """DELETE /lotes/{codigo} devuelve 503 si Neo4j no está disponible."""
    driver_falso.execute_query.side_effect = ServiceUnavailable("caído")
    response = client.delete("/lotes/MP-900")
    assert response.status_code == 503


# ------HEALTH
def test_health_ok(client, driver_falso):
    """GET /health devuelve 200 cuando Neo4j responde."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["neo4j"] == "conectado"


def test_health_sin_neo4j_503(client, driver_falso):
    """GET /health devuelve 503 si Neo4j no responde."""
    driver_falso.verify_connectivity.side_effect = ServiceUnavailable("caído")
    response = client.get("/health")
    assert response.status_code == 503
