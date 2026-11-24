from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.controllers.common import guardar
from app.core.exceptions import Prohibido
from app.models.libro import Libro
from app.models.socio import Socio
from app.models.solicitud_prestamo import SolicitudPrestamo
from app.schemas.solicitud_prestamo import SolicitudCrear, SolicitudResolver


def _consulta_base():
    return select(SolicitudPrestamo).options(
        selectinload(SolicitudPrestamo.socio),
        selectinload(SolicitudPrestamo.libro).selectinload(Libro.autor),
        selectinload(SolicitudPrestamo.libro).selectinload(Libro.categorias),
    )


def listar(db: Session, user_id: int | None = None) -> list[SolicitudPrestamo]:
    consulta = _consulta_base().order_by(SolicitudPrestamo.fecha_solicitud.desc())
    if user_id is not None:
        consulta = consulta.join(Socio).where(Socio.usuario_id == user_id)
    return list(db.scalars(consulta))


def obtener(db: Session, solicitud_id: int) -> SolicitudPrestamo:
    solicitud = db.scalar(_consulta_base().where(SolicitudPrestamo.id == solicitud_id))
    if solicitud is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitud no encontrada",
        )
    return solicitud


def crear(db: Session, user_id: int, datos: SolicitudCrear) -> SolicitudPrestamo:
    socio = db.scalar(select(Socio).where(Socio.usuario_id == user_id))
    if socio is None or not socio.activo:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La cuenta no tiene un socio activo asociado",
        )

    libro = db.get(Libro, datos.libro_id)
    if libro is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Libro no encontrado")

    solicitud_pendiente = db.scalar(
        select(SolicitudPrestamo.id).where(
            SolicitudPrestamo.socio_id == socio.id,
            SolicitudPrestamo.libro_id == libro.id,
            SolicitudPrestamo.estado == "pendiente",
        )
    )
    if solicitud_pendiente is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya tienes una solicitud pendiente para este libro",
        )

    solicitud = SolicitudPrestamo(socio_id=socio.id, libro_id=libro.id)
    db.add(solicitud)
    db.flush()
    guardar(db, "No se pudo registrar la solicitud")
    return obtener(db, solicitud.id)


def resolver(
    db: Session,
    solicitud_id: int,
    datos: SolicitudResolver,
) -> SolicitudPrestamo:
    solicitud = obtener(db, solicitud_id)
    if solicitud.estado != "pendiente":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La solicitud ya fue resuelta",
        )
    solicitud.estado = datos.estado
    solicitud.fecha_entrega_estimada = datos.fecha_entrega_estimada
    guardar(db, "No se pudo resolver la solicitud")
    return obtener(db, solicitud_id)


def eliminar(db: Session, solicitud_id: int) -> None:
    solicitud = obtener(db, solicitud_id)
    db.delete(solicitud)
    guardar(db, "No se pudo eliminar la solicitud")


def cancelar_cliente(db: Session, solicitud_id: int, user_id: int) -> None:
    solicitud = obtener(db, solicitud_id)
    if solicitud.socio.usuario_id != user_id:
        raise Prohibido()
    if solicitud.estado != "pendiente":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Solo puedes cancelar solicitudes pendientes",
        )
    eliminar(db, solicitud_id)
