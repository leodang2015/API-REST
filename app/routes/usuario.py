from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.controllers import usuario as usuario_controller
from app.core.dependencies import (
    CurrentUser,
    PaginationDep,
    SessionDep,
    requiere_rol,
)
from app.core.exceptions import Prohibido
from app.models.usuario import Usuario
from app.schemas.pagina import Pagina
from app.schemas.usuario import UsuarioActualizar, UsuarioPublico

router = APIRouter(prefix="/usuarios", tags=["usuarios"])
AdminDep = Annotated[Usuario, Depends(requiere_rol("admin"))]


@router.get("/me", response_model=UsuarioPublico)
def perfil_actual(current_user: CurrentUser) -> Usuario:
    return current_user


@router.patch("/me", response_model=UsuarioPublico)
def actualizar_perfil(
    data: UsuarioActualizar,
    current_user: CurrentUser,
    db: SessionDep,
) -> Usuario:
    return usuario_controller.actualizar_usuario(db, current_user, data)


@router.get("", response_model=Pagina[UsuarioPublico])
def listar(
    db: SessionDep,
    pagination: PaginationDep,
    _admin: AdminDep,
) -> Pagina[UsuarioPublico]:
    items, total = usuario_controller.listar_usuarios(
        db,
        offset=pagination.offset,
        limit=pagination.page_size,
    )
    return Pagina(
        items=items,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    )


@router.get("/{user_id}", response_model=UsuarioPublico)
def obtener(
    user_id: int,
    db: SessionDep,
    current_user: CurrentUser,
) -> Usuario:
    if current_user.id != user_id and current_user.role != "admin":
        raise Prohibido()
    user = usuario_controller.obtener_usuario(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def desactivar(
    user_id: int,
    db: SessionDep,
    _admin: AdminDep,
) -> None:
    user = usuario_controller.obtener_usuario(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    usuario_controller.desactivar_usuario(db, user)
