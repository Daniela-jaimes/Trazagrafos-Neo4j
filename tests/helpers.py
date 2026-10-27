def resultado(*filas):
    """Imita la tupla (records, summary, keys) que devuelve driver.execute_query."""
    return (list(filas), None, None)


LOTE = {
    "codigo": "MP-900",
    "tipo": "MATERIA_PRIMA",
    "producto": "Leche",
    "cantidad_kg": 50.0,
    "estado": "ACTIVO",
}
