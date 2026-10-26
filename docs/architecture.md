# Arquitectura y modelos de datos

## Arquitectura de ejecución

```mermaid
flowchart LR
    Client[Cliente REST / navegador]
    API[FastAPI<br/>app.main]
    Trace[Router de trazabilidad<br/>app.routers.trazabilidad]
    Neo4j[(Neo4j 5<br/>grafo de trazabilidad)]
    Seed[Seed idempotente<br/>scripts/seed.cypher]

    Client -->|HTTP JSON| API
    API --> Trace
    Trace -->|Cypher con parámetros| Neo4j
    Seed -->|cypher-shell al iniciar| Neo4j
```

Docker Compose levanta Neo4j, ejecuta el seed después del healthcheck y luego
inicia la API. Las rutas de consulta usan el driver oficial de Neo4j; las
etiquetas y tipos de relación del grafo se detallan abajo.

## Modelo del grafo

```mermaid
flowchart LR
    Producer[Productor<br/>id, nombre, municipio]
    Raw[Lote materia prima<br/>codigo, producto, cantidad, estado]
    Product[Lote producto<br/>codigo, producto, cantidad, estado]
    Facility[Instalacion<br/>id, tipo, municipio]
    Store[PuntoVenta<br/>id, nombre, municipio]
    Incident[Incidente<br/>id, tipo, estado, fecha]

    Producer -->|PRODUCE| Raw
    Raw -->|INSUMO_DE<br/>cantidad_kg| Product
    Product -->|INSUMO_DE<br/>cantidad_kg| Product
    Raw -->|PROCESADO_EN<br/>fecha| Facility
    Product -->|PROCESADO_EN<br/>fecha| Facility
    Product -->|ENVIADO_A<br/>id, fecha, cantidad_kg| Store
    Incident -->|AFECTA| Raw
    Incident -->|AFECTA| Product
```

`INSUMO_DE` apunta del lote de origen al lote que lo incorpora; por eso la
traza hacia atrás recorre las relaciones en sentido inverso y la traza hacia
adelante las recorre en sentido de la flecha. Cada envío tiene un identificador
en la relación `ENVIADO_A`, lo cual permite guardar varias entregas del mismo
lote al mismo punto de venta.

## Comparación con un modelo relacional

```mermaid
erDiagram
    PRODUCTOR ||--o{ LOTE_PRODUCIDO : produce
    LOTE ||--o{ LOTE_INSUMO : origen
    LOTE ||--o{ LOTE_INSUMO : resultado
    LOTE ||--o{ PROCESAMIENTO : procesado
    INSTALACION ||--o{ PROCESAMIENTO : realiza
    LOTE ||--o{ ENVIO : despachado
    PUNTO_VENTA ||--o{ ENVIO : recibe
    INCIDENTE ||--o{ INCIDENTE_LOTE : afecta
    LOTE ||--o{ INCIDENTE_LOTE : afectado

    PRODUCTOR {
        string id PK
        string nombre
        string municipio
    }
    LOTE {
        string codigo PK
        string tipo
        string producto
        float cantidad_kg
        string estado
    }
    LOTE_PRODUCIDO {
        string productor_id FK
        string lote_codigo FK
    }
    LOTE_INSUMO {
        string lote_origen FK
        string lote_resultado FK
        float cantidad_kg
    }
    INSTALACION {
        string id PK
        string nombre
        string tipo
        string municipio
    }
    PROCESAMIENTO {
        string lote_codigo FK
        string instalacion_id FK
        date fecha
    }
    PUNTO_VENTA {
        string id PK
        string nombre
        string municipio
    }
    ENVIO {
        string id PK
        string lote_codigo FK
        string punto_venta_id FK
        date fecha
        float cantidad_kg
    }
    INCIDENTE {
        string id PK
        string tipo
        string estado
        date fecha
    }
    INCIDENTE_LOTE {
        string incidente_id FK
        string lote_codigo FK
    }
```

| Aspecto | Grafo Neo4j | Relacional |
| --- | --- | --- |
| Relaciones | `PRODUCE`, `INSUMO_DE`, `PROCESADO_EN`, `ENVIADO_A` y `AFECTA` son relaciones explícitas con propiedades cuando corresponde. | Las relaciones se representan mediante claves foráneas y tablas de unión (`LOTE_INSUMO`, `ENVIO`, etc.). |
| Trazabilidad de varios niveles | Recorrido variable como `[:INSUMO_DE*0..]` y acceso directo a vecinos. | Requiere CTE recursivo o consultas recursivas con uniones repetidas. |
| Integridad e identidad | Restricciones únicas para identificadores de nodos; identidad propia para cada relación de envío. | PK/FK, restricciones `UNIQUE` y tablas de unión proporcionan integridad referencial. |
| Consulta por relaciones | Natural para rutas, impacto de incidentes y propagación entre lotes. | Adecuado para registros tabulares y agregaciones; los caminos recursivos requieren lógica adicional. |
| Coste principal | Las consultas de recorrido dependen del tamaño y ramificación de las rutas. | Los recorridos de profundidad variable dependen de uniones recursivas y sus índices. |

El esquema relacional del diagrama es una traducción conceptual equivalente,
no una segunda base de datos implementada en este proyecto.
