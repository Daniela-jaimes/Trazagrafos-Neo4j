from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from neo4j.exceptions import ConstraintError

from app.db import get_driver
from app.schemas import LoteCreate, LoteOut, TipoLote, EstadoLote
from app.routers._comunes import _lote_o_404
router = APIRouter(prefix="/lotes", tags=["Lotes"])

DB = "neo4j"



@router.post("", status_code=201, response_model=LoteOut, summary="Crear lote")
def crear_lote(lote: LoteCreate, drv=Depends(get_driver)):
    """Crea un lote nuevo en la base de datos.
    Args:
        lote: Datos del lote a crear (código, tipo, producto, cantidad y estado).
        drv: Driver de Neo4j, inyectado por FastAPI mediante get_driver.
    Returns:
        Un diccionario con las propiedades del lote recién creado.
    Raises:
        HTTPException: Error 409 si ya existe un lote con ese código.
    """
    query = """
    CREATE (l:Lote {
        codigo: $codigo, tipo: $tipo, producto: $producto,
        cantidad_kg: $cantidad_kg, estado: $estado
    })
    RETURN l
    """
    try:
        records, _, _ = drv.execute_query(
            query,
            lote.model_dump(),
            database_=DB
        )
    except ConstraintError:
        raise HTTPException(
            status_code=409,
            detail=f"Ya existe un lote con código '{lote.codigo}'"
        )

    return dict(records[0]["l"])


@router.get("", response_model=list[LoteOut], summary="Listar lotes")
def listar_lotes(
    tipo: Optional[TipoLote] = None,
    estado: Optional[EstadoLote] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    drv=Depends(get_driver),
):
    """Lista los lotes registrados, con filtros opcionales y paginacion
    Args: 
    tipo: Filtro opcional por tipo de lote 
    estado: Filtro opcional por estado del lote
    skip: Cantidad de registros dque se omiten desde el inicio. por defecto, 0
    limit: Numero maximo de lotes por pagina. por defecto 50, maximo, 200
    drv: Driver de Neo4j, inyectado por FastAPI mediante get_driver
    Returns: 
    Una lista de diccionarios con las propiedades de los lotes encontrado. 
    Si no hay coincidencias, devuelve una lista vacia
    """
    query = """
    MATCH (l:Lote)
    WHERE ($tipo IS NULL OR l.tipo = $tipo)
      AND ($estado IS NULL OR l.estado = $estado)
    RETURN l
    ORDER BY l.codigo
    SKIP $skip LIMIT $limit
    """
    params = {"tipo": tipo, "estado": estado, "skip": skip, "limit": limit}
    records, _, _ = drv.execute_query(query, params, database_=DB)
    return [dict(r["l"]) for r in records]


@router.get("/{codigo}", response_model=LoteOut, summary="Obtener lote")
def obtener_lote(codigo: str, drv=Depends(get_driver)):
    """Obtiene un lote por su código.
    Args:
        codigo: Código único del lote que se desea consultar.
        drv: Driver de Neo4j, inyectado por FastAPI mediante get_driver.
    Returns:
        Un diccionario con las propiedades del lote encontrado.
    Raises:
        HTTPException: Error 404 si no existe un lote con el código indicado.
    """
    records, _, _ = drv.execute_query(
        "MATCH (l:Lote {codigo: $codigo}) RETURN l", {"codigo": codigo}, database_=DB
    )
    return _lote_o_404(records, codigo)
