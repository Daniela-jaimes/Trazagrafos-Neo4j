from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response

from app.db import get_driver
from app.schemas import  LoteOut,LoteReplace,LotePatch
from app.routers._comunes import _lote_o_404
router = APIRouter(prefix="/lotes", tags=["Lotes"])

DB = "neo4j"
@router.put("/{codigo}", response_model=LoteOut, summary="Reemplazar lote")
def reemplazar_lote(codigo: str, datos: LoteReplace, drv=Depends(get_driver)):
    """Reemplaza los datos de un lote existente 
    Args:
    codigo: Codigo unico del lote que se desea reemplazar
    datos: Datos completos que reemplazara todo el lote existente
    drv: Driver de Neo4j, inyectado por FastAPI mediante get_driver
    Returns: 
    Un diccionario con las propiedades del lote actualizado
    Raises:
    HTTPException: Error 404 si no existe un lote con el codigo indicado
    """
    query = """
    MATCH (l:Lote {codigo: $codigo})
    SET l.tipo = $tipo, l.producto = $producto,
        l.cantidad_kg = $cantidad_kg, l.estado = $estado
    RETURN l
    """
    params = {"codigo": codigo, **datos.model_dump()}
    records, _, _ = drv.execute_query(query, params, database_=DB)
    return _lote_o_404(records, codigo)


@router.patch("/{codigo}", response_model=LoteOut, summary="Actualizar parcialmente")
def actualizar_lote(codigo: str, datos: LotePatch, drv=Depends(get_driver)):
    """Actualiza los datos de un lote existente 
    Args:
    codigo: Codigo unico del lote que se desea actualizar
    datos: Campos que se desean modificar en el lote 
    drv: Driver de Neo4j, inyectado por FastAPI mediante get_driver
    Returns: 
    Un diccionario con las propiedades actualizadas del lote
    Raises:
    HTTPException: Error 404 si no existe un lote con el codigo indicado
    """
    cambios = datos.model_dump(exclude_none=True)
    records, _, _ = drv.execute_query(
        "MATCH (l:Lote {codigo: $codigo}) SET l += $cambios RETURN l",
        {"codigo": codigo, "cambios": cambios},
        database_=DB,
    )
    return _lote_o_404(records, codigo)


@router.delete("/{codigo}", status_code=204, summary="Eliminar lote")
def eliminar_lote(
    codigo: str,
    forzar: bool = Query(
        False, description="Si es true, borra también las relaciones del lote"
    ),
    drv=Depends(get_driver),
):
    """Elimina un lote y opcional sus relaciones de trazabilidad
    Args:
    codigo: Codigo unico del lote que se desea elliminar 
    forzar: Indica si se deben eliminar tambien las relaciones del lote 
    drv: Driver de Neo4j, inyectado por FastAPI mediante get_driver
    Returns: 
    Una respuesta HTTP 204 sin contenido si la eliminación es exitosa.
    Raises:
    HTTPException: Error 404 si el lote no existe y 
    Error 409 si el lote tiene relaciones y forzar es False.
    """
    records, _, _ = drv.execute_query(
        """
        MATCH (l:Lote {codigo: $codigo})
        OPTIONAL MATCH (l)-[r]-()
        RETURN l, count(r) AS relaciones
        """,
        {"codigo": codigo},
        database_=DB,
    )
    if not records:
        raise HTTPException(status_code=404, detail=f"Lote '{codigo}' no encontrado")

    relaciones = records[0]["relaciones"]
    if relaciones and not forzar:
        raise HTTPException(
            status_code=409,
            detail=(
                f"El lote '{codigo}' tiene {relaciones} relación(es) en la cadena de "
                "trazabilidad. Use ?forzar=true para eliminarlo junto con ellas."
            ),
        )

    drv.execute_query(
        "MATCH (l:Lote {codigo: $codigo}) DETACH DELETE l",
        {"codigo": codigo},
        database_=DB,
    )
    return Response(status_code=204)
