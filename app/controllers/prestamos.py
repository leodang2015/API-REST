from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session, selectinload

from app.controllers.common import guardar
from app.models.libro import Libro
from app.models.prestamo import Prestamo
from app.models.socio import Socio
from app.schemas.prestamo import PrestamoActualizar, PrestamoCrear


def _consulta_base():
    return select(Prestamo).options(
        selectinload(Prestamo.socio),
        selectinload(Prestamo.libro).selectinload(Libro.autor),
        selectinload(Prestamo.libro).selectinload(Libro.categorias),
    )


def listar(db: Session) -> list[Prestamo]:
    consulta = _consulta_base().order_by(Prestamo.fecha_prestamo.desc())
    return list(db.scalars(consulta))


def obtener(db: Session, prestamo_id: int) -> Prestamo:
    prestamo = db.scalar(_consulta_base().where(Prestamo.id == prestamo_id))
    if prestamo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Préstamo no encontrado",
        )
    return prestamo


def crear(db: Session, datos: PrestamoCrear) -> Prestamo:
    socio = db.get(Socio, datos.socio_id)
    if socio is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Socio no encontrado")
    if not socio.activo:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El socio no está activo",
        )
    libro = db.get(Libro, datos.libro_id)
    if libro is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Libro no encontrado")

    resultado = db.execute(
        update(Libro)
        .where(Libro.id == datos.libro_id, Libro.disponible > 0)
        .values(disponible=Libro.disponible - 1)
    )
    if resultado.rowcount != 1:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No hay ejemplares disponibles para ese libro",
        )

    prestamo = Prestamo(
        socio_id=datos.socio_id,
        libro_id=datos.libro_id,
        fecha_limite=datos.fecha_limite,
    )
    db.add(prestamo)
    guardar(db, "No se pudo crear el préstamo")
    return obtener(db, prestamo.id)


def actualizar(db: Session, prestamo_id: int, datos: PrestamoActualizar) -> Prestamo:
    prestamo = obtener(db, prestamo_id)
    cambios = datos.model_dump(exclude_unset=True, exclude_none=True)
    fecha_devolucion = cambios.get("fecha_devolucion")
    if fecha_devolucion is not None and not prestamo.devuelto:
        prestamo.fecha_devolucion = fecha_devolucion
        prestamo.devuelto = True
        dias_tarde = (fecha_devolucion.date() - prestamo.fecha_limite.date()).days
        prestamo.multa = max(dias_tarde * 1000, 0)
        prestamo.libro.disponible += 1
    if "multa" in cambios:
        prestamo.multa = cambios["multa"]
    guardar(db, "No se pudo actualizar el préstamo")
    return obtener(db, prestamo_id)


def eliminar(db: Session, prestamo_id: int) -> None:
    prestamo = obtener(db, prestamo_id)
    if not prestamo.devuelto:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar un préstamo activo",
        )
    db.delete(prestamo)
    guardar(db, "No se puede eliminar el préstamo")
