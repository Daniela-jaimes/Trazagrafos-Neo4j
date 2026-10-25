from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from neo4j.exceptions import ConstraintError, ServiceUnavailable, AuthError

from app.db import driver, cerrar_driver
from app.schemas import LoteCreate


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    cerrar_driver()


app = FastAPI(title="TrazaGrafo API", version="0.1.0", lifespan=lifespan)


@app.get("/health")
def health():
    try:
        driver.verify_connectivity()
        return {"status": "ok", "neo4j": "conectado"}
    except (ServiceUnavailable, AuthError, OSError) as e:
        raise HTTPException(status_code=503, detail=f"Neo4j no disponible: {e}")


@app.post("/lotes", status_code=201)
def crear_lote(lote: LoteCreate):
    query = """
    CREATE (l:Lote {
        codigo: $codigo, tipo: $tipo, producto: $producto,
        cantidad_kg: $cantidad_kg, estado: $estado
    })
    RETURN l
    """
    try:
        records, _, _ = driver.execute_query(
            query, lote.model_dump(), database_="neo4j"
        )
        return dict(records[0]["l"])
    except ConstraintError:
        raise HTTPException(status_code=409, detail=f"Ya existe un lote con código '{lote.codigo}'")
    except ServiceUnavailable:
        raise HTTPException(status_code=503, detail="Neo4j no disponible")


@app.get("/lotes/{codigo}")
def obtener_lote(codigo: str):
    query = "MATCH (l:Lote {codigo: $codigo}) RETURN l"
    try:
        records, _, _ = driver.execute_query(query, {"codigo": codigo}, database_="neo4j")
    except ServiceUnavailable:
        raise HTTPException(status_code=503, detail="Neo4j no disponible")
    if not records:
        raise HTTPException(status_code=404, detail=f"Lote '{codigo}' no encontrado")
    return dict(records[0]["l"])