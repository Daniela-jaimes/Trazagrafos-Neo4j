# TrazaGrafo Neo4j

Proyecto académico para el modelado y análisis de trazabilidad de lotes de alimentos mediante una base de datos orientada a grafos (**Neo4j**), expuesta a través de una API REST con **FastAPI**.

## Objetivo

Registrar y consultar la cadena de suministro de alimentos para responder con agilidad preguntas críticas como **¿a qué puntos de venta llegó un lote contaminado?** o **¿de qué productores proviene un producto final?**

## Modelo del grafo

### Nodos
- **Productor**: fincas o proveedores de materias primas.
- **Lote**: materias primas, ingredientes intermedios o productos terminados.
- **Instalacion**: plantas de procesamiento, centros de acopio o bodegas.
- **PuntoVenta**: tiendas, supermercados o distribuidores finales.
- **Incidente**: alertas de contaminación o fallas sanitarias.

### Relaciones
- `(:Productor)-[:PRODUCE]->(:Lote)`
- `(:Lote)-[:INSUMO_DE]->(:Lote)`
- `(:Lote)-[:PROCESADO_EN]->(:Instalacion)`
- `(:Lote)-[:ENVIADO_A]->(:PuntoVenta)`
- `(:Incidente)-[:AFECTA]->(:Lote)`

### Consultas clave (Cypher)
- Trazabilidad hacia adelante: impacto de un lote de materia prima.
- Trazabilidad hacia atrás: origen de un producto final.
- Alcance de un incidente: lotes afectados y puntos de venta alcanzados.

El diagrama del modelo y su comparación con el modelo relacional están en [`docs/architecture.md`](docs/architecture.md).

## Tecnologías

- **Python 3.12** + **FastAPI** (API REST)
- **Neo4j 5 Community** (base de datos de grafos)
- **Docker Compose** (orquestación)
- **pytest** (pruebas)

## Requisitos

- Docker y Docker Compose v2 (`docker compose version`)
- Para ejecución local sin Docker: Python 3.12+

## Instalación y ejecución con Docker

```bash
git clone <URL-DEL-REPOSITORIO>
cd trazagrafo-neo4j
cp .env.example .env        # en Windows PowerShell: Copy-Item .env.example .env
# editar .env y definir NEO4J_PASSWORD (mínimo 8 caracteres)
docker compose up --build
```

Se levantan tres servicios, en este orden:

1. `neo4j`: la base de datos, con healthcheck.
2. `neo4j-seed`: carga restricciones y datos de ejemplo (`scripts/seed.cypher`) y termina.
3. `api`: arranca cuando Neo4j está sano y el seed terminó correctamente.

| Servicio | URL |
|---|---|
| Documentación interactiva (Swagger) | http://localhost:8000/docs |
| Estado de la API y de Neo4j | http://localhost:8000/health |
| Neo4j Browser | http://localhost:7474 (usuario `neo4j`, clave de `.env`) |

Para detener: `docker compose down`. Para borrar también los datos y empezar de cero: `docker compose down -v`.

### Variables de entorno

| Variable | Descripción | Valor por defecto |
|---|---|---|
| `NEO4J_PASSWORD` | Clave de Neo4j (la usa el compose y la API) | sin valor, es obligatoria |
| `NEO4J_USER` | Usuario de Neo4j | `neo4j` |
| `NEO4J_URI` | Solo para ejecutar la API fuera de Docker | `bolt://localhost:7687` |

## Ejecución local (sin Docker para la API)

```bash
docker compose up -d neo4j neo4j-seed     # solo la base de datos
python -m venv venv
source venv/bin/activate                  # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

## Endpoints del CRUD de lotes

| Método | Ruta | Descripción | Respuestas |
|---|---|---|---|
| POST | `/lotes` | Crear lote | 201, 409 (código repetido), 422 |
| GET | `/lotes` | Listar (filtros `tipo`, `estado`; `skip`, `limit`) | 200, 422 |
| GET | `/lotes/{codigo}` | Obtener un lote | 200, 404 |
| PUT | `/lotes/{codigo}` | Reemplazar todos los campos | 200, 404, 422 |
| PATCH | `/lotes/{codigo}` | Actualizar solo los campos enviados | 200, 404, 422 |
| DELETE | `/lotes/{codigo}` | Eliminar (con relaciones exige `?forzar=true`) | 204, 404, 409 |
| GET | `/health` | Estado de la API y de la conexión con Neo4j | 200, 503 |

Campos de un lote: `codigo` (único), `tipo` (`MATERIA_PRIMA` o `PRODUCTO`), `producto`, `cantidad_kg` (> 0) y `estado` (`ACTIVO`, `RETENIDO` o `RETIRADO`; por defecto `ACTIVO`).

### Ejemplos con curl

```bash
# Crear
curl -X POST http://localhost:8000/lotes -H 'Content-Type: application/json' \
  -d '{"codigo":"MP-100","tipo":"MATERIA_PRIMA","producto":"Leche","cantidad_kg":70}'

# Listar con filtro y paginación
curl "http://localhost:8000/lotes?tipo=MATERIA_PRIMA&limit=10"

