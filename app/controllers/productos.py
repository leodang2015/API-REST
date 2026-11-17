from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.controllers.common import guardar
from app.models.categoria import Categoria
from app.models.producto import Producto
from app.schemas.producto import ProductoActualizar, ProductoCrear


def _consulta_base():
    return select(Producto).options(selectinload(Producto.categoria))


def listar(
    db: Session,
    categoria_id: int | None = None,
    buscar: str | None = None,
    solo_activos: bool = False,
) -> list[Producto]:
    consulta = _consulta_base()
    if categoria_id is not None:
        consulta = consulta.where(Producto.categoria_id == categoria_id)
    if buscar:
        consulta = consulta.where(Producto.nombre.ilike(f"%{buscar}%"))
    if solo_activos:
        consulta = consulta.where(Producto.activo.is_(True))
    return list(db.scalars(consulta.order_by(Producto.nombre)))


def obtener(db: Session, producto_id: int) -> Producto:
    producto = db.scalar(_consulta_base().where(Producto.id == producto_id))
    if producto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado",
        )
    return producto


def _validar_nombre_unico(db: Session, nombre: str, excluir_id: int | None = None) -> None:
    consulta = select(Producto.id).where(func.lower(Producto.nombre) == nombre.lower())
    if excluir_id is not None:
        consulta = consulta.where(Producto.id != excluir_id)
    if db.scalar(consulta) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe el producto '{nombre}'",
        )


def crear(db: Session, datos: ProductoCrear) -> Producto:
    if db.get(Categoria, datos.categoria_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada",
        )
    _validar_nombre_unico(db, datos.nombre)
    producto = Producto(**datos.model_dump())
    db.add(producto)
    guardar(db, f"Ya existe el producto '{datos.nombre}'")
    return obtener(db, producto.id)


def actualizar(db: Session, producto_id: int, datos: ProductoActualizar) -> Producto:
    producto = obtener(db, producto_id)
    cambios = datos.model_dump(exclude_unset=True, exclude_none=True)
    if "categoria_id" in cambios and db.get(Categoria, cambios["categoria_id"]) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada",
        )
    if "nombre" in cambios:
        _validar_nombre_unico(db, cambios["nombre"], excluir_id=producto_id)
    for campo, valor in cambios.items():
        setattr(producto, campo, valor)
    guardar(db, "Ya existe otro producto con ese nombre")
    return obtener(db, producto_id)


def eliminar(db: Session, producto_id: int) -> None:
    producto = obtener(db, producto_id)
    db.delete(producto)
    guardar(db, "No se puede eliminar el producto")
