from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.controllers.common import guardar
from app.models.categoria import Categoria
from app.models.libro import Libro
from app.models.producto import Producto
from app.schemas.categoria import CategoriaActualizar, CategoriaCrear


def listar(db: Session) -> list[Categoria]:
    return list(db.scalars(select(Categoria).order_by(Categoria.nombre)))


def obtener(db: Session, categoria_id: int) -> Categoria:
    categoria = db.get(Categoria, categoria_id)
    if categoria is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada",
        )
    return categoria


def _validar_nombre_unico(db: Session, nombre: str, excluir_id: int | None = None) -> None:
    consulta = select(Categoria.id).where(func.lower(Categoria.nombre) == nombre.lower())
    if excluir_id is not None:
        consulta = consulta.where(Categoria.id != excluir_id)
    if db.scalar(consulta) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe la categoría '{nombre}'",
        )


def crear(db: Session, datos: CategoriaCrear) -> Categoria:
    _validar_nombre_unico(db, datos.nombre)
    categoria = Categoria(**datos.model_dump())
    db.add(categoria)
    guardar(db, f"Ya existe la categoría '{datos.nombre}'")
    db.refresh(categoria)
    return categoria


def actualizar(db: Session, categoria_id: int, datos: CategoriaActualizar) -> Categoria:
    categoria = obtener(db, categoria_id)
    cambios = datos.model_dump(exclude_unset=True, exclude_none=True)
    if "nombre" in cambios:
        _validar_nombre_unico(db, cambios["nombre"], excluir_id=categoria_id)
    for campo, valor in cambios.items():
        setattr(categoria, campo, valor)
    guardar(db, "Ya existe otra categoría con ese nombre")
    db.refresh(categoria)
    return categoria


def eliminar(db: Session, categoria_id: int) -> None:
    categoria = obtener(db, categoria_id)
    libros = db.scalar(
        select(func.count(Libro.id))
        .join(Libro.categorias)
        .where(Categoria.id == categoria_id)
    ) or 0
    productos = db.scalar(
        select(func.count(Producto.id)).where(Producto.categoria_id == categoria_id)
    ) or 0
    if libros or productos:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar una categoría que tenga libros o productos",
        )
    db.delete(categoria)
    guardar(db, "No se puede eliminar la categoría")
