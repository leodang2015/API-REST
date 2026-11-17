from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.libro import LibroLeer
from app.schemas.socio import SocioResumen


class PrestamoCrear(BaseModel):
    socio_id: int = Field(gt=0)
    libro_id: int = Field(gt=0)
    fecha_limite: datetime


class PrestamoActualizar(BaseModel):
    fecha_devolucion: datetime | None = None
    multa: float | None = Field(default=None, ge=0)
    devuelto: bool | None = None

    @model_validator(mode="after")
    def validar_devolucion(self) -> "PrestamoActualizar":
        if self.devuelto is True and self.fecha_devolucion is None:
            raise ValueError("Indica fecha_devolucion para registrar la devolución")
        if self.devuelto is False and self.fecha_devolucion is not None:
            raise ValueError("No se puede marcar como activo un préstamo devuelto")
        return self


class PrestamoLeer(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    socio_id: int
    libro_id: int
    fecha_prestamo: datetime
    fecha_limite: datetime
    fecha_devolucion: datetime | None
    multa: float
    devuelto: bool
    socio: SocioResumen
    libro: LibroLeer