# Obtener
curl http://localhost:8000/lotes/MP-100

# Reemplazar (PUT: todos los campos)
curl -X PUT http://localhost:8000/lotes/MP-100 -H 'Content-Type: application/json' \
  -d '{"tipo":"MATERIA_PRIMA","producto":"Leche entera","cantidad_kg":65,"estado":"ACTIVO"}'

# Actualizar parcialmente (PATCH)
curl -X PATCH http://localhost:8000/lotes/MP-100 -H 'Content-Type: application/json' \
  -d '{"estado":"RETIRADO"}'

# Eliminar
curl -X DELETE http://localhost:8000/lotes/MP-100

# Eliminar un lote con relaciones (borra también sus relaciones)
curl -X DELETE "http://localhost:8000/lotes/MP-001?forzar=true"
```

## Endpoints de trazabilidad

| Método y ruta | Uso | Respuestas |
|---|---|---|
| `GET /trazabilidad/lotes/{codigo}/origen` | Orígenes y productores que contribuyen a un lote | 200, 404, 503 |
| `GET /trazabilidad/lotes/{codigo}/destino` | Lotes derivados, envíos y puntos de venta | 200, 404, 503 |
| `GET /trazabilidad/incidentes/{incidente_id}` | Lotes afectados y destinos conocidos de un incidente | 200, 404, 503 |

```bash
curl http://localhost:8000/trazabilidad/lotes/PT-010/origen
curl http://localhost:8000/trazabilidad/lotes/MP-001/destino
curl http://localhost:8000/trazabilidad/incidentes/INC001
```

## Manejo de errores

| Código | Cuándo |
|---|---|
| 404 | El lote o el incidente no existe |
| 409 | Código duplicado en POST, o DELETE de un lote con relaciones sin `forzar` |
| 422 | Datos inválidos (tipo desconocido, cantidad ≤ 0, cuerpo vacío en PATCH, etc.) |
| 503 | Neo4j no disponible |

Para provocar un 503 en una demostración:

```bash
docker compose stop neo4j
curl -i http://localhost:8000/health        # 503
docker compose start neo4j
```

## Pruebas

```bash
pip install -r requirements-dev.txt
pytest                                      # pruebas unitarias (driver simulado, sin Neo4j)

# Pruebas de integración contra un Neo4j real
docker compose up -d neo4j neo4j-seed
NEO4J_INTEGRATION=1 NEO4J_PASSWORD=<clave> pytest -m integration

# Pruebas del seed y la trazabilidad (usar una base de datos de prueba dedicada)
NEO4J_TEST_URI=bolt://localhost:7687 NEO4J_TEST_PASSWORD=<clave> pytest tests/test_seed_traceability.py
```

## Evidencias de ejecución

Todo queda en `docs/evidencias/`:

| Ubicación | Contenido |
|---|---|
| `01_docker_compose_ps.txt` a `08_pytest_completo.txt` | Estado de los contenedores, seed, health, conteo del grafo, trazabilidad, caso sin Neo4j y suite completa de pytest |
| `crud/evidencias_crud.log` | Log de cada endpoint del CRUD |
| `capturas/` | Capturas de Swagger y de Neo4j Browser (cada archivo indica método, endpoint y código HTTP) |

Para regenerar el log del CRUD con el sistema levantado:

```bash
bash scripts/evidencias_crud.sh
```

## Estructura del proyecto

```text
trazagrafo-neo4j/
├── app/
│   ├── main.py                  # Aplicación, manejo global de errores, /health
│   ├── db.py                    # Conexión a Neo4j y restricciones
│   ├── schemas.py               # Modelos de entrada y salida (Pydantic)
│   └── routers/
│       ├── _comunes.py          # Utilidades compartidas (404 de lote)
│       ├── lotes_consulta.py    # POST, GET (listar y obtener)
│       ├── lotes_escritura.py   # PUT, PATCH, DELETE
│       └── trazabilidad.py      # Consultas de trazabilidad
├── scripts/
│   ├── seed.cypher              # Datos de ejemplo y restricciones
│   └── evidencias_crud.sh       # Genera el log de evidencias del CRUD
├── tests/                       # Pruebas con pytest
├── docs/                        # Arquitectura, reparto y evidencias
├── Dockerfile                   # Imagen de la API (usuario no root, healthcheck)
├── docker-compose.yml           # Neo4j + seed + API
├── .env.example                 # Plantilla de variables de entorno
└── README.md
```

## Documentación adicional

- Arquitectura, modelo del grafo y comparación con el modelo relacional: [`docs/architecture.md`](docs/architecture.md)

## Solución de problemas

- **El puerto 7474, 7687 u 8000 está ocupado**: apague el servicio que lo usa (por ejemplo, otro Neo4j) o cambie el puerto de la izquierda en `docker-compose.yml`.
- **Cambié `NEO4J_PASSWORD` y la API no conecta**: Neo4j guarda la clave en su volumen la primera vez. Ejecute `docker compose down -v` y vuelva a levantar.
- **La API aparece como `unhealthy`**: revise `docker compose logs api neo4j`; el healthcheck consulta `/health`, que falla si Neo4j no responde.