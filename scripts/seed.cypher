// Trazagrafo agroindustrial: dataset de demostración idempotente para Neo4j 5.
// Ejecutar desde Docker Compose o con cypher-shell contra una base de pruebas.

// Unicidad de identificadores de nodos.
CREATE CONSTRAINT lote_codigo IF NOT EXISTS
FOR (l:Lote) REQUIRE l.codigo IS UNIQUE;
CREATE CONSTRAINT productor_id IF NOT EXISTS
FOR (p:Productor) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT instalacion_id IF NOT EXISTS
FOR (i:Instalacion) REQUIRE i.id IS UNIQUE;
CREATE CONSTRAINT punto_venta_id IF NOT EXISTS
FOR (v:PuntoVenta) REQUIRE v.id IS UNIQUE;
CREATE CONSTRAINT incidente_id IF NOT EXISTS
FOR (i:Incidente) REQUIRE i.id IS UNIQUE;

// Productores y lotes de materia prima.
UNWIND [
    {id: 'P1', nombre: 'Finca La Esperanza', municipio: 'Pamplona'},
    {id: 'P2', nombre: 'Finca El Roble', municipio: 'Pamplonita'},
    {id: 'P3', nombre: 'Finca San Miguel', municipio: 'Cácota'},
    {id: 'P4', nombre: 'Finca La Pradera', municipio: 'Chitagá'}
] AS row
MERGE (p:Productor {id: row.id})
SET p.nombre = row.nombre, p.municipio = row.municipio;

UNWIND [
    {codigo: 'MP-001', tipo: 'MATERIA_PRIMA', producto: 'Leche', cantidad_kg: 80.0},
    {codigo: 'MP-002', tipo: 'MATERIA_PRIMA', producto: 'Leche', cantidad_kg: 60.0},
    {codigo: 'MP-003', tipo: 'MATERIA_PRIMA', producto: 'Leche', cantidad_kg: 55.0},
    {codigo: 'MP-004', tipo: 'MATERIA_PRIMA', producto: 'Fresa', cantidad_kg: 45.0},
    {codigo: 'MP-005', tipo: 'MATERIA_PRIMA', producto: 'Leche', cantidad_kg: 90.0},
    {codigo: 'PT-010', tipo: 'PRODUCTO', producto: 'Queso campesino', cantidad_kg: 40.0},
    {codigo: 'PT-011', tipo: 'PRODUCTO', producto: 'Yogur de fresa', cantidad_kg: 35.0},
    {codigo: 'PT-020', tipo: 'PRODUCTO', producto: 'Postre lácteo', cantidad_kg: 20.0},
    {codigo: 'PT-030', tipo: 'PRODUCTO', producto: 'Queso madurado', cantidad_kg: 26.0},
    {codigo: 'PT-040', tipo: 'PRODUCTO', producto: 'Mermelada de fresa', cantidad_kg: 30.0}
] AS row
MERGE (l:Lote {codigo: row.codigo})
SET l.tipo = row.tipo, l.producto = row.producto,
    l.cantidad_kg = row.cantidad_kg, l.estado = 'ACTIVO';

UNWIND [
    {productor: 'P1', lote: 'MP-001'},
    {productor: 'P2', lote: 'MP-002'},
    {productor: 'P3', lote: 'MP-003'},
    {productor: 'P4', lote: 'MP-004'},
    {productor: 'P1', lote: 'MP-005'}
] AS row
MATCH (p:Productor {id: row.productor})
MATCH (l:Lote {codigo: row.lote})
MERGE (p)-[:PRODUCE]->(l);

// Instalaciones y puntos de venta de la cadena.
UNWIND [
    {id: 'I1', nombre: 'Centro de Acopio Norte', tipo: 'CENTRO_ACOPIO', municipio: 'Pamplonita'},
    {id: 'I2', nombre: 'Planta Láctea Central', tipo: 'PLANTA', municipio: 'Pamplona'},
    {id: 'I3', nombre: 'Planta de Fermentados', tipo: 'PLANTA', municipio: 'Cúcuta'},
    {id: 'I4', nombre: 'Bodega Regional Pamplona', tipo: 'BODEGA', municipio: 'Pamplona'},
    {id: 'I5', nombre: 'Bodega Regional Cúcuta', tipo: 'BODEGA', municipio: 'Cúcuta'},
    {id: 'I6', nombre: 'Planta Frutícola', tipo: 'PLANTA', municipio: 'Chitagá'}
] AS row
MERGE (i:Instalacion {id: row.id})
SET i.nombre = row.nombre, i.tipo = row.tipo, i.municipio = row.municipio;

