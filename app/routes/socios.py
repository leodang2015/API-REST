from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from app.controllers import socios as controlador
from app.core.dependencies import SessionDep, requiere_rol
from app.models.usuario import Usuario
from app.schemas.socio import SocioActualizar, SocioCrear, SocioLeer

router = APIRouter(prefix="/socios", tags=["socios"])
AdminDep = Annotated[Usuario, Depends(requiere_rol("admin"))]


@router.get("", response_model=list[SocioLeer])
def listar(db: SessionDep, _admin: AdminDep) -> list[SocioLeer]:
    return controlador.listar(db)


@router.get("/{socio_id}", response_model=SocioLeer)
def obtener(socio_id: int, db: SessionDep, _admin: AdminDep) -> SocioLeer:
    return controlador.obtener(db, socio_id)


@router.post("", response_model=SocioLeer, status_code=status.HTTP_201_CREATED)
def crear(datos: SocioCrear, db: SessionDep, _admin: AdminDep) -> SocioLeer:
    return controlador.crear(db, datos)


@router.patch("/{socio_id}", response_model=SocioLeer)
def actualizar(
    socio_id: int,
    datos: SocioActualizar,
    db: SessionDep,
    _admin: AdminDep,
) -> SocioLeer:
    return controlador.actualizar(db, socio_id, datos)


@router.delete("/{socio_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(socio_id: int, db: SessionDep, _admin: AdminDep) -> Response:
    controlador.eliminar(db, socio_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
