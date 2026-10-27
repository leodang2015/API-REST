from pydantic import EmailStr

from app.schemas.pagina import ORMModel
from app.schemas.usuario import Contrasena, UsuarioPublico


class LoginRequest(ORMModel):
    email: EmailStr
    password: Contrasena


class RefreshRequest(ORMModel):
    refresh_token: str


class TokenResponse(ORMModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RegistroResponse(ORMModel):
    usuario: UsuarioPublico
