from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from app.controllers import prestamos as controlador
from app.core.dependencies import SessionDep, requiere_rol
from app.models.usuario import Usuario
from app.schemas.prestamo import PrestamoActualizar, PrestamoCrear, PrestamoLeer

router = APIRouter(prefix="/prestamos", tags=["préstamos"])
AdminDep = Annotated[Usuario, Depends(requiere_rol("bibliotecario"))]


@router.get("", response_model=list[PrestamoLeer])
def listar(db: SessionDep, _admin: AdminDep) -> list[PrestamoLeer]:
    return controlador.listar(db)


@router.get("/{prestamo_id}", response_model=PrestamoLeer)
def obtener(prestamo_id: int, db: SessionDep, _admin: AdminDep) -> PrestamoLeer:
    return controlador.obtener(db, prestamo_id)


@router.post("", response_model=PrestamoLeer, status_code=status.HTTP_201_CREATED)
def crear(datos: PrestamoCrear, db: SessionDep, _admin: AdminDep) -> PrestamoLeer:
    return controlador.crear(db, datos)


@router.patch("/{prestamo_id}", response_model=PrestamoLeer)
def actualizar(
    prestamo_id: int,
    datos: PrestamoActualizar,
    db: SessionDep,
    _admin: AdminDep,
) -> PrestamoLeer:
    return controlador.actualizar(db, prestamo_id, datos)


@router.delete("/{prestamo_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(prestamo_id: int, db: SessionDep, _admin: AdminDep) -> Response:
    controlador.eliminar(db, prestamo_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
