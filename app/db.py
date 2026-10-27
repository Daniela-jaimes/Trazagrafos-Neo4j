import logging
import os

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

logger = logging.getLogger("trazagrafo.db")

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def get_driver():
    """Dependencia de FastAPI. Los tests la sustituyen por un driver falso."""
    return driver


def asegurar_restricciones(drv=None):
    """Garantiza la unicidad de Lote.codigo, de la que depende el 409 del POST.

    Usa el mismo nombre que scripts/seed.cypher, así que es idempotente.
    """
    (drv or driver).execute_query(
        "CREATE CONSTRAINT lote_codigo IF NOT EXISTS "
        "FOR (l:Lote) REQUIRE l.codigo IS UNIQUE",
        database_="neo4j",
    )


def cerrar_driver():
    driver.close()
