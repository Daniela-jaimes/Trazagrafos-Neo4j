import unittest
from unittest.mock import patch

from fastapi import HTTPException
from neo4j.exceptions import ServiceUnavailable

from app.routers import trazabilidad


class FakeDriver:
    def __init__(self, records=None, error=None):
        self.records = records or []
        self.error = error
        self.query = None
        self.parameters = None
        self.database = None

    def execute_query(self, query, parameters, database_):
        self.query = query
        self.parameters = parameters
        self.database = database_
        if self.error:
            raise self.error
        return self.records, None, None


class TraceabilityEndpointTests(unittest.TestCase):
    def setUp(self):
        self.driver = FakeDriver()
        self.driver_patch = patch.object(trazabilidad, "driver", self.driver)
        self.driver_patch.start()
        self.addCleanup(self.driver_patch.stop)

    def test_backward_trace_returns_lot_origins(self):
        self.driver.records = [
            {
                "lote": {"codigo": "PT-020", "producto": "Postre lácteo"},
                "origenes": [
                    {
                        "productor": {"id": "P1"},
                        "lote_origen": {"codigo": "MP-001"},
                        "ruta": ["P1", "MP-001", "PT-010", "PT-020"],
                    }
                ],
            }
        ]

        result = trazabilidad.trazar_origen("PT-020")

        self.assertEqual(result["lote"]["codigo"], "PT-020")
        self.assertEqual(result["origenes"][0]["lote_origen"]["codigo"], "MP-001")
        self.assertIn("PRODUCE", self.driver.query)
        self.assertIn("INSUMO_DE*0..", self.driver.query)
        self.assertEqual(self.driver.parameters, {"codigo": "PT-020"})
        self.assertEqual(self.driver.database, "neo4j")

    def test_forward_trace_returns_shipments_and_destinations(self):
        self.driver.records = [
            {
                "lote": {"codigo": "MP-001"},
                "destinos": [
                    {
                        "lote_enviado": {"codigo": "PT-010"},
                        "punto_venta": {"id": "V1"},
                        "envio": {"id": "SHP-001", "cantidad_kg": 15.0},
                        "ruta": ["MP-001", "PT-010"],
                    }
                ],
            }
        ]

        result = trazabilidad.trazar_destino("MP-001")

        self.assertEqual(result["destinos"][0]["punto_venta"]["id"], "V1")
        self.assertIn("INSUMO_DE*0..", self.driver.query)
        self.assertIn("ENVIADO_A", self.driver.query)
        self.assertEqual(self.driver.parameters, {"codigo": "MP-001"})

    def test_incident_trace_returns_impacted_shipments(self):
        self.driver.records = [
            {
                "incidente": {"id": "INC001"},
                "destinos": [
                    {
                        "lote_afectado": {"codigo": "MP-001"},
                        "lote_enviado": {"codigo": "PT-010"},
                        "punto_venta": {"id": "V1"},
                        "envio": {"id": "SHP-001"},
                        "ruta": ["MP-001", "PT-010"],
                    }
                ],
            }
        ]

        result = trazabilidad.trazar_incidente("INC001")

        self.assertEqual(result["incidente"]["id"], "INC001")
        self.assertEqual(result["destinos"][0]["punto_venta"]["id"], "V1")
        self.assertIn("AFECTA", self.driver.query)
        self.assertIn("ENVIADO_A", self.driver.query)

    def test_unknown_lot_and_incident_return_404(self):
        for endpoint, identifier in (
            (trazabilidad.trazar_origen, "UNKNOWN"),
            (trazabilidad.trazar_destino, "UNKNOWN"),
            (trazabilidad.trazar_incidente, "UNKNOWN"),
        ):
            with self.subTest(endpoint=endpoint.__name__):
                self.driver.records = []
                with self.assertRaises(HTTPException) as raised:
                    endpoint(identifier)
                self.assertEqual(raised.exception.status_code, 404)

    def test_neo4j_unavailable_returns_503(self):
        self.driver.error = ServiceUnavailable("offline")

        with self.assertRaises(HTTPException) as raised:
            trazabilidad.trazar_destino("MP-001")

        self.assertEqual(raised.exception.status_code, 503)

    def test_traceability_routes_are_registered(self):
        from app.main import app
        from app.db import driver

        self.addCleanup(driver.close)
        paths = app.openapi()["paths"]
        self.assertIn("/trazabilidad/lotes/{codigo}/origen", paths)
        self.assertIn("/trazabilidad/lotes/{codigo}/destino", paths)
        self.assertIn("/trazabilidad/incidentes/{incidente_id}", paths)


if __name__ == "__main__":
    unittest.main()
