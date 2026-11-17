from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.controllers.common import guardar
from app.models.prestamo import Prestamo
from app.models.socio import Socio
from app.schemas.socio import SocioActualizar, SocioCrear


def listar(db: Session) -> list[Socio]:
    return list(db.scalars(select(Socio).order_by(Socio.nombre)))


def obtener(db: Session, socio_id: int) -> Socio:
    socio = db.get(Socio, socio_id)
    if socio is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Socio no encontrado")
    return socio


def _validar_email_unico(db: Session, email: str, excluir_id: int | None = None) -> None:
    consulta = select(Socio.id).where(func.lower(Socio.email) == email.lower())
    if excluir_id is not None:
        consulta = consulta.where(Socio.id != excluir_id)
    if db.scalar(consulta) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un socio con el email '{email}'",
        )


def crear(db: Session, datos: SocioCrear) -> Socio:
    email = str(datos.email).lower()
    _validar_email_unico(db, email)
    socio = Socio(**datos.model_dump(exclude={"email"}), email=email)
    db.add(socio)
    guardar(db, f"Ya existe un socio con el email '{email}'")
    db.refresh(socio)
    return socio


def actualizar(db: Session, socio_id: int, datos: SocioActualizar) -> Socio:
    socio = obtener(db, socio_id)
    cambios = datos.model_dump(exclude_unset=True, exclude_none=True)
    if "email" in cambios:
        cambios["email"] = str(cambios["email"]).lower()
        _validar_email_unico(db, cambios["email"], excluir_id=socio_id)
    for campo, valor in cambios.items():
        setattr(socio, campo, valor)
    guardar(db, "Ya existe otro socio con ese correo")
    db.refresh(socio)
    return socio


def eliminar(db: Session, socio_id: int) -> None:
    socio = obtener(db, socio_id)
    total = db.scalar(
        select(func.count(Prestamo.id)).where(Prestamo.socio_id == socio_id)
    ) or 0
    if total:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El socio tiene {total} préstamo(s); no se puede eliminar",
        )
    db.delete(socio)
    guardar(db, "No se puede eliminar el socio")
