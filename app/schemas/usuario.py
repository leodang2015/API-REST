from datetime import datetime
from typing import Annotated

from pydantic import EmailStr, StringConstraints

from app.schemas.pagina import ORMModel

Nombre = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
Contrasena = Annotated[str, StringConstraints(min_length=8, max_length=128)]


class UsuarioCrear(ORMModel):
    nombre: Nombre
    email: EmailStr
    password: Contrasena


class UsuarioActualizar(ORMModel):
    nombre: Nombre | None = None
    email: EmailStr | None = None


class UsuarioPublico(ORMModel):
    id: int
    nombre: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime
