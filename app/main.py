import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from neo4j.exceptions import AuthError, ServiceUnavailable

from app.db import asegurar_restricciones, cerrar_driver, get_driver
from app.routers import lotes_consulta, lotes_escritura, trazabilidad

logger = logging.getLogger("trazagrafo.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestiona el ciclo de vida de la aplicación.

    Al arrancar intenta crear la restricción de unicidad de ``Lote.codigo``.
    Si Neo4j aún no responde, registra una advertencia y la API sigue
    levantando (``/health`` reportará el estado real).

    Args:
        app: Instancia de FastAPI que se está iniciando.

    Yields:
        None: Cede el control mientras la aplicación atiende solicitudes.
    """
    try:
        asegurar_restricciones()
    except (ServiceUnavailable, AuthError, OSError) as exc:
        logger.warning("No se pudo asegurar las restricciones: %s", exc)
    yield
    cerrar_driver()


app = FastAPI(title="TrazaGrafo API", version="0.1.0", lifespan=lifespan)

app.include_router(lotes_consulta.router)
app.include_router(lotes_escritura.router)
app.include_router(trazabilidad.router)


@app.get("/health")
def health(drv=Depends(get_driver)):
    """Comprueba la disponibilidad de Neo4j.

    Args:
        drv: Driver de Neo4j, inyectado por FastAPI mediante get_driver.

    Returns:
        Un diccionario con el estado de la API y la conexión con Neo4j.

    Raises:
        HTTPException: Error 503 si Neo4j no está disponible.
    """
    try:
        drv.verify_connectivity()
        return {"status": "ok", "neo4j": "conectado"}
    except (ServiceUnavailable, AuthError, OSError) as e:
        raise HTTPException(
            status_code=503,
            detail=f"Neo4j no disponible: {e}",
        )


@app.exception_handler(ServiceUnavailable)
async def neo4j_no_disponible(request: Request, exc: ServiceUnavailable):
    """Gestiona los errores de disponibilidad de Neo4j.

    Args:
        request: Solicitud HTTP que produjo el error.
        exc: Excepción de disponibilidad generada por Neo4j.

    Returns:
        JSONResponse con el código HTTP 503.
    """
    return JSONResponse(
        status_code=503,
        content={"detail": "Neo4j no disponible"},
    )
