// =====================================================================
// db/seed.cypher - Trazabilidad agroindustrial (Neo4j)
// Idempotente: se puede ejecutar varias veces sin duplicar datos.
// Ejecutar con:  cypher-shell -u neo4j -p <clave> -f db/seed.cypher
// =====================================================================

// ---------- 1. Restricciones de unicidad ----------
CREATE CONSTRAINT lote_codigo IF NOT EXISTS FOR (l:Lote) REQUIRE l.codigo IS UNIQUE;
CREATE CONSTRAINT productor_id IF NOT EXISTS FOR (p:Productor) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT instalacion_id IF NOT EXISTS FOR (i:Instalacion) REQUIRE i.id IS UNIQUE;
CREATE CONSTRAINT punto_venta_id IF NOT EXISTS FOR (v:PuntoVenta) REQUIRE v.id IS UNIQUE;
CREATE CONSTRAINT incidente_id IF NOT EXISTS FOR (i:Incidente) REQUIRE i.id IS UNIQUE;

// ---------- 2. Nodos y relaciones base ----------
MERGE (p1:Productor {id:'P1'}) SET p1.nombre='Finca La Esperanza', p1.municipio='Pamplona'
MERGE (p2:Productor {id:'P2'}) SET p2.nombre='Finca El Roble', p2.municipio='Pamplonita'
MERGE (mp1:Lote {codigo:'MP-001'}) SET mp1.tipo='MATERIA_PRIMA', mp1.producto='Leche', mp1.cantidad_kg=80, mp1.estado='ACTIVO'
MERGE (mp2:Lote {codigo:'MP-002'}) SET mp2.tipo='MATERIA_PRIMA', mp2.producto='Leche', mp2.cantidad_kg=40, mp2.estado='ACTIVO'
MERGE (pt:Lote {codigo:'PT-010'}) SET pt.tipo='PRODUCTO', pt.producto='Queso', pt.cantidad_kg=20, pt.estado='ACTIVO'
MERGE (po:Lote {codigo:'PT-020'}) SET po.tipo='PRODUCTO', po.producto='Postre', po.cantidad_kg=10, po.estado='ACTIVO'
MERGE (pl:Instalacion {id:'I1'}) SET pl.nombre='Planta Central', pl.tipo='PLANTA'
MERGE (pv:PuntoVenta {id:'V1'}) SET pv.nombre='Tienda Centro', pv.municipio='Pamplona'
MERGE (p1)-[:PRODUCE]->(mp1)
MERGE (p2)-[:PRODUCE]->(mp2)
MERGE (mp1)-[r1:INSUMO_DE]->(pt) SET r1.cantidad_kg=80
MERGE (mp2)-[r2:INSUMO_DE]->(pt) SET r2.cantidad_kg=40
MERGE (pt)-[r3:INSUMO_DE]->(po) SET r3.cantidad_kg=5
MERGE (pt)-[r4:PROCESADO_EN]->(pl) SET r4.fecha=date('2026-10-12')
MERGE (pt)-[r5:ENVIADO_A]->(pv) SET r5.fecha=date('2026-10-14'), r5.cantidad_kg=20
// [VERIFICAR] la linea original llegaba cortada: propiedades de este ultimo envio asumidas
MERGE (po)-[r6:ENVIADO_A]->(pv) SET r6.fecha=date('2026-10-15'), r6.cantidad_kg=10;

// ---------- 3. Incidente de demo (trazabilidad) ----------
MATCH (mp1:Lote {codigo:'MP-001'})
MERGE (inc:Incidente {id:'INC001'})
  SET inc.tipo='Contaminación', inc.estado='Abierto', inc.fecha=date('2026-10-23')
MERGE (inc)-[:AFECTA]->(mp1);

// ---------- 4. Opcional: lote suelto que existe hoy en la base (creado desde la API) ----------
// MERGE (mp3:Lote {codigo:'MP-003'})
//   SET mp3.tipo='MATERIA_PRIMA', mp3.producto='Leche', mp3.cantidad_kg=60, mp3.estado='ACTIVO';

// ---------- 5. Verificacion ----------
// MATCH (n) RETURN labels(n)[0] AS etiqueta, count(*) AS total;
// MATCH ()-[r]->() RETURN type(r) AS relacion, count(*) AS total;
// Esperado sin MP-003: 9 nodos y 9 relaciones.

// ---------- 6. Consultas de trazabilidad para la demo ----------
// Hacia adelante: de un incidente a los puntos de venta afectados
// MATCH (inc:Incidente {id:'INC001'})-[:AFECTA]->(origen:Lote)
// MATCH ruta = (origen)-[:INSUMO_DE*0..]->(l:Lote)-[:ENVIADO_A]->(pv:PuntoVenta)
// RETURN inc.id AS incidente, origen.codigo AS lote_origen,
//        l.codigo AS lote_enviado, pv.id AS punto_venta, length(ruta) AS saltos;
//
// Hacia atras: de un lote terminado hasta sus productores
// MATCH ruta = (p:Productor)-[:PRODUCE]->(:Lote)-[:INSUMO_DE*1..]->(l:Lote {codigo:'PT-020'})
// RETURN ruta;