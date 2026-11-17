from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.controllers.common import guardar
from app.models.autor import Autor
from app.models.libro import Libro
from app.schemas.autor import AutorActualizar, AutorCrear


def listar(db: Session) -> list[Autor]:
    return list(db.scalars(select(Autor).order_by(Autor.nombre)))


def obtener(db: Session, autor_id: int) -> Autor:
    autor = db.get(Autor, autor_id)
    if autor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Autor no encontrado")
    return autor


def _validar_nombre_unico(db: Session, nombre: str, excluir_id: int | None = None) -> None:
    consulta = select(Autor.id).where(func.lower(Autor.nombre) == nombre.lower())
    if excluir_id is not None:
        consulta = consulta.where(Autor.id != excluir_id)
    if db.scalar(consulta) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe el autor '{nombre}'",
        )


def crear(db: Session, datos: AutorCrear) -> Autor:
    _validar_nombre_unico(db, datos.nombre)
    autor = Autor(**datos.model_dump())
    db.add(autor)
    guardar(db, f"Ya existe el autor '{datos.nombre}'")
    db.refresh(autor)
    return autor


def actualizar(db: Session, autor_id: int, datos: AutorActualizar) -> Autor:
    autor = obtener(db, autor_id)
    cambios = datos.model_dump(exclude_unset=True, exclude_none=True)
    if "nombre" in cambios:
        _validar_nombre_unico(db, cambios["nombre"], excluir_id=autor_id)
    for campo, valor in cambios.items():
        setattr(autor, campo, valor)
    guardar(db, "Ya existe otro autor con esos datos")
    db.refresh(autor)
    return autor


def eliminar(db: Session, autor_id: int) -> None:
    autor = obtener(db, autor_id)
    total = db.scalar(select(func.count(Libro.id)).where(Libro.autor_id == autor_id)) or 0
    if total:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El autor tiene {total} libro(s); no se puede eliminar",
        )
    db.delete(autor)
    guardar(db, "No se puede eliminar el autor")
