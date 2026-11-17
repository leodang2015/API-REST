from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status

from app.controllers import productos as controlador
from app.core.dependencies import CurrentUser, SessionDep, requiere_rol
from app.models.usuario import Usuario
from app.schemas.producto import ProductoActualizar, ProductoCrear, ProductoLeer

router = APIRouter(prefix="/productos", tags=["productos"])
AdminDep = Annotated[Usuario, Depends(requiere_rol("admin"))]


@router.get("", response_model=list[ProductoLeer])
def listar(
    _user: CurrentUser,
    db: SessionDep,
    categoria_id: int | None = Query(default=None, gt=0),
    buscar: str | None = Query(default=None, max_length=100),
    solo_activos: bool = False,
) -> list[ProductoLeer]:
    return controlador.listar(db, categoria_id, buscar, solo_activos)


@router.get("/{producto_id}", response_model=ProductoLeer)
def obtener(producto_id: int, _user: CurrentUser, db: SessionDep) -> ProductoLeer:
    return controlador.obtener(db, producto_id)


@router.post("", response_model=ProductoLeer, status_code=status.HTTP_201_CREATED)
def crear(datos: ProductoCrear, db: SessionDep, _admin: AdminDep) -> ProductoLeer:
    return controlador.crear(db, datos)


@router.patch("/{producto_id}", response_model=ProductoLeer)
def actualizar(
    producto_id: int,
    datos: ProductoActualizar,
    db: SessionDep,
    _admin: AdminDep,
) -> ProductoLeer:
    return controlador.actualizar(db, producto_id, datos)


@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(producto_id: int, db: SessionDep, _admin: AdminDep) -> Response:
    controlador.eliminar(db, producto_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
