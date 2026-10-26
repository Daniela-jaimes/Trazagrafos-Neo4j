# Trazagrafo Neo4j

API de trazabilidad agroindustrial que modela productores, lotes, instalaciones,
puntos de venta e incidentes en Neo4j.

## Inicio rápido

1. Copia `.env.example` a `.env` y define `NEO4J_PASSWORD`.
2. Ejecuta `docker compose up --build`.
3. Abre la documentación interactiva en `http://localhost:8000/docs`.

Docker Compose inicia Neo4j, carga el dataset de demostración desde
[`scripts/seed.cypher`](scripts/seed.cypher) y, después, inicia la API.

## Endpoints de trazabilidad

| Método y ruta | Uso |
| --- | --- |
| `GET /trazabilidad/lotes/{codigo}/origen` | Orígenes y productores que contribuyen a un lote |
| `GET /trazabilidad/lotes/{codigo}/destino` | Lotes derivados, envíos y puntos de venta |
| `GET /trazabilidad/incidentes/{incidente_id}` | Lotes afectados y destinos conocidos de un incidente |

Las respuestas incluyen los datos del lote/incidente y una lista de rutas,
envíos o destinos. Un identificador inexistente devuelve `404`; si Neo4j no
está disponible, la API devuelve `503`.

## Seed y pruebas

El seed es idempotente y crea 4 productores, 10 lotes, 6 instalaciones,
6 puntos de venta, 2 incidentes y 10 envíos. Para ejecutar las pruebas unitarias:

```powershell
python -m unittest discover -s tests
```

Las pruebas de integración aplican el seed y verifican las trazas reales. Para
ejecutarlas, configura `NEO4J_TEST_URI`, `NEO4J_TEST_USER` y
`NEO4J_TEST_PASSWORD` para una instancia Neo4j **dedicada a pruebas** antes de
ejecutar el mismo comando. No apuntes estas pruebas a una base con datos que
debas conservar.

## Documentación

Consulta [docs/README.md](docs/README.md) para la arquitectura, el modelo del
grafo y su comparación con un modelo relacional.