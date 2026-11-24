from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from app.controllers import autores as controlador
from app.core.dependencies import CurrentUser, SessionDep, requiere_rol
from app.models.usuario import Usuario
from app.schemas.autor import AutorActualizar, AutorCrear, AutorLeer

router = APIRouter(prefix="/autores", tags=["autores"])
AdminDep = Annotated[Usuario, Depends(requiere_rol("bibliotecario"))]


@router.get("", response_model=list[AutorLeer])
def listar(_user: CurrentUser, db: SessionDep) -> list[AutorLeer]:
    return controlador.listar(db)


@router.get("/{autor_id}", response_model=AutorLeer)
def obtener(autor_id: int, _user: CurrentUser, db: SessionDep) -> AutorLeer:
    return controlador.obtener(db, autor_id)


@router.post("", response_model=AutorLeer, status_code=status.HTTP_201_CREATED)
def crear(datos: AutorCrear, db: SessionDep, _admin: AdminDep) -> AutorLeer:
    return controlador.crear(db, datos)


@router.patch("/{autor_id}", response_model=AutorLeer)
def actualizar(
    autor_id: int,
    datos: AutorActualizar,
    db: SessionDep,
    _admin: AdminDep,
) -> AutorLeer:
    return controlador.actualizar(db, autor_id, datos)


@router.delete("/{autor_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(autor_id: int, db: SessionDep, _admin: AdminDep) -> Response:
    controlador.eliminar(db, autor_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
