from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.common import limpiar_nombre


class CategoriaCrear(BaseModel):
    nombre: str = Field(min_length=3, max_length=50)
    descripcion: str | None = Field(default=None, max_length=200)

    validar_nombre = field_validator("nombre")(
        lambda value: limpiar_nombre(value, capitalizar=True)
    )


class CategoriaActualizar(BaseModel):
    nombre: str | None = Field(default=None, min_length=3, max_length=50)
    descripcion: str | None = Field(default=None, max_length=200)

    validar_nombre = field_validator("nombre")(
        lambda value: limpiar_nombre(value, capitalizar=True)
    )


class CategoriaLeer(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    descripcion: str | None


class CategoriaResumen(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
