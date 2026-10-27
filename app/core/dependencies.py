from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.exceptions import NoAutenticado, Prohibido
from app.core.security import decode_token
from app.models.usuario import Usuario

bearer_scheme = HTTPBearer(auto_error=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


SessionDep = Annotated[Session, Depends(get_db)]


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: SessionDep,
) -> Usuario:
    if credentials is None:
        raise NoAutenticado()
    try:
        claims = decode_token(credentials.credentials)
        if claims.get("type") != "access":
            raise NoAutenticado("Se requiere un token de acceso")
        user_id = int(claims["sub"])
    except (JWTError, KeyError, TypeError, ValueError) as exc:
        raise NoAutenticado("Token inválido o expirado") from exc

    user = db.get(Usuario, user_id)
    if user is None or not user.is_active:
        raise NoAutenticado("Usuario inexistente o inactivo")
    return user


CurrentUser = Annotated[Usuario, Depends(get_current_user)]


def requiere_rol(*roles: str):
    def check_role(user: CurrentUser) -> Usuario:
        if user.role not in roles:
            raise Prohibido()
        return user

    return check_role


class Paginacion:
    def __init__(
        self,
        page: Annotated[int, Query(ge=1)] = 1,
        page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    ) -> None:
        self.page = page
        self.page_size = page_size
        self.offset = (page - 1) * page_size


PaginationDep = Annotated[Paginacion, Depends()]