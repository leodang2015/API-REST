from fastapi import APIRouter, status

from app.controllers import auth as auth_controller
from app.core.dependencies import CurrentUser, SessionDep
from app.models.usuario import Usuario
from app.schemas.auth import LoginRequest, RefreshRequest, RegistroResponse, TokenResponse
from app.schemas.usuario import UsuarioCrear, UsuarioPublico

router = APIRouter(prefix="/auth", tags=["autenticación"])


@router.post("/registro", response_model=RegistroResponse, status_code=status.HTTP_201_CREATED)
def registrar(data: UsuarioCrear, db: SessionDep) -> RegistroResponse:
    return RegistroResponse(usuario=auth_controller.registrar_usuario(db, data))


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: SessionDep) -> dict[str, str]:
    user = auth_controller.autenticar_usuario(db, data)
    return auth_controller.crear_tokens(db, user)


@router.post("/refresh", response_model=TokenResponse)
def refresh(data: RefreshRequest, db: SessionDep) -> dict[str, str]:
    return auth_controller.renovar_tokens(db, data.refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(data: RefreshRequest, db: SessionDep) -> None:
    auth_controller.revocar_refresh_token(db, data.refresh_token)


@router.get("/me", response_model=UsuarioPublico)
def perfil_actual(current_user: CurrentUser) -> Usuario:
    return current_user
