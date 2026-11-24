from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from app.controllers import categorias as controlador
from app.controllers import productos as productos_controlador
from app.core.dependencies import CurrentUser, SessionDep, requiere_rol
from app.models.usuario import Usuario
from app.schemas.categoria import CategoriaActualizar, CategoriaCrear, CategoriaLeer
from app.schemas.producto import ProductoLeer

router = APIRouter(prefix="/categorias", tags=["categorías"])
AdminDep = Annotated[Usuario, Depends(requiere_rol("bibliotecario"))]


@router.get("", response_model=list[CategoriaLeer])
def listar(_user: CurrentUser, db: SessionDep) -> list[CategoriaLeer]:
    return controlador.listar(db)


@router.get("/{categoria_id}/productos", response_model=list[ProductoLeer])
def listar_productos(categoria_id: int, _user: CurrentUser, db: SessionDep) -> list[ProductoLeer]:
    controlador.obtener(db, categoria_id)
    return productos_controlador.listar(db, categoria_id=categoria_id)


@router.get("/{categoria_id}", response_model=CategoriaLeer)
def obtener(categoria_id: int, _user: CurrentUser, db: SessionDep) -> CategoriaLeer:
    return controlador.obtener(db, categoria_id)


@router.post("", response_model=CategoriaLeer, status_code=status.HTTP_201_CREATED)
def crear(datos: CategoriaCrear, db: SessionDep, _admin: AdminDep) -> CategoriaLeer:
    return controlador.crear(db, datos)


@router.patch("/{categoria_id}", response_model=CategoriaLeer)
def actualizar(
    categoria_id: int,
    datos: CategoriaActualizar,
    db: SessionDep,
    _admin: AdminDep,
) -> CategoriaLeer:
    return controlador.actualizar(db, categoria_id, datos)


@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(categoria_id: int, db: SessionDep, _admin: AdminDep) -> Response:
    controlador.eliminar(db, categoria_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
