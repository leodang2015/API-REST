from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.schemas.libro import LibroLeer
from app.schemas.pagina import ORMModel
from app.schemas.socio import SocioResumen


class SolicitudCrear(BaseModel):
    libro_id: int = Field(gt=0)


class SolicitudResolver(BaseModel):
    estado: Literal["aceptada", "rechazada"]
    fecha_entrega_estimada: datetime | None = None

    @model_validator(mode="after")
    def validar_fecha_entrega(self) -> "SolicitudResolver":
        if self.estado == "aceptada" and self.fecha_entrega_estimada is None:
            raise ValueError("Indica una fecha estimada para aceptar la solicitud")
        if self.estado == "rechazada" and self.fecha_entrega_estimada is not None:
            raise ValueError("Una solicitud rechazada no debe tener fecha estimada")
        return self


class SolicitudLeer(ORMModel):
    id: int
    socio_id: int
    libro_id: int
    fecha_solicitud: datetime
    estado: str
    fecha_entrega_estimada: datetime | None
    socio: SocioResumen
    libro: LibroLeer
