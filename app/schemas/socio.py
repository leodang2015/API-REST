from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.schemas.common import limpiar_nombre


class SocioCrear(BaseModel):
    nombre: str = Field(min_length=2, max_length=120)
    email: EmailStr
    telefono: str | None = Field(default=None, max_length=30)
    activo: bool = True

    validar_nombre = field_validator("nombre")(limpiar_nombre)


class SocioActualizar(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=120)
    email: EmailStr | None = None
    telefono: str | None = Field(default=None, max_length=30)
    activo: bool | None = None

    validar_nombre = field_validator("nombre")(limpiar_nombre)


class SocioLeer(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    email: EmailStr
    telefono: str | None
    activo: bool
    creado_en: datetime


class SocioResumen(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    email: EmailStr
