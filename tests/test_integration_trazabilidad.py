import os
import unittest
from pathlib import Path

from neo4j import GraphDatabase

from app.routers import trazabilidad


TEST_URI = os.getenv("NEO4J_TEST_URI")


@unittest.skipUnless(
    TEST_URI,
    "Set NEO4J_TEST_URI to run integration tests against a dedicated Neo4j test database.",
)
class SeedTraceabilityIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = GraphDatabase.driver(
            TEST_URI,
            auth=(
                os.getenv("NEO4J_TEST_USER", "neo4j"),
                os.getenv("NEO4J_TEST_PASSWORD", ""),
            ),
        )
        cls.driver.verify_connectivity()

        seed_path = Path(__file__).resolve().parents[1] / "scripts" / "seed.cypher"
        seed = seed_path.read_text(encoding="utf-8")
        seed_without_comments = "\n".join(
            line.split("//", maxsplit=1)[0] for line in seed.splitlines()
        )
        statements = [
            statement for statement in seed_without_comments.split(";")
            if statement.strip()
        ]
        for _ in range(2):
            for statement in statements:
                cls.driver.execute_query(statement, database_="neo4j")

    @classmethod
    def tearDownClass(cls):
        cls.driver.close()

    def test_seed_has_expected_facilities_and_shipments(self):
        records, _, _ = self.driver.execute_query(
            """
            MATCH (p:Productor)
            WITH count(p) AS productores
            MATCH (l:Lote)
            WITH productores, count(l) AS lotes
            MATCH (i:Instalacion)
            WITH productores, lotes, count(i) AS instalaciones
            MATCH (v:PuntoVenta)
            WITH productores, lotes, instalaciones, count(v) AS puntos_venta
            MATCH (inc:Incidente)
            WITH productores, lotes, instalaciones, puntos_venta, count(inc) AS incidentes
            MATCH ()-[e:ENVIADO_A]->()
            RETURN productores, lotes, instalaciones, puntos_venta, incidentes,
                   count(e) AS envios
            """,
            database_="neo4j",
        )
        self.assertEqual(
            dict(records[0]),
            {
                "productores": 4,
                "lotes": 10,
                "instalaciones": 6,
                "puntos_venta": 6,
                "incidentes": 2,
                "envios": 10,
            },
        )

    def test_seeded_raw_lot_traces_to_all_impacted_stores(self):
        result = trazabilidad.trazar_destino("MP-001", self.driver)

        stores = {row["punto_venta"]["id"] for row in result["destinos"]}
        self.assertEqual(stores, {"V1", "V2", "V3", "V4"})

    def test_seeded_finished_lot_traces_back_to_all_producers(self):
        result = trazabilidad.trazar_origen("PT-020", self.driver)

        producer_ids = {row["productor"]["id"] for row in result["origenes"]}
        self.assertEqual(producer_ids, {"P1", "P2"})

    def test_seeded_incident_traces_to_affected_stores(self):
        result = trazabilidad.trazar_incidente("INC001", self.driver)

        stores = {row["punto_venta"]["id"] for row in result["destinos"]}
        self.assertEqual(stores, {"V1", "V2", "V3", "V4"})


if __name__ == "__main__":
    unittest.main()
