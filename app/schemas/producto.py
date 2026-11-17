from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.categoria import CategoriaResumen
from app.schemas.common import limpiar_nombre


class ProductoCrear(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)
    descripcion: str | None = Field(default=None, max_length=300)
    precio: float = Field(gt=0, le=1_000_000)
    stock: int = Field(default=0, ge=0)
    activo: bool = True
    categoria_id: int = Field(gt=0)

    validar_nombre = field_validator("nombre")(
        lambda value: limpiar_nombre(value, capitalizar=True)
    )


class ProductoActualizar(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=100)
    descripcion: str | None = Field(default=None, max_length=300)
    precio: float | None = Field(default=None, gt=0, le=1_000_000)
    stock: int | None = Field(default=None, ge=0)
    activo: bool | None = None
    categoria_id: int | None = Field(default=None, gt=0)

    validar_nombre = field_validator("nombre")(
        lambda value: limpiar_nombre(value, capitalizar=True)
    )


class ProductoLeer(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    descripcion: str | None
    precio: float
    stock: int
    activo: bool
    creado_en: datetime
    categoria: CategoriaResumen
