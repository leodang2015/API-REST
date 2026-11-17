from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.common import limpiar_nombre


class AutorCrear(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)
    nacionalidad: str | None = Field(default=None, max_length=60)
    anio_nacimiento: int | None = Field(default=None, ge=1000)

    validar_nombre = field_validator("nombre")(limpiar_nombre)


class AutorActualizar(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=100)
    nacionalidad: str | None = Field(default=None, max_length=60)
    anio_nacimiento: int | None = Field(default=None, ge=1000)

    validar_nombre = field_validator("nombre")(limpiar_nombre)


class AutorLeer(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    nacionalidad: str | None
    anio_nacimiento: int | None


class AutorResumen(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