UNWIND [
    {id: 'V1', nombre: 'Tienda Centro', municipio: 'Pamplona'},
    {id: 'V2', nombre: 'Supermercado La Sabana', municipio: 'Pamplonita'},
    {id: 'V3', nombre: 'Mercado del Norte', municipio: 'Cúcuta'},
    {id: 'V4', nombre: 'Distribuidora El Puente', municipio: 'Chitagá'},
    {id: 'V5', nombre: 'Tienda La Frontera', municipio: 'Cúcuta'},
    {id: 'V6', nombre: 'Mercado Campesino', municipio: 'Pamplona'}
] AS row
MERGE (v:PuntoVenta {id: row.id})
SET v.nombre = row.nombre, v.municipio = row.municipio;

// Lotes e instalaciones que participan en cada etapa de procesamiento.
UNWIND [
    {lote: 'MP-001', instalacion: 'I1', fecha: '2026-10-10'},
    {lote: 'MP-002', instalacion: 'I1', fecha: '2026-10-10'},
    {lote: 'PT-010', instalacion: 'I2', fecha: '2026-10-12'},
    {lote: 'PT-011', instalacion: 'I3', fecha: '2026-10-13'},
    {lote: 'PT-020', instalacion: 'I2', fecha: '2026-10-14'},
    {lote: 'PT-030', instalacion: 'I4', fecha: '2026-10-15'},
    {lote: 'PT-040', instalacion: 'I6', fecha: '2026-10-16'}
] AS row
MATCH (l:Lote {codigo: row.lote})
MATCH (i:Instalacion {id: row.instalacion})
MERGE (l)-[r:PROCESADO_EN]->(i)
SET r.fecha = date(row.fecha);

// Ingredientes: lote de origen -> lote producido.
UNWIND [
    {origen: 'MP-001', destino: 'PT-010', cantidad_kg: 24.0},
    {origen: 'MP-002', destino: 'PT-010', cantidad_kg: 20.0},
    {origen: 'MP-003', destino: 'PT-011', cantidad_kg: 18.0},
    {origen: 'MP-004', destino: 'PT-011', cantidad_kg: 12.0},
    {origen: 'PT-010', destino: 'PT-020', cantidad_kg: 10.0},
    {origen: 'MP-005', destino: 'PT-020', cantidad_kg: 8.0},
    {origen: 'PT-010', destino: 'PT-030', cantidad_kg: 24.0},
    {origen: 'MP-004', destino: 'PT-040', cantidad_kg: 30.0}
] AS row
MATCH (origen:Lote {codigo: row.origen})
MATCH (destino:Lote {codigo: row.destino})
MERGE (origen)-[r:INSUMO_DE]->(destino)
SET r.cantidad_kg = row.cantidad_kg;

// Envíos identificados como relaciones para conservar entregas repetidas.
UNWIND [
    {id: 'SHP-001', lote: 'PT-010', punto: 'V1', fecha: '2026-10-14', cantidad_kg: 15.0},
    {id: 'SHP-002', lote: 'PT-010', punto: 'V2', fecha: '2026-10-14', cantidad_kg: 10.0},
    {id: 'SHP-003', lote: 'PT-020', punto: 'V1', fecha: '2026-10-16', cantidad_kg: 6.0},
    {id: 'SHP-004', lote: 'PT-020', punto: 'V3', fecha: '2026-10-17', cantidad_kg: 5.0},
    {id: 'SHP-005', lote: 'PT-011', punto: 'V2', fecha: '2026-10-16', cantidad_kg: 12.0},
    {id: 'SHP-006', lote: 'PT-011', punto: 'V3', fecha: '2026-10-17', cantidad_kg: 8.0},
    {id: 'SHP-007', lote: 'PT-030', punto: 'V4', fecha: '2026-10-18', cantidad_kg: 18.0},
    {id: 'SHP-008', lote: 'PT-030', punto: 'V2', fecha: '2026-10-18', cantidad_kg: 8.0},
    {id: 'SHP-009', lote: 'PT-040', punto: 'V5', fecha: '2026-10-19', cantidad_kg: 10.0},
    {id: 'SHP-010', lote: 'PT-040', punto: 'V6', fecha: '2026-10-19', cantidad_kg: 8.0}
] AS row
MATCH (l:Lote {codigo: row.lote})
MATCH (v:PuntoVenta {id: row.punto})
MERGE (l)-[r:ENVIADO_A {id: row.id}]->(v)
SET r.fecha = date(row.fecha), r.cantidad_kg = row.cantidad_kg;

// Incidentes para demostrar trazabilidad hacia adelante.
UNWIND [
    {id: 'INC001', tipo: 'Contaminación microbiológica', estado: 'Abierto', fecha: '2026-10-20'},
    {id: 'INC002', tipo: 'Alerta de calidad de fruta', estado: 'En investigación', fecha: '2026-10-21'}
] AS row
MERGE (i:Incidente {id: row.id})
SET i.tipo = row.tipo, i.estado = row.estado, i.fecha = date(row.fecha);

UNWIND [
    {incidente: 'INC001', lote: 'MP-001'},
    {incidente: 'INC002', lote: 'MP-004'}
] AS row
MATCH (i:Incidente {id: row.incidente})
MATCH (l:Lote {codigo: row.lote})
MERGE (i)-[:AFECTA]->(l);
