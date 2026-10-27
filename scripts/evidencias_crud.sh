#!/usr/bin/env bash
# Ejecuta cada endpoint del CRUD y guarda el resultado como evidencia.
# Uso:  docker compose up -d   &&   bash scripts/evidencias_crud.sh
set -u
BASE="${BASE:-http://localhost:8000}"
OUT_DIR="docs/evidencias/crud"
mkdir -p "$OUT_DIR"
LOG="$OUT_DIR/evidencias_$(date +%Y%m%d-%H%M%S).log"
exec > >(tee "$LOG") 2>&1

LOTE="EVID-$(date +%s)"
echo "Evidencias CRUD  -  $(date '+%Y-%m-%d %H:%M:%S')  -  $BASE"

req() { # titulo metodo ruta [json]
  local titulo="$1" metodo="$2" ruta="$3" cuerpo="${4:-}"
  echo; echo "### $titulo"
  if [ -n "$cuerpo" ]; then
    echo "\$ curl -X $metodo $BASE$ruta -d '$cuerpo'"
    curl -s -w '\nHTTP %{http_code}\n' -X "$metodo" "$BASE$ruta" \
      -H 'Content-Type: application/json' -d "$cuerpo"
  else
    echo "\$ curl -X $metodo $BASE$ruta"
    curl -s -w '\nHTTP %{http_code}\n' -X "$metodo" "$BASE$ruta"
  fi
}

req "0. Salud de la API y de Neo4j (200)"            GET    /health
req "1. Crear lote (201)"                            POST   /lotes \
    "{\"codigo\":\"$LOTE\",\"tipo\":\"MATERIA_PRIMA\",\"producto\":\"Leche\",\"cantidad_kg\":50}"
req "2. Crear lote duplicado (409)"                  POST   /lotes \
    "{\"codigo\":\"$LOTE\",\"tipo\":\"MATERIA_PRIMA\",\"producto\":\"Leche\",\"cantidad_kg\":50}"
req "3. Crear lote con datos inválidos (422)"        POST   /lotes \
    "{\"codigo\":\"$LOTE-X\",\"tipo\":\"OTRO\",\"producto\":\"Leche\",\"cantidad_kg\":-1}"
req "4. Listar lotes (200)"                          GET    "/lotes?limit=5"
req "5. Listar con filtro por tipo (200)"            GET    "/lotes?tipo=PRODUCTO"
req "6. Obtener lote (200)"                          GET    "/lotes/$LOTE"
req "7. Obtener lote inexistente (404)"              GET    /lotes/NO-EXISTE
req "8. Reemplazar lote con PUT (200)"               PUT    "/lotes/$LOTE" \
    '{"tipo":"PRODUCTO","producto":"Queso","cantidad_kg":12.5,"estado":"ACTIVO"}'
req "9. Actualizar parcialmente con PATCH (200)"     PATCH  "/lotes/$LOTE" '{"estado":"RETIRADO"}'
req "10. PATCH sin campos (422)"                     PATCH  "/lotes/$LOTE" '{}'
req "11. PUT sobre lote inexistente (404)"           PUT    /lotes/NO-EXISTE \
    '{"tipo":"PRODUCTO","producto":"Queso","cantidad_kg":1}'
req "12. Borrar lote con relaciones, sin forzar (409)" DELETE /lotes/MP-001
req "13. Borrar lote propio sin relaciones (204)"    DELETE "/lotes/$LOTE"
req "14. Confirmar que ya no existe (404)"           GET    "/lotes/$LOTE"

echo; echo "Log guardado en: $LOG"
echo "Caso 503: ver README (docker compose stop neo4j  ->  GET /health)."
