# Trazagrafo Neo4j

Proyecto académico para el modelado y analisis de trazabilidad de lotes de alimentos mediante una base de datos orientada a grafos(**Neo4j**)

## Objetivo

Desarrollar una solución eficiente para registrar y consultar la cadena de suministros de alimentos, permitiendo responder de manera agil a preguntas criticas como: ** ¿A que puntos de venta llego un lote contaminado?** o **¿De que productos proviene un producto final?*

## 🏗️ Modelo del Grafo

### Nodos
- **Productor**: Fincas o proveedores de materias primas.
- **Lote**: Lotes de materia prima, ingredientes intermedios o productos terminados.
- **Instalacion**: Plantas de procesamiento, centros de acopio o bodegas compartidas.
- **PuntoVenta**: Tiendas, supermercados o distribuidores finales.
- **Incidente**: Alertas de contaminación o fallas sanitarias.

### Relaciones principales
- `(:Productor)-[:PRODUCE]->(:Lote)`
- `(:Lote)-[:INSUMO_DE]->(:Lote)`
- `(:Lote)-[:PROCESADO_EN]->(:Instalacion)`
- `(:Lote)-[:ENVIADO_A]->(:PuntoVenta)`
- `(:Incidente)-[:AFECTA]->(:Lote)`

## Consultas Clave (Cypher)
- Trazabilidad hacia adelante (impacto de un lote de materia prima).
- Trazabilidad hacia atrás (origen de un producto final).
- Detección de contaminación cruzada por instalaciones compartidas.
- Identificación de productores más críticos en la red.

## Tecnologías

- **Python** (Lógica de la API y scripts de carga)
- **Neo4j** (Base de datos de grafos)
- **Docker Compose** (Orquestación de contenedores)

## Estructura del proyecto

```text
trazagrafo-neo4j/
├── app/                 # Código de la API
├── scripts/             # Carga inicial de datos y consultas Cypher
├── docs/                # Documentación, diagramas y evidencias
├── docker-compose.yml   # Configuración de servicios
├── .env.example         # Ejemplo de variables de entorno
├── .gitignore           # Archivos excluidos de Git
└── README.md            # Documentación principal
```

## Configuración

Las instrucciones para instalar, configurar y ejecutar el proyecto se agregarán conforme avance el desarrollo.

## Estado del proyecto

En preparación: estructura inicial y configuración del entorno.