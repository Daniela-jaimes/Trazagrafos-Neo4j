# Reparto de trabajo

Proyecto: Trazagrafo (Neo4j). Sustentación: **30 de octubre de 2026** (20 min).

| Persona | Rol | Rama |
|---|---|---|
| **Daniela** | A: API y CRUD | `feat/crud-lotes` |
| **Rubén** | B: Grafo y datos | `feat/trazabilidad` |

## Paso 0 (común, antes de dividirse)

1. Commit inicial, repositorio en GitHub y colaborador agregado (Git).
2. Refactor de `db.py` y `main.py` en routers, para no editar los mismos archivos.

## Responsabilidades

| Área | Daniela (A) | Rubén (B) |
|---|---|---|
| Código | CRUD completo en `app/routers/lotes.py` | Trazabilidad en `app/routers/trazabilidad.py` |
| Datos | n/a | Seed completo con datos de demo (`scripts/seed.cypher`) |
| Tests | CRUD: casos 404, 409 y 503 | Trazabilidad y seed |
| Docker | Dockerfile: usuario no root y healthcheck | Verificar `docker compose up` desde cero |
| Docs | README: instalación, uso y ejemplos `curl` | Diagrama de arquitectura y modelo del grafo vs relacional |
| Evidencias | Capturas y logs de los endpoints CRUD | Capturas de Neo4j Browser y consultas Cypher |

## Reglas de Git

- Nadie hace commit directo a `main`; se integra por Pull Request revisado por la otra persona.
- Conventional commits (`feat:`, `fix:`, `test:`, `docs:`, `chore:`).
- `git pull --rebase origin main` antes de empezar cada día.
- Cada funcionalidad nueva lleva test, y antes del PR se corre `pytest` completo.

## Calendario

| Fecha | Actividad |
|---|---|
| 23-24 oct | Paso 0 |
| 25-27 oct | Trabajo en paralelo (código y tests) |
| 28 oct | Docs, diagrama, evidencias y prueba de reproducibilidad desde cero |
| 29 oct | Ensayo con cronómetro |

## Sustentación

Ambas personas deben dominar todo el proyecto. Reparto sugerido de preguntas guía:

- **Rubén:** 1, 2 y 4 (problema, modelo de grafos vs relacional, escalabilidad).
- **Daniela:** 3 y 5 (arquitectura, implementación y dificultades) y la demo técnica.
