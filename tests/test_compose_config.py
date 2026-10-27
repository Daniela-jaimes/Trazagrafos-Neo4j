"""Valida que docker-compose.yml y .env.example sean coherentes con el repo."""
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parent.parent
VARIABLES_REQUERIDAS = {"NEO4J_URI", "NEO4J_USER", "NEO4J_PASSWORD"}


def _cargar_compose() -> dict:
    """Carga y devuelve el contenido de docker-compose.yml.

    Returns:
        Diccionario con la definición de servicios del compose.
    """
    with open(RAIZ / "docker-compose.yml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def test_api_build_apunta_a_raiz_con_dockerfile():
    """El build de la API debe usar un contexto que contenga el Dockerfile."""
    contexto = _cargar_compose()["services"]["api"]["build"]
    assert (RAIZ / contexto / "Dockerfile").is_file()


def test_seed_montado_existe():
    """El archivo seed montado en neo4j-seed debe existir en el repositorio."""
    volumenes = _cargar_compose()["services"]["neo4j-seed"]["volumes"]
    origen = volumenes[0].split(":")[0]
    assert (RAIZ / origen).is_file()


def test_env_example_define_variables_requeridas():
    """.env.example debe declarar todas las variables que usa la aplicación."""
    lineas = (RAIZ / ".env.example").read_text(encoding="utf-8").splitlines()
    claves = {l.split("=")[0].strip() for l in lineas if "=" in l}
    assert VARIABLES_REQUERIDAS <= claves
