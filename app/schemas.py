from typing import Literal
from pydantic import BaseModel, Field


class LoteCreate(BaseModel):
    codigo: str = Field(min_length=1, max_length=50)
    tipo: Literal["MATERIA_PRIMA", "PRODUCTO"]
    producto: str = Field(min_length=1, max_length=100)
    cantidad_kg: float = Field(gt=0)
    estado: str = "ACTIVO"