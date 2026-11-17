from datetime import datetime

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, field_validator

from app.schemas.autor import AutorResumen
from app.schemas.categoria import CategoriaResumen
from app.schemas.common import limpiar_nombre


class LibroCrear(BaseModel):
    titulo: str = Field(min_length=2, max_length=150)
    isbn: str = Field(min_length=8, max_length=20)
    descripcion: str | None = Field(default=None, max_length=500)
    anio_publicacion: int | None = Field(default=None, ge=1000)
    ejemplares: int = Field(default=1, ge=1)
    disponible: int = Field(default=1, ge=0)
    autor_id: int = Field(gt=0)
    categoria_ids: list[int] = Field(default_factory=list)

    validar_titulo = field_validator("titulo")(limpiar_nombre)


class LibroActualizar(BaseModel):
    titulo: str | None = Field(default=None, min_length=2, max_length=150)
    isbn: str | None = Field(default=None, min_length=8, max_length=20)
    descripcion: str | None = Field(default=None, max_length=500)
    anio_publicacion: int | None = Field(default=None, ge=1000)
    ejemplares: int | None = Field(default=None, ge=1)
    disponible: int | None = Field(default=None, ge=0)
    autor_id: int | None = Field(default=None, gt=0)
    categoria_ids: list[int] | None = None

    validar_titulo = field_validator("titulo")(limpiar_nombre)


class LibroLeer(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    titulo: str
    isbn: str
    descripcion: str | None
    anio_publicacion: int | None
    ejemplares: int
    disponible: int
    creado_en: datetime
    portada_url: AnyHttpUrl | None
    autor: AutorResumen
    categorias: list[CategoriaResumen]
