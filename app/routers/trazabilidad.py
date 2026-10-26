from typing import Any

from fastapi import APIRouter, HTTPException
from neo4j.exceptions import AuthError, ServiceUnavailable

from app.db import driver


router = APIRouter(prefix="/trazabilidad", tags=["trazabilidad"])


def _execute_trace(query: str, parameters: dict[str, str]) -> list[Any]:
    try:
        records, _, _ = driver.execute_query(
            query, parameters, database_="neo4j"
        )
    except (AuthError, ServiceUnavailable) as exc:
        raise HTTPException(status_code=503, detail="Neo4j no disponible") from exc
    return records


@router.get("/lotes/{codigo}/origen")
def trazar_origen(codigo: str):
    query = """
    MATCH (final:Lote {codigo: $codigo})
    OPTIONAL MATCH path=(productor:Productor)-[:PRODUCE]->(origen:Lote)
                   -[:INSUMO_DE*0..]->(final)
    WITH final, collect(DISTINCT CASE
        WHEN productor IS NULL THEN null
        ELSE {
            productor: properties(productor),
            lote_origen: properties(origen),
            ruta: [n IN nodes(path) | coalesce(n.codigo, n.id)]
        }
    END) AS origenes
    RETURN properties(final) AS lote, origenes
    """
    records = _execute_trace(query, {"codigo": codigo})
    if not records:
        raise HTTPException(status_code=404, detail=f"Lote '{codigo}' no encontrado")
    return {"lote": records[0]["lote"], "origenes": records[0]["origenes"]}


@router.get("/lotes/{codigo}/destino")
def trazar_destino(codigo: str):
    query = """
    MATCH (origen:Lote {codigo: $codigo})
    OPTIONAL MATCH path=(origen)-[:INSUMO_DE*0..]->(enviado:Lote)
                   -[envio:ENVIADO_A]->(punto:PuntoVenta)
    WITH origen, collect(DISTINCT CASE
        WHEN envio IS NULL THEN null
        ELSE {
            lote_enviado: properties(enviado),
            punto_venta: properties(punto),
            envio: properties(envio),
            ruta: [n IN nodes(path) | coalesce(n.codigo, n.id)]
        }
    END) AS destinos
    RETURN properties(origen) AS lote, destinos
    """
    records = _execute_trace(query, {"codigo": codigo})
    if not records:
        raise HTTPException(status_code=404, detail=f"Lote '{codigo}' no encontrado")
    return {"lote": records[0]["lote"], "destinos": records[0]["destinos"]}


@router.get("/incidentes/{incidente_id}")
def trazar_incidente(incidente_id: str):
    query = """
    MATCH (incidente:Incidente {id: $incidente_id})
    OPTIONAL MATCH (incidente)-[:AFECTA]->(afectado:Lote)
    OPTIONAL MATCH path=(afectado)-[:INSUMO_DE*0..]->(enviado:Lote)
                   -[envio:ENVIADO_A]->(punto:PuntoVenta)
    WITH incidente, collect(DISTINCT CASE
        WHEN afectado IS NULL THEN null
        ELSE {
            lote_afectado: properties(afectado),
            lote_enviado: properties(enviado),
            punto_venta: properties(punto),
            envio: properties(envio),
            ruta: [n IN nodes(path) | coalesce(n.codigo, n.id)]
        }
    END) AS destinos
    RETURN properties(incidente) AS incidente, destinos
    """
    records = _execute_trace(query, {"incidente_id": incidente_id})
    if not records:
        raise HTTPException(
            status_code=404,
            detail=f"Incidente '{incidente_id}' no encontrado",
        )
    return {
        "incidente": records[0]["incidente"],
        "destinos": records[0]["destinos"],
    }
