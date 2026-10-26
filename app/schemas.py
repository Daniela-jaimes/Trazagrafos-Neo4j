from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator

EstadoLote = Literal["ACTIVO", "RETENIDO", "RETIRADO"]
TipoLote = Literal["MATERIA_PRIMA", "PRODUCTO"]


class LoteBase(BaseModel):
    tipo: TipoLote
    producto: str = Field(min_length=1, max_length=100)
    cantidad_kg: float = Field(gt=0)
    estado: EstadoLote = Field(default="ACTIVO")


class LoteCreate(LoteBase):
     codigo: str = Field(min_length=1, max_length=50)


class LoteReplace(LoteBase):
    """Cuerpo del PUT: reemplaza todos los campos; el código no se modifica."""


class LotePatch(BaseModel):
    """Cuerpo del PATCH: solo los campos enviados cambian."""

    tipo: Optional[TipoLote] = None
    producto: Optional[str] = Field(default=None, min_length=1, max_length=100)
    cantidad_kg: Optional[float] = Field(default=None, gt=0)
    estado: Optional[EstadoLote] = None
    @model_validator(mode="after")
    def al_menos_un_campo(self):
        if all(v is None for v in self.model_dump().values()):
            raise ValueError("Debe enviar al menos un campo para actualizar")
        return self


class LoteOut(BaseModel):
    codigo: str
    tipo: str
    producto: str
    cantidad_kg: float
    estado: str

# --------- Trazabilidad
class EnvioOut(BaseModel):
    lote: str
    punto_venta_id: str
    punto_venta: Optional[str] = None
    municipio: Optional[str] = None
    fecha: Optional[str] = None
    cantidad_kg: Optional[float] = None
    saltos: int  
class TrazaAdelanteOut(BaseModel):
    lote_origen: str
    total_puntos_venta: int
    envios: list[EnvioOut]


class OrigenOut(BaseModel):
    productor_id: str
    productor: Optional[str] = None
    municipio: Optional[str] = None
    lote_origen: str
    producto_origen: Optional[str] = None
    saltos: int 

class TrazaAtrasOut(BaseModel):
    lote: str
    total_productores: int
    origenes: list[OrigenOut]


class LoteResumen(BaseModel):
    codigo: str
    producto: Optional[str] = None


class PuntoVentaResumen(BaseModel):
    id: str
    nombre: Optional[str] = None


class AlcanceIncidenteOut(BaseModel):
    incidente: str
    tipo: Optional[str] = None
    estado: Optional[str] = None
    lotes_afectados: list[LoteResumen]
    puntos_venta: list[PuntoVentaResumen]


class LoteExpuestoOut(BaseModel):
    lote_expuesto: str
    producto: Optional[str] = None
    instalacion_id: str
    instalacion: Optional[str] = None
    lote_afectado: str
    fecha_afectado: Optional[str] = None
    fecha_expuesto: Optional[str] = None


class ContaminacionCruzadaOut(BaseModel):
    lote_origen: str
    ventana_dias: int
    total_lotes_expuestos: int
    lotes_expuestos: list[LoteExpuestoOut]
