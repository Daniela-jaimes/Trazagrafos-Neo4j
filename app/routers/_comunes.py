from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response

router = APIRouter(prefix="/lotes", tags=["Lotes"])

DB = "neo4j"


def _lote_o_404(records, codigo: str) -> dict:
    """Convierte el resultado de Neo4j en un lote o lanza 404.

    Args:
        records: Filas devueltas por ``execute_query``.
        codigo: Código buscado, usado en el mensaje de error.

    Returns:
        El lote como diccionario.

    Raises:
        HTTPException: 404 si ``records`` está vacío.
    """
    if not records:
        raise HTTPException(status_code=404, detail=f"Lote '{codigo}' no encontrado")
    return dict(records[0]["l"])